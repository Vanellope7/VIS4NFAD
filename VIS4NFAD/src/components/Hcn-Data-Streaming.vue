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



        const margin = { top: 400, right: 160, bottom: 60, left: 60 },
            width = 1250 - margin.left - margin.right,
            height = 800 - margin.top - margin.bottom,
            sliderHeight = 50;

        const svg = d3.select(chart.value)
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom);


        const bgcG = svg.append('g')
            .attr('class', 'bgcG')
            .attr("transform", `translate(${margin.left},${0})`);

        const chartArea = svg.append("g")
            .attr("clip-path", "url(#clip)")
            .attr("transform", `translate(${margin.left},${margin.top})`);


        const hcn = [];
        const time = [];
        const ws = new WebSocket("ws://localhost:8080");

        let isFirst = true;
        ws.onmessage = event => {
            const newData = JSON.parse(event.data);
            newData['data'].forEach((d, i) => {
                hcn[i] === undefined ? (hcn.push([])) : '';
                hcn[i].push(d);
            })
            time.push(newData['time']);

            if(isFirst) {
                isFirst = false;
                DrawGraph(hcn, time);
            }
            else {
                UpdateGraph(hcn, time)
            }
        };

        function DrawGraph(hcn, time) {
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

            const makeXGridlines = () => d3.axisBottom(x).ticks(10);
            const makeYGridlines = () => d3.axisLeft(y).ticks(10);



            {
                // 绘制 overview version1
                const overview1 = svg.append('g')
                    .attr('class', 'overviewV1')
                    .attr("transform", `translate(${margin.left},${0})`);
                hcn.forEach((lineData, index) => {
                    let sampledData = [];
                    let interval = 40;
                    for (let i = 0; i < lineData.length; i += interval) {
                        sampledData.push(lineData[i]);
                    }
                    const path = overview1.append("path")
                        .datum(sampledData.map((d, i) => ({ x: time[i*interval], y: d })).filter(d => d.y !== null))
                        .attr("fill", "none")
                        .attr("stroke", d3.schemeCategory10[index % 10])
                        .attr("stroke-width", 1.5)
                        .attr("class", `line line-${index}`)
                        .attr("d", d3.line()
                            .x(d => x(d.x))
                            .y(d => y(d.y)));
                });

                svg.append("g")
                    .attr("class", "grid-overview-x")
                    .attr("transform", `translate(${margin.left},${margin.top - 60})`)
                    .call(makeXGridlines()
                        .tickSize(-height)
                        .tickFormat(""))
                    .selectAll("line")
                    .style("stroke-dasharray", ("3, 3"))
                    .style("opacity", 0.3);

                svg.append("g")
                    .attr("class", "grid-overview-y")
                    .attr("transform", `translate(${margin.left},${0})`)
                    .call(makeYGridlines()
                        .tickSize(-width)
                        .tickFormat(""))
                    .selectAll("line")
                    .style("stroke-dasharray", ("3, 3"))
                    .style("opacity", 0.3);
            }


            svg.append("g")
                .attr("class", "grid-x")
                .attr("transform", `translate(${margin.left},${margin.top + height})`)
                .call(makeXGridlines()
                    .tickSize(-height)
                    .tickFormat(""))
                .selectAll("line")
                .style("stroke-dasharray", ("3, 3"))
                .style("opacity", 0.3);

            svg.append("g")
                .attr("class", "grid-y")
                .attr("transform", `translate(${margin.left},${margin.top})`)
                .call(makeYGridlines()
                    .tickSize(-width)
                    .tickFormat(""))
                .selectAll("line")
                .style("stroke-dasharray", ("3, 3"))
                .style("opacity", 0.3);

            svg.append("text")
                .attr("transform", `translate(${margin.left + width / 2}, ${margin.top + height + margin.bottom - 20})`)
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

        }
        function UpdateGraph(hcn, time) {
            const xMin = d3.min(time);
            const xMax = d3.max(time);
            const yMin = d3.min(hcn, d => d3.min(d.filter(val => val !== null))) - 50;
            const yMax = d3.max(hcn, d => d3.max(d.filter(val => val !== null))) + 50;

            const x = d3.scaleLinear()
                .domain([xMin, xMax])
                .range([0, width]);

            const y = d3.scaleLinear()
                .domain([yMin, yMax])
                .range([height, 0]);

            const makeXGridlines = () => d3.axisBottom(x).ticks(10);
            const makeYGridlines = () => d3.axisLeft(y).ticks(10);



            {
                // 绘制 overview version1
                const overview1 = svg.select('.overviewV1')
                hcn.forEach((lineData, index) => {

                    const path = overview1.select(`.line-${index}`)
                        .datum(lineData.map((d, i) => ({ x: time[i], y: d })).filter(d => d.y !== null))
                        .attr("d", d3.line()
                            .x(d => x(d.x))
                            .y(d => y(d.y)));
                });


            }


        }

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