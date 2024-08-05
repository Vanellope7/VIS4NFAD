<template>
  <div class="table-container">
    <el-table :data="sortedTableData" style="width: 100%" height="320" @sort-change="handleSortChange">
      <!-- 复选框列 -->
      <el-table-column label=" " width="70">
        <template #header>
          <el-checkbox 
            :model-value="isAllSelected" 
            @change="handleSelectAllChange">
            <el-icon><View /></el-icon>
          </el-checkbox>
        </template>
        <template #default="scope">
          <el-checkbox 
            v-model="checkboxState[scope.$index]" 
            @change="handleCheckboxChange(scope.row, scope.$index)">
          </el-checkbox>
        </template>
      </el-table-column>
      <!-- Index column -->
      <el-table-column label="N" width="40">
        <template #default="scope">
          {{ scope.$index + 1 }}
        </template>
      </el-table-column>
      <!-- Table columns here -->
      <el-table-column prop="Hcn" label="Hcn">
        <template #default="scope">
          {{ scope.row.Hcn }}
        </template>
      </el-table-column>
      <el-table-column prop="CombinedSimilarity" label="Combine Similarity" sortable="custom">
        <template #default="scope">
          <span>{{ parseFloat(scope.row.CombinedSimilarity).toFixed(4) }}</span>
        </template>
      </el-table-column>
      <!-- Other similarity columns here -->
      <el-table-column prop="CosineSimilarity" label="Cosine Similarity" sortable="custom">
        <template #default="scope">
          <span>{{ calculateCosineSimilarity(scope.row) }}%</span>
        </template>
      </el-table-column>
      <el-table-column prop="EuclideanDistance" label="Euclidean Distance" sortable="custom">
        <template #default="scope">
          <span>{{ calculateEuclideanDistance(scope.row) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="SlopeSimilarity" label="Slope Similarity" sortable="custom">
        <template #default="scope">
          <span>{{ calculateSlopeSimilarity(scope.row) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="MatchPrecision" label="Match Precision" sortable="custom">
        <template #default="scope">
          <div class="match-precision">
            <div class="precision-bar" :style="{ width: calculateMatchPrecision(scope.row.Smooth) + '%' }"></div>
            <span>{{ calculateMatchPrecision(scope.row.Smooth).toFixed(2) }}%</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="PeriodLength" label="Period Length (s)" sortable="custom">
        <template #default="scope">
          <span>{{ calculatePeriodLength(scope.row).toFixed(4) }}s</span>
        </template>
      </el-table-column>
      <el-table-column prop="StartPoint" label="Start Point (s)" sortable="custom">
        <template #default="scope">
          <span>{{ calculateStartPoint(scope.row).toFixed(4) }}s</span>
        </template>
      </el-table-column>
      <el-table-column prop="Length" label="Length" sortable="custom">
        <template #default="scope">
          <span>{{ calculateLength(scope.row).toFixed(4) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Operate" header-align="right" align="right" width="100">
        <template #default="scope">
          <div class="button-group">
            <el-button size="small" type="success" @click="handleSave(scope.$index, scope.row)">
              <el-icon><FolderChecked /></el-icon>
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.$index, scope.row)">
              <el-icon><FolderDelete /></el-icon>
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>
    <div v-if="isProcessing" class="progress-overlay">
      <div class="gradient-progress-bar">
        <div class="progress" :style="{ width: progress + '%' }"></div>
      </div>
      <p>Processing data, please wait... {{ progress.toFixed(2) }}%</p>
      <p>Elapsed time: {{ elapsedTime }}s</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useStore } from 'vuex';
import { io } from 'socket.io-client';
import { FolderChecked, FolderDelete, View } from '@element-plus/icons-vue';

const store = useStore();

const sortKey = ref('');
const sortOrder = ref('');
const checkboxState = ref([]);

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

const isAllSelected = computed(() => {
  return checkboxState.value.length > 0 && checkboxState.value.every(item => item);
});

const calculateMatchPrecision = (smooth) => {
  return (1 - smooth) * 100;
};

const calculateCosineSimilarity = (row) => {
  return parseFloat(row.CosineSimilarity).toFixed(4);
};

const calculateEuclideanDistance = (row) => {
  return parseFloat(row.EuclideanDistance).toFixed(4);
};

const calculateSlopeSimilarity = (row) => {
  return parseFloat(row.SlopeSimilarity).toFixed(4);
};

const calculatePeriodLength = (row) => {
  return row.TimeValues[row.TimeValues.length - 1] - row.TimeValues[0];
};

const calculateStartPoint = (row) => {
  return row.TimeValues[0];
};

const calculateLength = (row) => {
  return row.MeasurementValues.length;
};

const elapsedTime = ref(0);
let timer;

const startTimer = () => {
  if (!timer) {
    timer = setInterval(() => {
      elapsedTime.value += 1;
    }, 1000);
  }
};

const stopTimer = () => {
  if (timer) {
    clearInterval(timer);
    timer = null;
  }
  elapsedTime.value = 0;
};

const handleSave = (index, row) => {
  // Handle save logic
};

const handleDelete = (index, row) => {
  // Handle delete logic
};

const generateUniqueID = () => '_' + Math.random().toString(36).substr(2, 9);

const handleCheckboxChange = (row, index) => {
  const segmentId = `${row.Hcn}-${index}`;
  const segment = {
    id: segmentId,
    name: row.Hcn,
    data: {
      TimeValues: row.TimeValues,
      MeasurementValues: row.MeasurementValues
    }
  };
  if (checkboxState.value[index]) {
    store.dispatch('addHighlightedSegment', segment);
  } else {
    store.dispatch('removeHighlightedSegmentById', segmentId); // 根据ID移除高亮段
  }
};

const handleSelectAllChange = (value) => {
  checkboxState.value = checkboxState.value.map(() => value);
  sortedTableData.value.forEach((row, index) => {
    const segmentId = `${row.Hcn}-${index}`;
    const segment = {
      id: segmentId,
      name: row.Hcn,
      data: {
        TimeValues: row.TimeValues,
        MeasurementValues: row.MeasurementValues
      }
    };
    if (value) {
      store.dispatch('addHighlightedSegment', segment);
    } else {
      store.dispatch('removeHighlightedSegmentById', segmentId); // 根据ID移除高亮段
    }
  });
};

const handleSortChange = ({ prop, order }) => {
  sortKey.value = prop;
  sortOrder.value = order;
};

watch(isProcessing, (newVal) => {
  if (newVal) {
    store.commit('setProgress', 0); 
    startTimer(); 
  } else {
    stopTimer(); 
  }
});

watch(tableData, (newData) => {
  checkboxState.value = new Array(newData.length).fill(false);
}, { immediate: true });

onMounted(() => {
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

.gradient-progress-bar {
  width: 70%;
  height: 10px;
  background: linear-gradient(to right, #4caf50, #ffeb3b, #f44336);
  border-radius: 5px;
  overflow: hidden;
  margin-bottom: 10px;
  background-color: transparent;
  /* 透明背景 */
}

.gradient-progress-bar .progress {
  height: 100%;
  background-color: rgba(0, 0, 0, 0.2);
  transition: width 0.3s ease-in-out;
  /* 平滑过渡效果 */
}

.button-group {
  display: flex;
  gap: 5px;
  justify-content: space-between;
}

.match-precision {
  display: flex;
  align-items: center;
}

.precision-bar {
  height: 10px;
  background-color: #4CAF50;
  margin-right: 5px;
}
</style>
