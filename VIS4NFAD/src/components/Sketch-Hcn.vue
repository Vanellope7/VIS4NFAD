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
    <el-row class="slider-container" align="middle">
        <span>Zoom Level:</span>
        <el-slider v-model="zoomLevel" :min="1" :max="3" step="0.1" show-tooltip format-tooltip="formatTooltip"></el-slider>
    </el-row>
    <div class="main-container">
      <el-card class="canvas-card" shadow="never">
        <div class="canvas-container">
          <canvas ref="canvas"></canvas>
          <div class="grid-legend">
            <p>Grid Size: {{ (gridSize * zoomLevel).toFixed(2) }} x {{ (gridSize * zoomLevel).toFixed(2) }}</p>
          </div>
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
import { io } from 'socket.io-client';

const store = useStore();

const canvas = ref(null);
let fabricCanvas = null;
const isPenToolActive = ref(true);
let path, isDrawing, points = [];
const predefinedQueries = [];
const similarQueries = [];
const savedDrawings = ref([]);
const zoomLevel = ref(1);
const gridSize = 20;

const clearCanvas = () => {
  fabricCanvas.clear();
  drawGrid(); // Redraw the grid after clearing the canvas
};

const saveDrawing = () => {
  const drawing = getCurveCoordinates();
  const thumbnail = fabricCanvas.toDataURL({
    format: 'png',
    quality: 0.5,
    multiplier: 0.2,
  });
  savedDrawings.value.push
  ({ drawing, thumbnail });
};

const loadDrawing = (index) => {
  clearCanvas();
  const curveData = savedDrawings.value[index].drawing;
  loadCurveFromCoordinates(curveData);
};

const deleteDrawing = (index) => {
  savedDrawings.value.splice(index, 1);
};

const submitDrawing = () => {
  const drawingData = getCurveCoordinates();
  axios.post('http://127.0.0.1:5000/submit', { drawing: drawingData })
    .then(response => {
      console.log('Drawing submitted:', response.data);
    })
    .catch(error => {
      console.error('Error submitting drawing:', error.response ? error.response.data : error.message);
    });

  const selectedSmoothedData = store.state.selectedSmoothedData;
  const smoothness = store.state.smoothness;

  store.commit('setIsProcessing', true);
  store.commit('setProgress', 0);
  store.commit('clearTableData');

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





const getCurveCoordinates = () => {
  const objects = fabricCanvas.getObjects('path');
  return objects.map(path => ({ path: path.path }));
};

const loadCurveFromCoordinates = (curveData) => {
  curveData.forEach(data => {
    const path = new fabric.Path(data.path, {
      strokeWidth: 2,
      stroke: 'black',
      fill: 'transparent',
    });
    fabricCanvas.add(path);
  });
  fabricCanvas.renderAll();
};

const selectPredefinedQuery = (query) => {
  // Add functionality to handle predefined queries
};

const drawGrid = () => {
  const width = fabricCanvas.getWidth();
  const height = fabricCanvas.getHeight();

  for (let i = 0; i <= width / gridSize; i++) {
    fabricCanvas.add(new fabric.Line([i * gridSize, 0, i * gridSize, height], { stroke: '#ccc', selectable: false, evented: false }));
  }

  for (let i = 0; i <= height / gridSize; i++) {
    fabricCanvas.add(new fabric.Line([0, i * gridSize, width, i * gridSize], { stroke: '#ccc', selectable: false, evented: false }));
  }
};

const initCanvas = () => {
  fabricCanvas = new fabric.Canvas(canvas.value, {
    width: 370,
    height: 400,
    backgroundColor: '#fff',
  });

  drawGrid();

  fabricCanvas.isDrawingMode = true;

  fabricCanvas.on('mouse:down', function (o) {
    if (isPenToolActive.value) {
      isDrawing = true;
      const pointer = fabricCanvas.getPointer(o.e);
      points = [{ x: pointer.x, y: pointer.y }];
      path = new fabric.Path(`M ${pointer.x} ${pointer.y}`, {
        strokeWidth: 2,
        fill: 'transparent',
        stroke: 'black',
        selectable: false,
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
        const pathData = `M ${points[0].x} ${points[0].y} ` + points.map(p => `L ${p.x} ${p.y}`).join(' ');
        path.set({ path: new fabric.Path(pathData).path });
        fabricCanvas.renderAll();
      }
    }
  });

  fabricCanvas.on('mouse:up', function () {
    if (isPenToolActive.value) {
      isDrawing = false;
      points = [];
      const pathData = path.path[0].slice(1);
      if (pathData.length <= 2) {
        fabricCanvas.remove(path);
      } else {
        path.path[0] = ['M', ...pathData];
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
    fabricCanvas.forEachObject(obj => {
      obj.selectable = !newVal;
    });
    fabricCanvas.renderAll();
  });

  watch(zoomLevel, (newZoom) => {
    fabricCanvas.setViewportTransform([newZoom, 0, 0, newZoom, 0, 0]);
    fabricCanvas.renderAll();
  });
};

const formatTooltip = (value) => {
  return `Zoom: ${value.toFixed(1)}x`;
};

onMounted(() => {
  initCanvas();
  fabricCanvas.isDrawingMode = isPenToolActive.value;

  // Initialize Socket.IO client
  const socket = io('http://127.0.0.1:5000');

  socket.on('connect', () => {
    console.log('Connected to server');
  });

  socket.on('processing_complete', (data) => {
    console.log(data.message);
    store.commit('setIsProcessing', false);
    store.dispatch('fetchData');
  });

  socket.on('progress_update', (data) => {
    store.commit('setProgress', data.progress);
  });
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

.slider-container {
  width: 100%;
  margin: 10px 0;
}

.main-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.canvas-card {
  height: 390px;
  width: 100%;
}

.canvas-container {
  height: 100%;
  position: relative;
}

.grid-legend {
  position: absolute;
  bottom: 40px;
  right: 0px;
  background: rgba(255, 255, 255, 0.8);
  padding: 5px;
  border: 1px solid #ccc;
  border-radius: 8px;
}

.history-section {
  width: 100%;
  height: 200px;
  overflow-x: auto;
  overflow-y: hidden;
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
  margin-bottom: 10px;
}

.dropdown-content {
  display: flex;
  gap: 5px;
}

.dropdown-content button {
  border: none;
  background: none;
  cursor: pointer;
}

.similar-queries {
  display: flex;
  gap: 10px;
  overflow-x: auto;
}

.similar-query img {
  width: 70px;
  height: 70px;
  border: 1px solid #ccc;
  background-color: #f9f9f9;
  cursor: pointer;
}

.el-slider {
  width: 100%;
}
</style>
