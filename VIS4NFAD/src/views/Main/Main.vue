<template>
  <div class="Main">
    <Overview/>
    <Analysis/>
  </div>
</template>

<script setup>
import Overview from './Part/Overview.vue'
import Analysis from './Part/Analysis.vue'
</script>

<style scoped>
  .Main {
      width: 100vw;
      height: 100vh;
  }
</style>