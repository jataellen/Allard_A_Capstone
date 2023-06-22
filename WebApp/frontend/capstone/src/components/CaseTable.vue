<template>
  <v-container class="container">
    <div class="table-wrapper">
      <v-card-title class="title-wrapper">
        <div class="title">
          Ontario Landlord and Tenant Board Cases
        </div>
        <div class="search">
          <v-text-field
            v-model="search"
            append-icon="mdi-magnify"
            label="Search"
            single-line
            hide-details
          ></v-text-field>
        </div>
      </v-card-title>

      <v-data-table
        :headers="headers"
        :items="cases"
        class="elevation-1 custom-table"
        :search="search"
      >
      <template v-slot:item.raw_file_name="{ item }">
        <div v-if="item.columns.raw_file_name">
          {{ item.columns.raw_file_name }}
        </div>
        <div v-else>
          —
        </div>
      </template>

      <template v-slot:item.year="{ item }">
        <div v-if="item.columns.year">
          {{ item.columns.year }}
        </div>
        <div v-else>
          —
        </div>
      </template>

      <template v-slot:item.url="{ item }">
        <div v-if="item.columns.url">
          <a :href="item.columns.url" class="url-link" target="_blank">
            {{ item.columns.url }}
          </a>
        </div>
        <div v-else>
          —
        </div>
      </template>

      <template v-slot:item.adjudicating_member="{ item }">
        <div v-if="item.columns.adjudicating_member">
          {{ item.columns.adjudicating_member }}
        </div>
        <div v-else>
          —
        </div>
      </template>

      <template v-slot:item.approved="{ item }">
  <v-icon :color="item.columns.approved === '1' ? 'green' : 'red'">
    {{ item.columns.approved === '1' ? 'mdi-check' : 'mdi-close' }}
  </v-icon>
</template>





      <template v-slot:item.action="{ item }">
        <div class="action-buttons">
          <router-link :to="`/viewCase/${item.raw.id}`" class="btn view-button">
            View
          </router-link>
          <router-link :to="`/editCase/${item.raw.id}`" class="btn edit-button">
            Edit
          </router-link>
        </div>
      </template>


    
      </v-data-table>
    </div>
  </v-container>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      search: '',
      headers: [
        {
          title: 'File Number',
          align: 'start',
          sortable: false,
          key: 'file_number',
        },
        { title: 'Year', key: 'year' },
        { title: 'URL', key: 'url' },
        { title: 'Adjudicating Member', key: 'adjudicating_member' },
        { title: 'Verified', key: 'approved' },
        { title: 'Action', key: 'action' },
      ],
      cases: [],
    };
  },
  mounted() {
    this.getCases();
  },
  methods: {
    getCases() {
      axios
        .get('http://localhost:8000/api/')
        .then(response => {
          this.cases = response.data;
        })
        .catch(error => {
          console.error(error);
        });
    },
  },
};
</script>

<style scoped>
.container {
  padding: 50px 0px 50px 0px;
}

.table-wrapper {
  overflow-x: auto;
}

.custom-table {
  min-width: 400px;
  width: 100%;
}

.url-link {
  color: #0099cc;
}

.action-buttons {
  display: flex;
  flex-direction: row;
  gap: 10px; /* Adjust the gap between buttons as needed */
}

.title-wrapper {
  display: flex;
  align-items: center;
}

.title {
  margin-right: auto;
}

.search {
  min-width: 300px;
}

.btn {
  display: inline-block;
  padding: 0.2em 0.5em; /* Adjust the padding here */
  font-size: 0.9rem; /* Adjust the font-size here */
  text-decoration: none;
  border-radius: 4px;
  text-align: center;
  transition: background-color 0.2s;
  color: #fff;
}

.view-button {
  background-color: #44c767; /* green */
}

.edit-button {
  background-color: #0099cc; /* blue */
}

.btn:hover {
  opacity: 0.7;
}
</style>