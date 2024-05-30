<template>
    <div ref="chartContainer" class="chart-container">
        <div ref="chart"></div>
<!--        <div ref="slider" class="slider-container"></div>-->
        <div ref="legend" class="legend-container"></div>
    </div>
</template>

<script setup>
import * as d3 from 'd3';
import axios from 'axios';
import {h, onMounted, ref} from 'vue';

const chart = ref(null);
const slider = ref(null);
const legend = ref(null);
const isResizing = ref(false)
// const selectedPathGroup = ref(null)

onMounted(async () => {
    try {

        // Function to measure rendering time using requestAnimationFrame
        function measureRenderTime(callback) {
            const start = performance.now();

            // Schedule the rendering logic to execute after the current frame
            requestAnimationFrame(() => {
                // Execute the rendering logic
                callback();

                // Schedule another frame to measure the end time
                requestAnimationFrame(() => {
                    const end = performance.now();
                    const renderTime = end - start;
                    console.log(`D3 Render Time: ${renderTime.toFixed(2)} ms`);
                });
            });
        }

        console.time('data');
        const response1 = await axios.get('/data/hcnData.json');
        console.timeEnd('data');
        const data = response1.data;

        const hcn = data.hcn;
        const time = data.time;
        console.log(hcn, time);

        const margin = { top: 400, right: 160, bottom: 60, left: 60 },
            width = 1250 - margin.left - margin.right,
            height = 800 - margin.top - margin.bottom,
            sliderHeight = 50;


        measureRenderTime(() => {
            console.time('start');
            const canvas = d3.select(chart.value)
                .append('canvas')
                .attr('width', width + margin.left + margin.right)
                .attr('height', height + margin.top + margin.bottom)
                .node();

            const xMin = d3.min(time) - 0.5;
            const xMax = d3.max(time);
            const yMin = d3.min(hcn, d => d3.min(d.filter(val => val !== null))) - 50;
            const yMax = d3.max(hcn, d => d3.max(d.filter(val => val !== null))) + 50;

            const ox = d3.scaleLinear()
                .domain([xMin, xMax])
                .range([0, width]);

            const oy = d3.scaleLinear()
                .domain([yMin, yMax])
                .range([height, 0]);

            const x = d3.scaleLinear()
                .domain([xMin, xMax])
                .range([0, width]);

            const y = d3.scaleLinear()
                .domain([yMin, yMax])
                .range([height, 0]);


            {
                // 绘制 overview version1
                const context = canvas.getContext('2d');

                hcn.forEach((lineData, index) => {
                    let sampledData = [];
                    let interval = 1;
                    for (let i = 0; i < lineData.length; i += interval) {
                        sampledData.push(lineData[i]);
                    }

                    const data = sampledData.map((d, i) => ({x: time[i * interval], y: d})).filter(d => d.y !== null);

                    context.beginPath();
                    context.strokeStyle = d3.schemeCategory10[index % 10];
                    context.lineWidth = 1.5;

                    // 使用 d3.line 定义路径
                    const line = d3.line()
                        .x(d => x(d.x))
                        .y(d => y(d.y))
                        .context(context);

                    line(data);

                    context.stroke();
                });

                // 绘制 X 轴网格
                const xTicks = x.ticks();
                context.beginPath();
                xTicks.forEach(d => {
                    context.moveTo(x(d), margin.top - 60);
                    context.lineTo(x(d), height);
                });
                context.strokeStyle = 'rgba(0, 0, 0, 0.3)';
                context.setLineDash([3, 3]);
                context.stroke();

                // 绘制 Y 轴网格
                const yTicks = y.ticks();
                context.beginPath();
                yTicks.forEach(d => {
                    context.moveTo(margin.left, y(d));
                    context.lineTo(width, y(d));
                });
                context.strokeStyle = 'rgba(0, 0, 0, 0.3)';
                context.setLineDash([3, 3]);
                context.stroke();
            }

            console.timeEnd('start')

        })

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

.slider-container {
    width: 80%;
    height: 50px;

    position: absolute;
    top: 350px;
}

.legend-container {
    width: 100%;
    gap: 10px;
    margin-top: 10px;
}

.legend-button {
    background-color: #4CAF50;
    /* 绿色背景 */
    border: none;
    color: white;
    /* 白色文字 */
    padding: 8px 16px;
    /* 调整填充 */
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 12px;
    /* 调整字体大小 */
    margin: 4px 2px;
    cursor: pointer;
    border-radius: 5px;
    /* 圆角 */
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

.focus circle {
    fill: none;
    stroke: steelblue;
}

.zoom {
    cursor: move;
    fill: none;
    pointer-events: all;
}
</style>