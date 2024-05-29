<template>
    <div class="toolbar">
      <button @click="toggleTool('scale')">Scale</button>
      <button @click="toggleTool('offset')">Offset</button>
      <button @click="toggleTool('regex')">Regex</button>
      <button @click="undo">Undo</button>
      <button @click="redo">Redo</button>
      <button @click="clearCanvas">Clear</button>
    </div>
    <div class="canvas-container">
      <canvas ref="canvas" @mousedown="startDrawing" @mouseup="stopDrawing" @mousemove="draw"></canvas>
    </div>
</template>


<script setup>
import { ref, reactive, computed } from 'vue';

const canvas = ref(null);
const context = ref(null);
const drawing = ref(false);
const tool = ref(null);
const history = reactive([]);


const startDrawing = (event) => {
  drawing.value = true;
  context.value = canvas.value.getContext('2d');
  context.value.beginPath();
  context.value.moveTo(event.offsetX, event.offsetY);
};

const stopDrawing = () => {
  drawing.value = false;
  context.value.closePath();
};

const draw = (event) => {
  if (!drawing.value) return;
  context.value.lineTo(event.offsetX, event.offsetY);
  context.value.stroke();
};

const clearCanvas = () => {
  context.value.clearRect(0, 0, canvas.value.width, canvas.value.height);
};

const toggleTool = (selectedTool) => {
  tool.value = tool.value === selectedTool ? null : selectedTool;
};

const undo = () => {
  // Add undo functionality here
};

const redo = () => {

};

const selectQuery = (index) => {

};

const selectHistoryItem = (index) => {

};

</script>



<style>
.canvas-container {
  border: 1px solid #000;
  width: 600px;
  height:150px;
  position: relative;
}

.toolbar {
  display: flex;
  justify-content: space-around;
  margin-bottom: 10px;
}

.predefined-queries,
.history {
  margin-top: 20px;
}

.query,
.history-item {
  display: inline-block;
  margin-right: 10px;
  cursor: pointer;
}

button {
  margin-right: 10px;
}

canvas {
  width: 100%;
  height: 100%;
}

</style>

