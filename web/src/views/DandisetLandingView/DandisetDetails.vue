<template>
  <v-card
    v-if="currentDandiset"
    height="100%"
    class="px-3 py-1"
  >
    <template>
      <v-row
        v-if="contactName"
        no-gutters
        :class="rowClasses"
      >
        <v-icon>mdi-account</v-icon>
        <span :class="labelClasses">Contact</span>
        <span :class="itemClasses">{{ contactName }}</span>
      </v-row>
      <v-row
        no-gutters
        :class="rowClasses"
      >
        <v-icon>mdi-calendar</v-icon>
        <span :class="labelClasses">Created on</span>
        <span :class="itemClasses">{{ created }}</span>
      </v-row>
      <v-row
        no-gutters
        :class="rowClasses"
      >
        <v-icon>mdi-update</v-icon>
        <span :class="labelClasses">Last updated</span>
        <span :class="itemClasses">{{ lastUpdated }}</span>
      </v-row>

      <v-divider class="my-2" />

      <v-row :class="`${rowClasses} px-2`">
        <span :class="labelClasses">Identifier</span>
        <span :class="itemClasses">{{ currentDandiset.meta.dandiset.identifier }}</span>
      </v-row>
      <template v-if="stats">
        <v-row :class="`${rowClasses} px-2`">
          <v-col
            cols="auto"
            class="text--secondary mx-2 pa-0 py-1"
          >
            <v-icon color="primary">
              mdi-file
            </v-icon>
            {{ stats.items }}
          </v-col>
          <v-col
            class="text--secondary mx-2 pa-0 py-1"
            cols="auto"
          >
            <v-icon color="primary">
              mdi-folder
            </v-icon>
            {{ stats.folders }}
          </v-col>
          <v-col
            class="text--secondary mx-2 pa-0 py-1"
            cols="auto"
          >
            <v-icon color="primary">
              mdi-server
            </v-icon>
            {{ formattedSize }}
          </v-col>
        </v-row>
      </template>

      <v-divider class="my-2 px-0 mx-0" />

      <v-row>
        <v-col>
          <v-card
            color="grey lighten-3"
            class="mx-2"
            flat
            tile
          >
            <v-row
              no-gutters
              class="py-2"
            >
              <v-col cols="11">
                <v-icon
                  class="mx-2"
                  color="primary"
                >
                  mdi-link
                </v-icon>
                <span :class="itemClasses">Draft</span>
              </v-col>
              <v-col>
                <v-tooltip top>
                  <template v-slot:activator="{ on }">
                    <v-icon
                      small
                      color="grey darken-1"
                      v-on="on"
                    >
                      mdi-help-circle
                    </v-icon>
                  </template>
                  <span>This is a version of your dandiset that contains unpublished changes.</span>
                </v-tooltip>
              </v-col>
            </v-row>
          </v-card>
        </v-col>
      </v-row>

      <v-divider class="my-2 px-0 mx-0" />

      <v-row
        no-gutters
        :class="rowClasses"
      >
        <v-col>
          <span :class="labelClasses">Ownership</span>
        </v-col>
        <v-col cols="auto">
          <v-dialog
            v-model="ownerDialog"
            width="50%"
          >
            <template v-slot:activator="{ on }">
              <v-tooltip
                :disabled="!manageOwnersDisabled"
                left
              >
                <template
                  v-slot:activator="{ on: tooltipOn }"
                >
                  <div v-on="tooltipOn">
                    <v-btn
                      color="primary"
                      x-small
                      text
                      :disabled="manageOwnersDisabled"
                      v-on="on"
                    >
                      <v-icon
                        x-small
                        class="pr-1"
                      >
                        mdi-lock
                      </v-icon>
                      Manage
                    </v-btn>
                  </div>
                </template>
                <template v-if="loggedIn">
                  You must be an owner to manage ownership.
                </template>
                <template v-else>
                  You must be logged in to manage ownership.
                </template>
              </v-tooltip>
            </template>
            <DandisetOwnersDialog
              :key="ownerDialogKey"
              :owners="owners"
              @close="ownerDialog = false"
            />
          </v-dialog>
        </v-col>
      </v-row>
      <!-- TODO: Make chips wrap, instead of pushing whole card wide -->
      <v-row :class="rowClasses">
        <v-col cols="12">
          <v-chip
            v-for="owner in limitedOwners"
            :key="owner.id"
            color="light-blue lighten-4"
            text-color="light-blue darken-3"
            class="font-weight-medium ma-1"
          >
            {{ owner.login }}
          </v-chip>
          <span
            v-if="numExtraOwners"
            class="ml-1 text--secondary"
          >
            +{{ numExtraOwners }} more...
          </span>
        </v-col>
      </v-row>
      <!-- TODO: Uncomment this once the versions API is accessible -->
      <!-- <v-row>
        <v-col class="pa-0">
          <v-card
            color="grey lighten-2"
            tile
            flat
          >
            <div class="py-1 px-3">
              Versions
            </div>
          </v-card>
        </v-col>
      </v-row>

      <v-row>
        <v-timeline>
          <v-timeline-item
            small
            right
          >
            <template v-slot:opposite>
              <span class="caption text--secondary">
                02/26/19
              </span>
            </template>

            <span class="font-weight-medium">
              1.2.1
            </span>
          </v-timeline-item>
        </v-timeline>
      </v-row> -->
    </template>
  </v-card>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import girderRest, { loggedIn, user } from '@/rest';
