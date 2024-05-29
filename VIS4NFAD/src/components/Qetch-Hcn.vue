<template>
    <div class="container">
      <el-card class="dataset-card"><HcnData/></el-card>
      <div class="main-content">
        <div class="query-section">
          <el-card><SketchHcn/></el-card>
        </div>
        <div class="result-section">
          <el-card>Result</el-card>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  import HcnData from './Hcn-Data.vue'
  import SketchHcn from './Sketch-Hcn.vue'
  import ResultHcn from './Result-Hcn.vue'
  </script>
  
  <style scoped>
  .container {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  
  .main-content {
    display: flex;
    flex-direction: row;
    gap: 10px;
  }
  
  .dataset-card {
    flex: 0 0 auto;
  }
  
  .query-section {
    flex: 2;
  }
  
  .result-section {
    flex: 3;
  }
  </style>
  