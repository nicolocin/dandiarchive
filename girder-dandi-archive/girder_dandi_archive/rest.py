import re
from urllib.parse import urljoin

import requests
from requests.exceptions import ConnectionError, HTTPError

from girder.api import access
from girder.api.describe import autoDescribeRoute, describeRoute, Description
from girder.api.rest import Resource
from girder.constants import AccessType, TokenScope
from girder.exceptions import RestException, ValidationException
from girder.models.collection import Collection
from girder.models.folder import Folder
from girder.models.setting import Setting
from girder.models.user import User

from .settings import PUBLISH_API_KEY, PUBLISH_API_URL
from .util import (
    dandiset_find,
    dandiset_identifier,
    DANDISET_IDENTIFIER_COUNTER,
    DANDISET_IDENTIFIER_LENGTH,
    find_dandiset_by_identifier,
    get_dandiset_owners,
    get_or_create_drafts_collection,
    validate_user,
)


class DandiResource(Resource):
    def __init__(self):
        super(DandiResource, self).__init__()

        self.resourceName = "dandi"
        self.route("GET", (":identifier",), self.get_dandiset)
        self.route("GET", (":identifier", "stats"), self.get_dandiset_stats)
        self.route("GET", (":identifier", "owners"), self.get_dandiset_owners)
        self.route("PUT", (":identifier", "owners"), self.set_dandiset_owners)
        self.route("GET", ("user",), self.get_user_dandisets)
        self.route("GET", ("search",), self.search_dandisets)
        self.route("GET", (), self.list_dandisets)
        self.route("POST", (), self.create_dandiset)
        self.route("POST", (":identifier",), self.publish_dandiset)
        self.route("GET", ("stats",), self.stats)

    @access.user(scope=TokenScope.DATA_WRITE)
    @describeRoute(
        Description("Create Dandiset")
        .param("name", "Name of the Dandiset")
        .param("description", "Description of the Dandiset")
    )
    def create_dandiset(self, params):
        if "name" not in params or "description" not in params:
            raise RestException("Name and description required.")

        name, description = params["name"], params["description"]

        if not name or not description:
            raise RestException("Name and description must not be empty.")

        new_identifier_count = Setting().collection.find_one_and_update(
            {"key": DANDISET_IDENTIFIER_COUNTER},
            {"$inc": {"value": 1}},
            projection={"value": True},
        )["value"]
        padded_identifier = f"{new_identifier_count:0{DANDISET_IDENTIFIER_LENGTH}d}"

        meta = {
            "name": name,
            "description": description,
            "identifier": padded_identifier,
        }

        drafts = get_or_create_drafts_collection()
        folder = Folder().createFolder(
            drafts, padded_identifier, parentType="collection", creator=self.getCurrentUser(),
        )
        folder = Folder().setMetadata(folder, {"dandiset": meta})
        return folder

    @access.public
    @describeRoute(
        Description("Get Dandiset").param("identifier", "Dandiset Identifier", paramType="path")
    )
    @dandiset_identifier
    def get_dandiset(self, identifier, params):
        doc = find_dandiset_by_identifier(identifier)
        if not doc:
            raise RestException("No such dandiset found.")
        return doc

    @access.public
    @describeRoute(
        Description("Get Dandiset Stats").param(
            "identifier", "Dandiset Identifier", paramType="path"
        )
    )
    @dandiset_identifier
    def get_dandiset_stats(self, identifier, params):
        doc = find_dandiset_by_identifier(identifier)
        if not doc:
            raise RestException("No such dandiset found.")

        size = Folder().getSizeRecursive(doc)

        # Subtract one from subtreeCount to exclude the root folder
        subtree_count = Folder().subtreeCount(doc) - 1
        num_folders = Folder().subtreeCount(doc, includeItems=False) - 1
        num_items = subtree_count - num_folders

        return {
            "bytes": size,
            "items": num_items,
            "folders": num_folders,
        }

    @access.public
    @describeRoute(
        Description("Get Dandiset Owners").param(
            "identifier", "Dandiset Identifier", paramType="path"
        )
    )
    @dandiset_identifier
    def get_dandiset_owners(self, identifier, params):
        return get_dandiset_owners(find_dandiset_by_identifier(identifier))

    @access.user
    @autoDescribeRoute(
        Description("Set Dandiset Owners")
        .param("identifier", "Dandiset Identifier", paramType="path")
        .jsonParam(
            "owners",
            "A JSON list of girder users to set as the owners.",
            paramType="body",
            requireArray=True,
        )
    )
    @dandiset_identifier
    def set_dandiset_owners(self, identifier, owners, params):
        dandiset = find_dandiset_by_identifier(identifier)
        Folder().requireAccess(dandiset, user=self.getCurrentUser(), level=AccessType.ADMIN)

        users = {}
        for owner in owners:
            if owner["_id"] in users:
                continue

            if not validate_user(owner):
                raise ValidationException("All owners must be valid user objects.")

            users[owner["_id"]] = {"id": owner["_id"], "level": AccessType.ADMIN}

        # Assumes there is at least one admin
        admin = next(User().getAdmins())
        doc = Folder().setAccessList(
            dandiset, {"users": list(users.values())}, save=True, recurse=True, user=admin
        )
        return get_dandiset_owners(doc)

    @access.user
    @autoDescribeRoute(
        Description("Get User Dandisets").pagingParams(defaultSort="meta.dandiset.identifier")
    )
    def get_user_dandisets(self, limit, offset, sort):
        user_id = self.getCurrentUser()["_id"]
        return dandiset_find({"creatorId": user_id}, limit=limit, offset=offset, sort=sort)

    @access.public
    @autoDescribeRoute(
        Description("List Dandisets").pagingParams(defaultSort="meta.dandiset.identifier")
    )
    def list_dandisets(self, limit, offset, sort):
        return dandiset_find({}, limit=limit, offset=offset, sort=sort)

    @access.public
    @autoDescribeRoute(
        Description("Search Dandisets")
        .param("search", "Search Query", paramType="query")
        .pagingParams(defaultSort="meta.dandiset.identifier")
    )
    def search_dandisets(self, search, limit, offset, sort):
        if not search:
            # Empty search string should return all possible results
            return dandiset_find({}, limit=limit, offset=offset, sort=sort)

        return dandiset_find(
            {
                "$or": [
                    {
                        "meta.dandiset.identifier": {
                            "$regex": re.compile(re.escape(search), re.IGNORECASE)
                        }
                    },
                    {
                        "meta.dandiset.name": {
                            "$regex": re.compile(re.escape(search), re.IGNORECASE)
                        }
                    },
                    {
                        "meta.dandiset.description": {
                            "$regex": re.compile(re.escape(search), re.IGNORECASE)
                        }
                    },
                    {
                        "meta.dandiset.contributors.name": {
                            "$regex": re.compile(re.escape(search), re.IGNORECASE)
                        }
                    },
                ],
            },
            limit=limit,
            offset=offset,
            sort=sort,
        )

    # TODO this is restricted to site admins for now
    @access.admin
    # @access.user
    @describeRoute(
        Description("Publish Dandiset").param("identifier", "Dandiset Identifier", paramType="path")
    )
    @dandiset_identifier
    def publish_dandiset(self, identifier, params):
        dandiset_folder = find_dandiset_by_identifier(identifier)
        Folder().requireAccess(dandiset_folder, user=self.getCurrentUser(), level=AccessType.ADMIN),

        publish_api_url = Setting().get(PUBLISH_API_URL)
        publish_api_key = Setting().get(PUBLISH_API_KEY)

        try:
            response = requests.post(
                urljoin(publish_api_url, f"dandisets/{identifier}/versions/publish/"),
                headers={"Authorization": f"Token {publish_api_key}"},
            )
            response.raise_for_status()
        except HTTPError:
            raise RestException(message="Failed to publish")
        except ConnectionError:
            raise RestException(message="Failed to contact publish API")

    @access.public
    @describeRoute(Description("Global Dandiset Statistics"))
    def stats(self, params):
        drafts = get_or_create_drafts_collection()
        draft_count = Collection().countFolders(drafts)

        # TODO no way to publish
        published_count = 0

        user_count = User().collection.count_documents({})

        # These aggregate queries are not indexable.
        # Here are some benchmarks I generated for this endpoint as is:
        #    0 dandisets  |  0.008207440376281738 seconds
        # 1000 dandisets  |  0.019745850563049318 seconds
        # 2000 dandisets  |  0.030080437660217285 seconds
        # 1000 more dandisets takes about .011 more seconds
        # Here is the same benchmark but with these aggregate queries removed:
        #    0 dandisets  |  0.004081225395202637
        # 1000 dandisets  |  0.008220505714416505
        # 2000 dandisets  |  0.011307811737060547
        # 1000 more dandisets takes about 0.0035 more seconds

        species_count = list(
            Folder().collection.aggregate(
                [
                    {"$unwind": "$meta.dandiset.organism"},
                    {"$group": {"_id": "$meta.dandiset.organism.species"}},
                    {"$group": {"_id": "0", "count": {"$sum": 1}}},
                ]
            )
        )
        if species_count:
            species_count = species_count[0]["count"]
        else:
            species_count = 0

        subject_count = list(
            Folder().collection.aggregate(
                [{"$group": {"_id": "0", "count": {"$sum": "$meta.dandiset.number_of_subjects"}}}]
            )
        )
        if subject_count:
            subject_count = subject_count[0]["count"]
        else:
            subject_count = 0

        cell_count = list(
            Folder().collection.aggregate(
                [{"$group": {"_id": "0", "count": {"$sum": "$meta.dandiset.number_of_cells"}}}]
            )
        )
        if cell_count:
            cell_count = cell_count[0]["count"]
        else:
            cell_count = 0

        return {
            "draft_count": draft_count,
            "published_count": published_count,
            "user_count": user_count,
            "species_count": species_count,
            "subject_count": subject_count,
            "cell_count": cell_count,
            "size": drafts["size"],
        }