import moment from 'moment';
import filesize from 'filesize';


import DandisetOwnersDialog from './DandisetOwnersDialog.vue';


export default {
  name: 'DandisetDetails',
  components: {
    DandisetOwnersDialog,
  },
  data() {
    return {
      rowClasses: 'my-1',
      labelClasses: 'mx-2 text--secondary',
      itemClasses: 'font-weight-medium',
      ownerDialog: false,
      ownerDialogKey: 0,
    };
  },
  computed: {
    user,
    loggedIn,
    created() {
      return this.formatDateTime(this.currentDandiset.created);
    },
    lastUpdated() {
      return this.formatDateTime(this.currentDandiset.updated);
    },
    contactName() {
      if (!this.currentDandiset || !this.currentDandiset.meta.dandiset.contributors) {
        return null;
      }

      const contacts = this.currentDandiset.meta.dandiset.contributors.filter(
        (contributor) => contributor.roles.includes('ContactPerson'),
      );

      if (contacts.length > 0) {
        return contacts[0].name;
      }

      return null;
    },
    manageOwnersDisabled() {
      if (!this.loggedIn || !this.owners) return true;
      return !this.owners.find((owner) => owner.id === this.user._id);
    },
    limitedOwners() {
      if (!this.owners) return [];
      return this.owners.slice(0, 5);
    },
    numExtraOwners() {
      if (!this.owners) return 0;
      return this.owners.length - this.limitedOwners.length;
    },
    formattedSize() {
      const { stats } = this;
      if (!stats) {
        return undefined;
      }
      return filesize(stats.bytes);
    },
    ...mapState('girder', {
      currentDandiset: (state) => state.currentDandiset,
      owners: (state) => state.currentDandisetOwners,
    }),
  },
  watch: {
    currentDandiset: {
      immediate: true,
      async handler(val) {
        const { identifier } = val.meta.dandiset;
        this.fetchDandisetOwners(identifier);
      },
    },
    ownerDialog() {
      // This is incremented to force re-render of the owner dialog
      this.ownerDialogKey += 1;
    },
  },
  asyncComputed: {
    async stats() {
      const { identifier } = this.currentDandiset.meta.dandiset;
      const { data } = await girderRest.get(`/dandi/${identifier}/stats`);
      return data;
    },
  },
  methods: {
    formatDateTime(datetimeStr) {
      const datetime = moment(datetimeStr);
      const date = datetime.format('LL');
      const time = datetime.format('hh:mm A');

      return `${date} at ${time}`;
    },
    ...mapActions('girder', ['fetchDandisetOwners']),
  },
};
</script>
