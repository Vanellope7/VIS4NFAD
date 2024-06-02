<template>
  <div class="query-sketcher">
    <div class="canvas-header">
      <div class="query-title">Query</div>
      <div class="header-buttons">
        <el-switch v-model="isPenToolActive" active-text="Pen" inactive-text="Zoom" />
        <el-button round @click="clearCanvas" size="small" type="danger">Clear</el-button>
        <el-button round @click="saveDrawing" size="small" type="success">Save</el-button>
        <el-button round @click="submitDrawing" size="small" type="primary">Submit</el-button>
      </div>
    </div>
    <div class="main-container">
      <el-card class="canvas-card" shadow="never">
        <div class="canvas-container">
          <canvas ref="canvas"></canvas>
        </div>
      </el-card>
      <el-card class="history-section" shadow="never">
        <template #header>
          <div class="card-header">
            <h3>History</h3>
          </div>
        </template>
        <div class="history-content-container">
          <div class="history-content">
            <div v-for="(drawing, index) in savedDrawings" :key="index" class="history-item">
              <img :src="drawing.thumbnail" :alt="'Drawing ' + (index + 1)" @click="loadDrawing(index)">
              <button class="delete-button" @click="deleteDrawing(index)">Delete</button>
            </div>
          </div>
        </div>
      </el-card>
    </div>
    <div class="predefined-section">
      <div class="dropdown">
        <div class="dropdown-content">
          <button v-for="(query, index) in predefinedQueries" :key="index" @click="selectPredefinedQuery(query)">
            <img :src="query.thumbnail" :alt="'Query ' + (index + 1)">
          </button>
        </div>
      </div>
      <div class="similar-queries">
        <div v-for="(query, index) in similarQueries" :key="index" class="similar-query">
          <img :src="query.thumbnail" :alt="'Similar Query ' + (index + 1)">
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import axios from 'axios';
import { fabric } from 'fabric';
import 'element-plus/dist/index.css';
import { useStore } from 'vuex';

const store = useStore();

const canvas = ref(null);
let fabricCanvas = null;
const isPenToolActive = ref(true);
let path, isDrawing, points = [];
const predefinedQueries = [
  // Add paths to predefined curve thumbnails here
];
const similarQueries = [
  // Add paths to similar predefined curve thumbnails here
];
const savedDrawings = ref([]);

const clearCanvas = () => {
  fabricCanvas.clear();
};

const saveDrawing = () => {
  const drawing = fabricCanvas.toJSON();
  const thumbnail = fabricCanvas.toDataURL({
    format: 'png',
    quality: 0.5,
    multiplier: 0.2,
  });
  savedDrawings.value.push({ drawing, thumbnail });
};

const loadDrawing = (index) => {
  clearCanvas();
  fabricCanvas.loadFromJSON(savedDrawings.value[index].drawing, () => {
    fabricCanvas.renderAll();
  });
};

const deleteDrawing = (index) => {
  savedDrawings.value.splice(index, 1);
};

const submitDrawing = () => {
  const drawingData = fabricCanvas.toJSON();
  // 原有的submit功能
  axios.post('http://127.0.0.1:5000/submit', { drawing: drawingData })
    .then(response => {
      console.log('Drawing submitted:', response.data);
    })
    .catch(error => {
      console.error('Error submitting drawing:', error.response ? error.response.data : error.message);
    });

  // 新增功能：提交 selectedSmoothedData 和 smoothness
  const selectedSmoothedData = store.state.selectedSmoothedData;
  const smoothness = store.state.smoothness;

  axios.post('http://127.0.0.1:5000/submit_smoothed_data', {
    selectedSmoothedData: selectedSmoothedData,
    smoothness: smoothness
  })
    .then(response => {
      console.log('Smoothed data submitted:', response.data);
    })
    .catch(error => {
      console.error('Error submitting smoothed data:', error.response ? error.response.data : error.message);
    });
};

const selectPredefinedQuery = (query) => {
  // Add functionality to handle predefined queries
};

