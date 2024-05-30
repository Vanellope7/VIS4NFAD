<template>
  <div class="container">
    <div class="dataset-section">
      <el-card>
        <div>
        <HcnData/>
      </div>
      </el-card>
      <el-card>
        <SketchHcn />
      </el-card>
    </div>
    <div class="result-content">
      <el-card>
        <ResultHcn />
      </el-card>
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

.dataset-card {
  flex: 0 0 auto;
  margin-right: 10px;
}

.dataset-section {
  display: flex;
  flex-direction: row;
  gap: 10px;
  align-items: center;
  justify-content: center;
}
</style>