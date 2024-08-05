<template>
  <div ref="chartContainer" class="chart-container">
    <div ref="sliderContainer" class="slider-container">
      <label for="smoothness">Smoothness: </label>
      <input type="range" id="smoothness" name="smoothness" min="0" max="1" step="0.01" v-model="smoothness">
      <span>{{ smoothness }}</span>
    </div>
    <div ref="chart"></div>
    <div ref="overview" class="overview-container"></div>
    <div ref="legend" class="legend-container"></div>
    <button @click="exportHighlightedData" class="export-button">导出异常数据</button>
    <button @click="toggleSelectionMode" class="selection-button">框选模式</button>
    <div v-if="showForm" class="highlight-form">
      <label for="exceptionType">异常类型:</label>
      <select id="exceptionType" v-model="exceptionType">
        <option value="type1">类型1</option>
        <option value="type2">类型2</option>
        <option value="type3">类型3</option>
      </select>
      <label for="exceptionDescription">异常描述:</label>
      <textarea id="exceptionDescription" v-model="exceptionDescription"></textarea>
      <button @click="saveHighlightData">保存</button>
    </div>
  </div>
</template>

<script setup>
import * as d3 from 'd3';
import axios from 'axios';
import { onMounted, ref, watch, computed } from 'vue';
import { useStore } from 'vuex';
import debounce from 'lodash/debounce';

// Setup references
const chart = ref(null);
const overview = ref(null);
const legend = ref(null);
const smoothness = ref(0.0);
const showForm = ref(false);
const exceptionType = ref('');
const exceptionDescription = ref('');
const currentHighlightIndex = ref(null);
const selectionMode = ref(false);
const selectionRect = ref(null);
const startPoint = ref(null);
const endPoint = ref(null);
const highlightedSegmentsOrange = ref([]);

// Vuex store
const store = useStore();
const selectedData = computed(() => store.state.selectedSmoothedData);
const highlightedSegments = computed(() => store.state.highlightedSegments);

// Function to handle form submission
const saveHighlightData = () => {
  if (currentHighlightIndex.value !== null) {
    store.commit('updateHighlightedSegment', {
      index: currentHighlightIndex.value,
      type: exceptionType.value,
      description: exceptionDescription.value,
    });
    showForm.value = false;
  }
};

