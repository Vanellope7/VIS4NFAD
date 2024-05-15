<template>
    <div ref="chartContainer" class="chart-container">
        <div ref="chart"></div>
    </div>
</template>

<script setup>
import * as d3 from 'd3';
import axios from 'axios';
import { onMounted, ref } from 'vue';

const chart = ref(null);

onMounted(async () => {
    const response = await axios.get('/data/hcnData.json'); // 请确保路径正确
    const data = response.data;

    const hcn = data.hcn;
    const time = data.time;

    const margin = { top: 20, right: 120, bottom: 40, left: 60 },
        width = 1250 - margin.left - margin.right,
        height = 600 - margin.top - margin.bottom;

    const svg = d3.select(chart.value)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // 计算所有数据的最小值和最大值
    const xMin = d3.min(time) - 0.5;
    const xMax = d3.max(time);
    const yMin = d3.min(hcn, d => d3.min(d.filter(val => val !== null))) - 50;
    const yMax = d3.max(hcn, d => d3.max(d.filter(val => val !== null))) + 50;

    const x = d3.scaleLinear()
        .domain([xMin, xMax])
        .range([0, width]);

    const y = d3.scaleLinear()
        .domain([yMin, yMax])
        .range([height, 0]);

    // 添加次刻度线
    const xAxis = d3.axisBottom(x)
        .ticks(10)
        .tickSizeOuter(0)
        .tickPadding(10)
        .tickFormat(d3.format(".1f"));

    const yAxis = d3.axisLeft(y)
        .ticks(10)
        .tickSizeOuter(0)
        .tickPadding(10)
        .tickFormat(d3.format("d"));

    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(xAxis);

    svg.append("g")
        .call(yAxis);

    // 添加次刻度线
    const xSubAxis = d3.axisBottom(x)
        .ticks(100)
        .tickSize(-6)
        .tickFormat('');

    const ySubAxis = d3.axisLeft(y)
        .ticks(50)
        .tickSize(-6)
        .tickFormat('');

    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(xSubAxis);

    svg.append("g")
        .call(ySubAxis);

    // 添加网格线
    const makeXGridlines = () => d3.axisBottom(x).ticks(10);
    const makeYGridlines = () => d3.axisLeft(y).ticks(10);

    svg.append("g")
        .attr("class", "grid")
        .attr("transform", `translate(0,${height})`)
        .call(makeXGridlines()
            .tickSize(-height)
            .tickFormat(""))
        .selectAll("line")
        .style("stroke-dasharray", ("3, 3"))
        .style("opacity", 0.3); // 设置网格线为虚线

    svg.append("g")
        .attr("class", "grid")
        .call(makeYGridlines()
            .tickSize(-width)
            .tickFormat(""))
        .selectAll("line")
        .style("stroke-dasharray", ("3, 3"))
        .style("opacity", 0.3); // 设置网格线为虚线

    hcn.forEach((lineData, index) => {
        svg.append("path")
            .datum(lineData.map((d, i) => ({ x: time[i], y: d })).filter(d => d.y !== null))
            .attr("fill", "none")
            .attr("stroke", d3.schemeCategory10[index % 10])
            .attr("stroke-width", 1.5)
            .attr("d", d3.line()
                .x(d => x(d.x))
                .y(d => y(d.y)));

        // 添加图例线条
        svg.append("line")
            .attr("x1", width + 10)
            .attr("y1", index * 20 + 5)
            .attr("x2", width + 30)
            .attr("y2", index * 20 + 5)
            .attr("stroke", d3.schemeCategory10[index % 10])
            .attr("stroke-width", 5);

        // 添加图例文本
        svg.append("text")
            .attr("x", width + 35)
            .attr("y", index * 20 + 10)
            .attr("fill", "black")
            .style("font-size", "10px")
            .text(`${4043 + index}/hcn_ne001`);

        // 添加 x 轴标签
        svg.append("text")
            .attr("transform", `translate(${width / 2}, ${height + margin.bottom})`)
            .attr("text-anchor", "middle")
            .style("font-size", "16px")
            .text("Time(s)");

        // 添加 y 轴标签
        svg.append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", 0 - margin.left + 15)
            .attr("x", 0 - (height / 2))
            .attr("text-anchor", "middle")
            .style("font-size", "16px")
            .text("10^7/m^2");
    });
});
</script>

<style scoped>
.chart-container {
    width: 100%;
    height: 100%;
}

svg {
    font: 10px sans-serif;
}

.axis path,
.axis line {
    fill: none;
    shape-rendering: crispEdges;
}
</style>
