<template>
  <v-list
    two-line
    subheader
  >
    <v-list-item
      v-for="item in items"
      :key="item._id"
      selectable
      :to="{ name: 'dandiset-metadata-viewer', params: { id: item._id } }"
    >
      <v-row
        no-gutters
        align="center"
      >
        <v-col cols="12">
          <v-list-item-content>
            <v-list-item-title>
              <template v-if="item.meta.dandiset.version">
                <v-chip
                  v-if="item.meta.dandiset.version === 'draft'"
                  small
                  color="amber lighten-3"
                  text-color="amber darken-4"
                >
                  <b>DRAFT</b>
                </v-chip>
                <v-chip
                  v-else
                  small
                  color="light-blue lighten-4"
                  text-color="light-blue darken-3"
                >
                  <b>{{ item.meta.dandiset.version }}</b>
                </v-chip>
              </template>
              {{ item.meta.dandiset.name }}
            </v-list-item-title>
            <v-list-item-subtitle>
              Contact <b>{{ getDandisetContact(item) }}</b>
              ·
              Created on <b>{{ formatDate(item.created) }}</b>
              ·
              DANDI:<b>{{item.meta.dandiset.identifier}}</b>
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-col>
        <!-- TODO: Uncomment this once backend detail issue is sorted -->
        <!-- <v-col cols="1">
          <v-icon color="primary">
            mdi-file
          </v-icon>
          {{ item.details.nItems }}
        </v-col>
        <v-col cols="1">
          <v-icon color="primary">
            mdi-server
          </v-icon>
          {{ filesize(item.size) }}
        </v-col> -->
      </v-row>
    </v-list-item>
  </v-list>
</template>

<script>
import moment from 'moment';
import filesize from 'filesize';

import { getDandisetContact } from '@/utils';

export default {
  props: {
    dandisets: {
      // Girder Items
      type: Array,
      required: true,
    },
    // TODO: Uncomment this once backend detail issue is sorted
    // dandisetDetails: {
    //   // nFolders and nItems
    //   type: Array,
    //   required: true,
    // },
  },
  computed: {
    items() {
      // TODO: Uncomment this once backend detail issue is sorted
      // return this.dandisets.map((item, i) => ({ ...item, details: this.dandisetDetails[i] }));
      return this.dandisets;
    },
  },
  methods: {
    filesize,
    getDandisetContact,
    formatDate(date) {
      return moment(date).format('LL');
    },
  },
};
</script>