const initCanvas = () => {
  fabricCanvas = new fabric.Canvas(canvas.value, {
    width: 370,
    height: 450,
    backgroundColor: '#fff',
  });

  // Enable free drawing mode by default
  fabricCanvas.isDrawingMode = true;

  fabricCanvas.on('mouse:down', function (o) {
    if (isPenToolActive.value) {
      isDrawing = true;
      const pointer = fabricCanvas.getPointer(o.e);
      points = [{ x: pointer.x, y: pointer.y }];
      path = new fabric.Path('M ' + pointer.x + ' ' + pointer.y + ' L ' + pointer.x + ' ' + pointer.y, {
        strokeWidth: 2,
        fill: 'transparent',
        stroke: 'black',
      });
      fabricCanvas.add(path);
    }
  });

  fabricCanvas.on('mouse:move', function (o) {
    if (isPenToolActive.value && isDrawing) {
      const pointer = fabricCanvas.getPointer(o.e);
      const lastPoint = points[points.length - 1];
      if (pointer.x >= lastPoint.x) {
        points.push({ x: pointer.x, y: pointer.y });
        const pathData = path.path[0].slice(1);
        pathData.push(pointer.x, pointer.y);
        path.path[0] = ['M', ...pathData];
        fabricCanvas.renderAll();
      }
    }
  });

  fabricCanvas.on('mouse:up', function () {
    if (isPenToolActive.value) {
      isDrawing = false;
      points = [];
      const pathData = path.path[0].slice(1);
      if (pathData.length > 2) {
        path.path[0] = ['M', ...pathData];
      } else {
        fabricCanvas.remove(path);
      }
    }
  });

  fabricCanvas.on('object:selected', function (e) {
    const activeObject = e.target;
    if (isPenToolActive.value) {
      activeObject.set({
        borderColor: 'red',
        cornerColor: 'green',
        cornerSize: 6,
        transparentCorners: false,
      });
    }
  });

  watch(isPenToolActive, (newVal) => {
    fabricCanvas.isDrawingMode = newVal;
    fabricCanvas.selection = !newVal;
  });
};

onMounted(() => {
  initCanvas();
});
</script>

<style scoped>
.query-sketcher {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.canvas-header {
  display: flex;
  justify-content: space-between;
  width: 100%;
  padding: 10px;
}

.query-title {
  font-size: 18px;
  font-weight: bold;
}

.header-buttons button {
  margin: 0 5px;
}

.main-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.canvas-card {
  height: 470px;
  width: 100%;
}

.canvas-container {
  height: 100%;
  position: relative;
}

.history-section {
  width: 100%;
  height: 200px;
  /* Maintain the original height */
  overflow-x: auto;
  overflow-y: hidden;
  /* Hide vertical scrollbar */
  margin-top: 10px;
}

.history-title {
  font-size: 18px;
  font-weight: bold;
  flex-shrink: 0;
}

.history-content-container {
  width: 370px;
  overflow-x: auto;
  white-space: nowrap;
}

.history-content {
  display: inline-flex;
  gap: 10px;
  padding: 5px;
}

.history-item {
  width: 70px;
  height: 70px;
  position: relative;
  border: 1px solid #ccc;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f9f9f9;
  flex-shrink: 0;
  /* Prevent items from shrinking */
}

.history-item img {
  width: 50px;
  height: 50px;
  cursor: pointer;
}

.delete-button {
  position: absolute;
  top: 0;
  right: 0;
  background-color: red;
  color: white;
  border: none;
  cursor: pointer;
  padding: 2px 5px;
  font-size: 10px;
}

.predefined-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 10px;
}

.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown .dropbtn {
  background-color: #f9f9f9;
  color: black;
  padding: 10px;
  font-size: 16px;
  border: none;
  cursor: pointer;
}

.dropdown .dropdown-content {
  display: none;
  position: absolute;
  background-color: #f9f9f9;
  min-width: 160px;
  box-shadow: 0px 8px 16px 0px rgba(0, 0, 0, 0.2);
  z-index: 1;
}

.dropdown .dropdown-content button {
  color: black;
  padding: 12px 16px;
  text-decoration: none;
  display: block;
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
}

.dropdown .dropdown-content button:hover {
  background-color: #f1f1f1;
}

.dropdown:hover .dropdown-content {
  display: block;
}

.dropdown:hover .dropbtn {
  background-color: #f1f1f1;
}

.similar-queries {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.similar-query img {
  width: 50px;
  height: 50px;
  cursor: pointer;
}
</style>