const exportHighlightedData = () => {
  const dataToExport = [...highlightedSegments.value, ...highlightedSegmentsOrange.value].map(segment => {
    console.log('Segment5345345:', segment.name); // Check segment to ensure lineName is present
    return {
      Hcn: segment.name,
      data: segment.data,
      type: segment.type,
      description: segment.description,
    };
  });

  console.log('Data to Export:', dataToExport); // Check final data to export

  const json = JSON.stringify(dataToExport, null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'highlighted_data.json';
  a.click();
  URL.revokeObjectURL(url);
};


// Function to toggle selection mode
const toggleSelectionMode = () => {
  selectionMode.value = !selectionMode.value;
  if (selectionMode.value) {
    d3.select(chart.value).style('cursor', 'crosshair');
  } else {
    d3.select(chart.value).style('cursor', 'default');
  }
};

// On component mount
onMounted(async () => {
  try {
    const response = await axios.get('/data/hcnData.json');
    const data = response.data;
    const hcn = data.hcn;
    const time = data.time;

    // Define dimensions and margins
    const margin = { top: 10, right: 130, bottom: 30, left: 60 },
      width = 1250 - margin.left - margin.right,
      height = 600 - margin.top - margin.bottom,
      overviewHeight = 50;

    // Create SVG for the main chart
    const svg = d3.select(chart.value)
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom);

    // Define clipping area
    const clip = svg.append("defs").append("svg:clipPath")
      .attr("id", "clip")
      .append("svg:rect")
      .attr("width", width)
      .attr("height", height)
      .attr("x", 0)
      .attr("y", 0);

    // Chart area
    const chartArea = svg.append("g")
      .attr("clip-path", "url(#clip)")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Define scales
    const xMin = d3.min(time) - 0.5;
    const xMax = d3.max(time);
    const yMin = d3.min(hcn, d => d3.min(d.filter(val => val !== null))) - 25;
    const yMax = d3.max(hcn, d => d3.max(d.filter(val => val !== null))) + 25;

    const x = d3.scaleLinear().domain([xMin, xMax]).range([0, width]);
    const y = d3.scaleLinear().domain([yMin, yMax]).range([height, 0]);

    // Define axes
    const xAxis = d3.axisBottom(x).ticks(10).tickSizeOuter(0).tickPadding(10).tickFormat(d3.format(".1f"));
    const yAxis = d3.axisLeft(y).ticks(10).tickSizeOuter(0).tickPadding(10).tickFormat(d3.format("d"));

    // Append axes to the SVG
    svg.append("g")
      .attr("class", "x-axis")
      .attr("transform", `translate(${margin.left},${margin.top + height})`)
      .call(xAxis);

    svg.append("g")
      .attr("class", "y-axis")
      .attr("transform", `translate(${margin.left},${margin.top})`)
      .call(yAxis);

    // Append grid lines
    const makeXGridlines = () => d3.axisBottom(x).ticks(10);
    const makeYGridlines = () => d3.axisLeft(y).ticks(10);

    svg.append("g")
      .attr("class", "grid-x")
      .attr("transform", `translate(${margin.left},${margin.top + height})`)
      .call(makeXGridlines().tickSize(-height).tickFormat(""))
      .selectAll("line")
      .style("stroke-dasharray", ("3, 3"))
      .style("opacity", 0.3);

    svg.append("g")
      .attr("class", "grid-y")
      .attr("transform", `translate(${margin.left},${margin.top})`)
      .call(makeYGridlines().tickSize(-width).tickFormat(""))
      .selectAll("line")
      .style("stroke-dasharray", ("3, 3"))
      .style("opacity", 0.3);

    // Append labels
    svg.append("text")
      .attr("transform", `translate(${margin.left + width / 2}, ${margin.top + height + margin.bottom + 0})`)
      .attr("text-anchor", "middle")
      .style("font-size", "16px")
      .text("Time(s)");

    svg.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", margin.left - 60)
      .attr("x", 0 - (margin.top + height / 2))
      .attr("dy", "1em")
      .attr("text-anchor", "middle")
      .style("font-size", "16px")
      .text("10^7/m^2");

    // Generate paths for each data series
    const paths = [];
    const lineGenerator = d3.line()
      .x(d => x(d.x))
      .y(d => y(d.y))
      .curve(d3.curveBasis);

    hcn.forEach((lineData, index) => {
      const lineName = `${4043 + index}/hcn_ne001`;

      const originalPath = chartArea.append("path")
        .datum(lineData.map((d, i) => ({ x: time[i], y: d })).filter(d => d.y !== null))
        .attr("fill", "none")
        .attr("stroke", d3.schemeCategory10[index % 10])
        .attr("stroke-width", 1.5)
        .attr("class", `original-line original-line-${index}`)
        .attr("d", lineGenerator);

      const smoothedPath = chartArea.append("path")
        .datum(lineData.map((d, i) => ({ x: time[i], y: d })).filter(d => d.y !== null))
        .attr("fill", "none")
        .attr("stroke", d3.schemeCategory10[index % 10])
        .attr("stroke-width", 1.5)
        .attr("class", `smoothed-line smoothed-line-${index}`)
        .attr("opacity", 0.0);

      paths.push({ originalPath, smoothedPath, lineName });

      svg.append("line")
        .attr("x1", width + 10)
        .attr("y1", index * 20 + 5)
        .attr("x2", width + 30)
        .attr("y2", index * 20 + 5)
        .attr("stroke", d3.schemeCategory10[index % 10])
        .attr("stroke-width", 5)
        .attr("transform", `translate(${margin.left},${margin.top})`);

      svg.append("text")
        .attr("x", width + 35)
        .attr("y", index * 20 + 8)
        .attr("fill", "black")
        .style("font-size", "10px")
        .attr("transform", `translate(${margin.left},${margin.top})`)
        .text(lineName);

      // Create checkboxes
      d3.select(chart.value).append('div')
        .style('position', 'absolute')
        .style('left', `${width + margin.left + 110}px`)
        .style('top', `${margin.top + index * 20 + 18}px`)
        .html(`<input type="checkbox" checked="checked" id="checkbox-${index}" />`)
        .on('change', function () {
          const checked = d3.select(`#checkbox-${index}`).property('checked');
          d3.select(`.original-line-${index}`).style('display', checked ? null : 'none');
          d3.select(`.smoothed-line-${index}`).style('display', checked ? null : 'none');
          debouncedUpdateStore();
        });
    });

    // Add "Select All" and "Clear All" buttons
    const legendContainer = d3.select(legend.value)
      .append('div')
      .style('position', 'absolute')
      .style('left', `${width + margin.left + 15}px`)
      .style('top', `${margin.top + hcn.length * 20 + 40}px`)
      .style('display', 'flex')
      .style('gap', '10px')
      .style('align-items', 'center');

    legendContainer.append('button')
      .text('全选')
      .attr('class', 'legend-button')
      .style('font-size', '16px')
      .on('click', () => {
        d3.selectAll('input[type=checkbox]').property('checked', true);
        d3.selectAll('.original-line').style('display', null);
        d3.selectAll('.smoothed-line').style('display', null);
        debouncedUpdateStore();
      });

    legendContainer.append('button')
      .text('清空')
      .attr('class', 'legend-button')
      .style('font-size', '16px')
      .on('click', () => {
        d3.selectAll('input[type=checkbox]').property('checked', false);
        d3.selectAll('.original-line').style('display', 'none');
        d3.selectAll('.smoothed-line').style('display', 'none');
        debouncedUpdateStore();
      });

    // Overview chart setup
    const overviewSvg = d3.select(overview.value)
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", overviewHeight + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    const xOverview = d3.scaleLinear().domain([xMin, xMax]).range([0, width]);
    const yOverview = d3.scaleLinear().domain([yMin, yMax]).range([overviewHeight, 0]);

    overviewSvg.append("g")
      .attr("class", "x-axis")
      .attr("transform", `translate(0,${overviewHeight})`)
      .call(d3.axisBottom(xOverview).ticks(10).tickFormat(d3.format(".1f")));

    hcn.forEach((lineData, index) => {
      overviewSvg.append("path")
        .datum(lineData.map((d, i) => ({ x: time[i], y: d })).filter(d => d.y !== null))
        .attr("fill", "none")
        .attr("stroke", d3.schemeCategory10[index % 10])
        .attr("stroke-width", 1)
        .attr("d", d3.line()
          .x(d => xOverview(d.x))
          .y(d => yOverview(d.y))
          .curve(d3.curveBasis));
    });

    const brush = d3.brushX()
      .extent([[0, 0], [width, overviewHeight]])
      .on("brush end", brushed);

    overviewSvg.append("g")
      .attr("class", "brush")
      .call(brush);

    function brushed(event) {
      const selection = event.selection || xOverview.range();
      const newX = selection.map(xOverview.invert, xOverview);

      x.domain(newX);
      svg.selectAll(".x-axis").call(d3.axisBottom(x).ticks(10).tickFormat(d3.format(".1f")));

      paths.forEach((path, index) => {
        if (d3.select(`#checkbox-${index}`).property("checked")) {
          path.originalPath.attr("d", lineGenerator);
          path.smoothedPath.attr("d", lineGenerator);
        }
      });

      svg.selectAll(".grid-x")
        .call(makeXGridlines().scale(x).tickSize(-height).tickFormat(""))
        .selectAll("line")
        .style("stroke-dasharray", ("3, 3"))
        .style("opacity", 0.3);

      // Update the highlight line and highlight area
      updateHighlightArea();
      updateHighlightAreaOrange();
    }

    // Function to update highlight areas
    function updateHighlightArea() {
  chartArea.selectAll('.highlight-line').remove();
  chartArea.selectAll('.highlight-area').remove();

  highlightedSegments.value.forEach((segment, index) => {
    const highlightData = segment.data.TimeValues.map((d, i) => ({ x: d, y: segment.data.MeasurementValues[i] }));
    chartArea.append('path')
      .datum(highlightData)
      .attr('class', 'highlight-line')
      .attr('fill', 'none')
      .attr('stroke', 'red')
      .attr('stroke-width', 3)
      .attr('d', lineGenerator)
      .attr('pointer-events', 'all')  // Ensure the path is clickable
      .style('cursor', 'pointer')  // Set cursor to pointer
      .on('click', () => {
        currentHighlightIndex.value = index;
        exceptionType.value = segment.type || '';
        exceptionDescription.value = segment.description || '';
        showForm.value = true;
      });

    const xHighlightMin = d3.min(highlightData, d => d.x);
    const xHighlightMax = d3.max(highlightData, d => d.x);
    chartArea.append('rect')
      .attr('class', 'highlight-area')
      .attr('x', x(xHighlightMin))
      .attr('y', 0)
      .attr('width', x(xHighlightMax) - x(xHighlightMin))
      .attr('height', height)
      .attr('fill', 'red')
      .attr('opacity', 0.1)
      .attr('pointer-events', 'none');  // Ensure the rect doesn't block the path clicks
  });
}

function updateHighlightAreaOrange() {
  chartArea.selectAll('.highlight-line-orange').remove();
  chartArea.selectAll('.highlight-area-orange').remove();

  highlightedSegmentsOrange.value.forEach((segment, index) => {
    const highlightData = segment.data.TimeValues.map((d, i) => ({ x: d, y: segment.data.MeasurementValues[i] }));
    chartArea.append('path')
      .datum(highlightData)
      .attr('class', 'highlight-line-orange')
      .attr('fill', 'none')
      .attr('stroke', 'orange')
      .attr('stroke-width', 3)
      .attr('d', lineGenerator)
      .attr('pointer-events', 'all')  // Ensure the path is clickable
      .style('cursor', 'pointer')  // Set cursor to pointer
      .on('click', () => {
        currentHighlightIndex.value = index;
        exceptionType.value = segment.type || '';
        exceptionDescription.value = segment.description || '';
        showForm.value = true;
      });

    const xHighlightMin = d3.min(highlightData, d => d.x);
    const xHighlightMax = d3.max(highlightData, d => d.x);
    chartArea.append('rect')
      .attr('class', 'highlight-area-orange')
      .attr('x', x(xHighlightMin))
      .attr('y', 0)
      .attr('width', x(xHighlightMax) - x(xHighlightMin))
      .attr('height', height)
      .attr('fill', 'orange')
      .attr('opacity', 0.1)
      .attr('pointer-events', 'none');  // Ensure the rect doesn't block the path clicks
  });
}

    // Update store data with debounce
    const debouncedUpdateStore = debounce(() => {
  const selectedData = [];
  paths.forEach((path, index) => {
    console.log('Path:', path); // Check path to ensure lineName is present
    if (d3.select(`#checkbox-${index}`).property("checked")) {
      const data = path.smoothedPath.datum();
      selectedData.push({ name: path.lineName, data });
    }
  });
  console.log('Selected Data:', selectedData); // Check selected data
  store.dispatch('updateSelectedSmoothedData', selectedData);
}, 300);

    // Watch for smoothness changes
    watch(smoothness, (newValue) => {
      store.dispatch('updateSmoothness', newValue);
      paths.forEach((path, index) => {
        if (d3.select(`#checkbox-${index}`).property("checked")) {
          const lineData = hcn[index].map((d, i) => ({ x: time[i], y: d })).filter(d => d.y !== null);
          const interpolatedData = interpolateData(lineData, smoothness.value);
          path.smoothedPath.datum(interpolatedData).attr("d", lineGenerator.curve(d3.curveBasis));
          path.originalPath.attr("opacity", 0.5 - 0.3 * smoothness.value); // Adjust transparency
          path.smoothedPath.attr("opacity", 1);
        }
      });
      debouncedUpdateStore();
    });

    // Data interpolation function
    function interpolateData(data, t) {
      if (t === 0) {
        return data;
      } else {
        const steps = Math.ceil(t * 200); // Increase smoothing steps
        let smoothedData = data;

        for (let i = 0; i < steps; i++) {
          smoothedData = smoothedData.map((d, i, a) => {
            if (i === 0 || i === a.length - 1) {
              return d;
            } else {
              return {
                x: d.x,
                y: (a[i - 2]?.y || d.y) * 0.1 + a[i - 1].y * 0.2 + d.y * 0.4 + a[i + 1].y * 0.2 + (a[i + 2]?.y || d.y) * 0.1
              };
            }
          });
        }

        return smoothedData;
      }
    }

    // Watch for changes in highlighted segments
    watch(highlightedSegments, (newSegments) => {
      updateHighlightArea();
    }, { deep: true });

    // Handle selection events
    d3.select(chart.value)
  .on('mousedown', (event) => {
    if (!selectionMode.value) return;
    const [x0, y0] = d3.pointer(event);
    startPoint.value = { x: x0, y: y0 };
    selectionRect.value = svg.append('rect')
      .attr('class', 'selection-rect')
      .attr('x', x0)
      .attr('y', y0)
      .attr('width', 0)
      .attr('height', 0)
      .attr('fill', 'orange')
      .attr('opacity', 0.3);
  })
  .on('mousemove', (event) => {
    if (!selectionMode.value || !selectionRect.value) return;
    const [x1, y1] = d3.pointer(event);
    const x0 = startPoint.value.x;
    const y0 = startPoint.value.y;
    selectionRect.value
      .attr('width', Math.abs(x1 - x0))
      .attr('height', Math.abs(y1 - y0))
      .attr('x', Math.min(x1, x0))
      .attr('y', Math.min(y1, y0));
  })
  .on('mouseup', (event) => {
    if (!selectionMode.value || !selectionRect.value) return;
    const [x1, y1] = d3.pointer(event);
    endPoint.value = { x: x1, y: y1 };

    const x0 = startPoint.value.x;
    const y0 = startPoint.value.y;
    const xMinSel = Math.min(x0, x1);
    const xMaxSel = Math.max(x0, x1);
    const yMinSel = Math.min(y0, y1);
    const yMaxSel = Math.max(y0, y1);

    const highlightedSegmentData = [];
    paths.forEach((path, index) => {
      if (d3.select(`#checkbox-${index}`).property("checked")) {
        const lineData = path.smoothedPath.datum();
        const segmentData = lineData.filter(d => {
          const xVal = x(d.x);
          const yVal = y(d.y);
          return xVal >= xMinSel && xVal <= xMaxSel && yVal >= yMinSel && yVal <= yMaxSel;
        });
        if (segmentData.length > 0) {
          
          highlightedSegmentData.push({
            data: {
              TimeValues: segmentData.map(d => d.x),
              MeasurementValues: segmentData.map(d => d.y),
              lineName: path.lineName // Add lineName here
            },
            type: 'type1',  // Default type
            description: '' // Default description
          });
        }
      }
    });

    highlightedSegmentsOrange.value = [...highlightedSegmentsOrange.value, ...highlightedSegmentData];
    updateHighlightAreaOrange();

    // Remove selection rectangle and reset mode
    selectionRect.value.remove();
    selectionRect.value = null;
    startPoint.value = null;
    endPoint.value = null;
    toggleSelectionMode();
  });


  } catch (error) {
    console.error("Error fetching data:", error);
  }
});
</script>

