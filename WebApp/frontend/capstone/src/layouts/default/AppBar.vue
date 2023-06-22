

<template>
  
  <v-app>
    <v-navigation-drawer v-model="sidebar" app>
      <v-list>
        <v-list-tile
          v-for="item in menuItems"
          :key="item.title"
          :to="item.path">
          <v-list-tile-action>
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-tile-action>
          <v-list-tile-content>{{ item.title }}</v-list-tile-content>
        </v-list-tile>
      </v-list>
    </v-navigation-drawer>

    <v-toolbar app class="navbar-container">
      <span class="hidden-sm-and-up">
        <v-toolbar-side-icon @click="sidebar = !sidebar">
        </v-toolbar-side-icon>
      </span>
      <v-toolbar-title>
        <router-link to="/" tag="span" class="app-title"><v-icon icon="mdi-gavel" style="padding:0px 10px 0px 0px"/>{{ appTitle }}</router-link>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-toolbar-items class="hidden-xs-only">
        <v-btn
          flat
          v-for="item in menuItems"
          :key="item.title"
          :to="item.path">
          <v-icon left dark>{{ item.icon }}</v-icon>
          {{ item.title }}
        </v-btn>
      </v-toolbar-items>
    </v-toolbar>
    
    <v-content>
      <router-view></router-view>
    </v-content>
    
  </v-app>

</template>

<script>
//import HelloWorld from "./components/HelloWorld";

export default {
  name: "App",
  data(){
    return {
      appTitle: 'Case Data',
      menuItems: [
          { title: 'All Cases', path: '/', icon: 'mdi-home' },
          { title: 'Request Access', path: '/signup', icon: 'mdi-account' },
          { title: 'Sign In', path: '/signin', icon: 'mdi-lock-open' }
     ]
    }
  },
};
</script>

<style scoped>

.navbar-container {
  background-color: #0099cc;
  color: white;
}


.app-title {
  color: white;
  cursor: pointer;
  text-decoration: none;
  text-transform: uppercase;
  padding-left: 8px;
  font-weight: 500;
}
</style>
