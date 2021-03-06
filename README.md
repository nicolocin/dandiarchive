# dandiarchive [![CircleCI](https://circleci.com/gh/dandi/dandiarchive/tree/master.svg?style=svg)](https://circleci.com/gh/dandi/dandiarchive/tree/master)
Infrastructure and code for the DANDI Archive.

Folders in this repo:

- `ansible`: Ansible code for deploying `girder-dandi-archive`.
- `docker`: Docker files for building and deploying the application in Docker.
- `girder-dandi-archive`: A Girder plugin which adds the custom endpoints for the DANDI Archive.
- `test`: End-to-end tests for the entire application.
- `web`: The web application front-end, based on Vue.js.

## Developing Locally

### Server

#### Install
1. Ensure MongoDB is running locally.

2. Create a python3 virtual environment:
    ```bash
    mkvirtualenv dandiarchive --python=python3
    ```

3. Install (in editable mode) the DANDI Archive plugin to Girder:
    ```bash
    cd girder-dandi-archive
    pip install -e .
    girder build
    ```

#### Run
```bash
girder serve
```

The Girder server will run at `http://localhost:8080/`.

##### Initial Bootstrapping

1. Create an admin user, using Girder's web client:
    * Visit `http://localhost:8080/#?dialog=register`.
    * The first user created automatically becomes the admin user.

2. Create a filesystem assetstore:
    * Visit `http://localhost:8080/#assetstores`.

#### Test
```bash
# within "girder-dandi-archive"
pip install -r requirements-dev.txt
tox
```

### Web App

#### Install
```bash
cd web
yarn install
```

#### Run
Ensure the server is running locally (see above), then:
```bash
# within "web"
yarn run serve
```

The web app will be served at `http://localhost:8085/`.

#### Test
```bash
# within "web"
yarn run lint
```

#### End-to-End Testing
See `test/README.md` for end-to-end testing instructions.

## Docker

Currently there is a docker-compose file which gets the necessary infrastructure up and running for dandiarchive.

In order to get up and running:

```
cd docker
docker-compose build
docker-compose up
```

This will spin up 4 containers:

1) MongoDB
2) Girder
3) Vue Web Client
4) Provision

Provision container creates a Girder admin user, creates a filesystem assetstore and set necessary CORS settings.
Credentials are username: admin, password: letmein.

When the provision container finishes, it will exit. The other three containers will remain running.

After docker-compose up succeeds and the provision container finishes, you should have:

1) Girder up and running on port 8091
2) Web client up and running on port 8092
3) MongoDB container up and running, and only visible to the other docker containers
