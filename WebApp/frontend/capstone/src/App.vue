<template>
  <app-bar />
</template>

<script setup>
import { RouterView } from 'vue-router'
import AppBar from '@/layouts/default/AppBar.vue'

// Register the AppBar component
const components = {
  AppBar
}
</script>
