<template>
  <div class="query-sketcher">
    <div class="canvas-header">
      <div class="query-title">Query</div>
      <div class="header-buttons">
        <button @click="togglePenTool">Toggle Pen Tool</button>
        <button @click="clearCanvas">Clear</button>
        <button @click="saveDrawing">Save</button>
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
        <div class="history-content">
          <div v-for="(drawing, index) in savedDrawings" :key="index" class="history-item">
            <img :src="drawing.thumbnail" :alt="'Drawing ' + (index + 1)" @click="loadDrawing(index)">
            <button class="delete-button" @click="deleteDrawing(index)">Delete</button>
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
import { ref, onMounted } from 'vue';
import { fabric } from 'fabric';
import 'element-plus/dist/index.css';

const canvas = ref(null);
let fabricCanvas = null;
let isPenToolActive = false;
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

const togglePenTool = () => {
  isPenToolActive = !isPenToolActive;
  if (isPenToolActive) {
    fabricCanvas.isDrawingMode = false;
    fabricCanvas.selection = false;
  } else {
    fabricCanvas.isDrawingMode = true;
    fabricCanvas.selection = true;
  }
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

const selectPredefinedQuery = (query) => {
  // Add functionality to handle predefined queries
};

const initCanvas = () => {
  fabricCanvas = new fabric.Canvas(canvas.value, {
    width: 600,
    height: 400,
    backgroundColor: '#fff',
  });

  // Enable free drawing mode by default
  fabricCanvas.isDrawingMode = true;

  fabricCanvas.on('mouse:down', function (o) {
    if (isPenToolActive) {
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
    if (isPenToolActive && isDrawing) {
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
    if (isPenToolActive) {
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
    if (isPenToolActive) {
      activeObject.set({
        borderColor: 'red',
        cornerColor: 'green',
        cornerSize: 6,
        transparentCorners: false,
      });
    }
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
  align-items: flex-start;
}

.canvas-card {
  flex-grow: 1;
  height: 400px;
  margin-right: 20px;
}

.canvas-container {
  height: 100%;
  position: relative;
}

.history-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 400px;
  overflow-y: auto;
  width: 250px;
}

.history-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 10px;
  flex-shrink: 0;
}

.history-content {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  width: 100%;
}

.history-item {
  width: 70px;
  height: 70px;
  margin: 5px;
  position: relative;
  border: 1px solid #ccc;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f9f9f9;
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