<style scoped>
.chart-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.overview-container {
  width: 80%;
  height: 100px;
}

.legend-container {
  width: 100%;
  gap: 10px;
  margin-top: 10px;
}

.slider-container {
  width: 100%;
  margin-top: 10px;
  display: flex;
  flex-direction: row;
  gap: 10px;
}

.legend-button {
  background-color: #4CAF50;
  border: none;
  color: white;
  padding: 8px 16px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 12px;
  margin: 4px 2px;
  cursor: pointer;
  border-radius: 5px;
}

.export-button {
  background-color: #2196F3;
  border: none;
  color: white;
  padding: 8px 16px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 12px;
  margin: 4px 2px;
  cursor: pointer;
  border-radius: 5px;
  position: absolute;
  top: -18px;
  right: 90px;
}

.selection-button {
  background-color: #FF9800;
  border: none;
  color: white;
  padding: 8px 16px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 12px;
  margin: 4px 2px;
  cursor: pointer;
  border-radius: 5px;
  position: absolute;
  top: -18px;
  right: 0px;
}

.highlight-form {
  position: absolute;
  top: 20px;
  right: 20px;
  background-color: white;
  border: 1px solid #ccc;
  padding: 20px;
  border-radius: 5px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.highlight-form label {
  display: block;
  margin-bottom: 10px;
  font-weight: bold;
}

.highlight-form select,
.highlight-form textarea {
  width: 100%;
  margin-bottom: 10px;
}

svg {
  font: 10px sans-serif;
}

.axis path,
.axis line {
  fill: none;
  shape-rendering: crispEdges;
}

.overlay {
  fill: none;
  pointer-events: all;
}

.zoom {
  cursor: move;
  fill: none;
  pointer-events: all;
}

.selection-rect {
  fill: orange;
  opacity: 0.3;
}
</style>
