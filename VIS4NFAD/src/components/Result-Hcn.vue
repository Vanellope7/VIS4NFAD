<template>
  <div class="table-container">
    <el-table :data="sortedTableData" style="width: 100%" height="320" @sort-change="handleSortChange">
      <!-- Index column -->
      <el-table-column label="#" width="50">
        <template #default="scope">
          {{ scope.$index + 1 }}
        </template>
      </el-table-column>
      <!-- Table columns here -->
      <el-table-column prop="Hcn" label="Hcn" sortable="custom">
        <template #default="scope">
          {{ scope.row.Hcn }}
        </template>
      </el-table-column>
      <el-table-column prop="Smooth" label="Smooth" width="200" sortable="custom">
        <template #default="scope">
          <span>{{ parseFloat(scope.row.Smooth).toFixed(4) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="CombinedSimilarity" label="Combined Similarity" sortable="custom">
        <template #default="scope">
          <span>{{ parseFloat(scope.row.CombinedSimilarity).toFixed(4) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="CosineSimilarity" label="Cosine Similarity" sortable="custom">
        <template #default="scope">
          <span>{{ parseFloat(scope.row.CosineSimilarity).toFixed(4) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="EuclideanDistance" label="Euclidean Distance" sortable="custom">
        <template #default="scope">
          <span>{{ parseFloat(scope.row.EuclideanDistance).toFixed(4) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="SlopeSimilarity" label="Slope Similarity" sortable="custom">
        <template #default="scope">
          <span>{{ parseFloat(scope.row.SlopeSimilarity).toFixed(4) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="Slope" label="Slope" sortable="custom">
        <template #default="scope">
          {{ parseFloat(scope.row.Slope).toFixed(4) }}
        </template>
      </el-table-column>
      <el-table-column label="Operate" header-align="right" align="right" width="250">
        <template #default="scope">
          <div class="button-group">
            <el-button size="small" type="primary" @click="handleSearch(scope.row)">
              Localization
            </el-button>
            <el-button size="small" type="success" @click="handleSave(scope.$index, scope.row)">
              Save
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.$index, scope.row)">
              Delete
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>
    <div v-if="isProcessing" class="progress-overlay">
      <el-progress :percentage="progress" status="active" />
      <p>Processing data, please wait... {{ progress.toFixed(2) }}%</p>
      <p>Elapsed time: {{ elapsedTime }}s</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import axios from 'axios';
import { useStore } from 'vuex';
import { io } from 'socket.io-client';

const store = useStore();

const sortKey = ref('');
const sortOrder = ref('');

const tableData = computed(() => store.state.tableData);
const isProcessing = computed(() => store.state.isProcessing);
const progress = computed(() => store.state.progress);

const sortedTableData = computed(() => {
  if (!sortKey.value) return tableData.value;
  return [...tableData.value].sort((a, b) => {
    let result = 0;
    if (a[sortKey.value] < b[sortKey.value]) {
      result = -1;
    } else if (a[sortKey.value] > b[sortKey.value]) {
      result = 1;
    }
    return sortOrder.value === 'ascending' ? result : -result;
  });
});

const elapsedTime = ref(0);
let timer;

const startTimer = () => {
  timer = setInterval(() => {
    elapsedTime.value += 1;
  }, 1000);
};

const stopTimer = () => {
  clearInterval(timer);
  elapsedTime.value = 0;
};

const handleSave = (index, row) => {
  // Handle save logic
};

const handleDelete = (index, row) => {
  // Handle delete logic
};

const handleSearch = (row) => {
  console.log('Search clicked:', row);
  const data = {
    TimeValues: row.TimeValues,
    MeasurementValues: row.MeasurementValues
  };
  store.dispatch('updateSelectedSmoothedData', data);
};

const handleSortChange = ({ prop, order }) => {
  sortKey.value = prop;
  sortOrder.value = order;
};

watch(isProcessing, (newVal) => {
  if (newVal) {
    store.commit('setProgress', 0); // Reset progress when starting new process
    startTimer(); // Start the timer
  } else {
    stopTimer(); // Stop the timer when processing is complete
  }
});

onMounted(() => {
  // Initialize Socket.IO client
  const socket = io('http://127.0.0.1:5000');

  socket.on('connect', () => {
    console.log('Connected to server');
  });

  socket.on('processing_complete', (data) => {
    console.log('Received processing_complete event', data);
    store.commit('setIsProcessing', false);
    store.dispatch('fetchData');
  });

  socket.on('progress_update', (data) => {
    console.log('Received progress_update event', data);
    store.commit('setProgress', data.progress);
  });
});
</script>

<style scoped>
.table-container {
  position: relative;
}

.progress-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 10;
}

.button-group {
  display: flex;
  gap: 5px;
  justify-content: space-between;
}
</style>
