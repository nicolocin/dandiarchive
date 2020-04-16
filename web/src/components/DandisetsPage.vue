<template>
  <div>
    <v-toolbar
      color="grey darken-2 white--text"
    >
      <v-toolbar-title class="d-none d-md-block mx-8">
        {{ title }}
      </v-toolbar-title>
      <v-divider
        class="d-none d-md-block"
        vertical
      />
      <div class="mx-6">
        Sort By:
      </div>
      <v-chip-group
        :value="sortOption"
        active-class="white light-blue--text"
        dark
        mandatory
      >
        <v-chip
          v-for="(option, i) in sortingOptions"
          :key="option.name"
          @click="changeSort(i)"
        >
          {{ option.name }}
          <v-icon right>
            <template v-if="sortDir === 1 || sortOption !== i">
              mdi-sort-ascending
            </template>
            <template v-else>
              mdi-sort-descending
            </template>
          </v-icon>
        </v-chip>
      </v-chip-group>
      <SearchField />
    </v-toolbar>
    <DandisetList
      class="
        mx-12
        my-12"
      :dandisets="dandisets"
    />
    <v-pagination
      v-model="page"
      :length="pages"
    />
  </div>
</template>

<script>
import DandisetList from '@/components/DandisetList.vue';
import SearchField from '@/views/PublicDandisetsView/SearchField.vue';
import girderRest from '@/rest';

const DANDISETS_PER_PAGE = 8;

const sortingOptions = [
  {
    name: 'Created',
    field: 'created',
  },
  {
    name: 'Name',
    field: 'meta.dandiset.name',
  },
];

export default {
  name: 'DandisetsPage',
  components: { DandisetList, SearchField },
  props: {
    title: {
      type: String,
      required: true,
    },
    user: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  data() {
    return {
      sortingOptions,
      sortOption: Number(this.$route.query.sortOption) || 0,
      sortDir: this.$route.query.sortDir || 1,
      page: Number(this.$route.query.page) || 1,
    };
  },
  computed: {
    listingUrl() {
      return this.user ? 'dandi/user' : 'dandi';
    },
    pages() {
      return Math.ceil(this.totalDandisets / DANDISETS_PER_PAGE) || 1;
    },
    sortField() {
      return this.sortingOptions[this.sortOption].field;
    },
    queryParams() {
      const {
        page, sortOption, sortDir,
      } = this;

      return {
        page,
        sortOption,
        sortDir,
      };
    },
    dandisets() {
      return this.dandisetRequest ? this.dandisetRequest.data : [];
    },
    totalDandisets() {
      return this.dandisetRequest ? this.dandisetRequest.headers['girder-total-count'] : 0;
    },
  },
  asyncComputed: {
    async dandisetRequest() {
      const {
        listingUrl, page, sortField, sortDir,
      } = this;

      const {
        data, headers, status, statusText,
      } = await girderRest.get(listingUrl, {
        params: {
          limit: DANDISETS_PER_PAGE,
          offset: (page - 1) * DANDISETS_PER_PAGE,
          sort: sortField,
          sortdir: sortDir,
        },
      });

      return {
        data,
        headers,
        status,
        statusText,
      };
    },
  },
  watch: {
    queryParams(query) {
      this.$router.replace({
        ...this.$route,
        query,
      });
    },
  },
  methods: {
    changeSort(index) {
      if (this.sortOption === index) {
        this.sortDir *= -1;
      } else {
        this.sortOption = index;
        this.sortDir = 1;
      }

      this.page = 1;
    },
  },
};
</script>