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
    </div>
</template>

<script setup>
import * as d3 from 'd3';
import axios from 'axios';
import { onMounted, ref, watch } from 'vue';
import { useStore } from 'vuex';

const chart = ref(null);
const overview = ref(null);
const legend = ref(null);
const smoothness = ref(0.0);

const store = useStore();

onMounted(async () => {
    try {
        const response = await axios.get('/data/hcnData.json');
        const data = response.data;

        const hcn = data.hcn;
        const time = data.time;

        const margin = { top: 10, right: 160, bottom: 30, left: 60 },
            width = 1250 - margin.left - margin.right,
            height = 600 - margin.top - margin.bottom,
            overviewHeight = 50;

        const svg = d3.select(chart.value)
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom);

        const clip = svg.append("defs").append("svg:clipPath")
            .attr("id", "clip")
            .append("svg:rect")
            .attr("width", width)
            .attr("height", height)
            .attr("x", 0)
            .attr("y", 0);

        const chartArea = svg.append("g")
            .attr("clip-path", "url(#clip)")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        const xMin = d3.min(time) - 0.5;
        const xMax = d3.max(time);
        const yMin = d3.min(hcn, d => d3.min(d.filter(val => val !== null))) - 25;
        const yMax = d3.max(hcn, d => d3.max(d.filter(val => val !== null))) + 25;

        const x = d3.scaleLinear()
            .domain([xMin, xMax])
            .range([0, width]);

        const y = d3.scaleLinear()
            .domain([yMin, yMax])
            .range([height, 0]);

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
            .attr("class", "x-axis")
            .attr("transform", `translate(${margin.left},${margin.top + height})`)
            .call(xAxis);

        svg.append("g")
            .attr("class", "y-axis")
            .attr("transform", `translate(${margin.left},${margin.top})`)
            .call(yAxis);

        const makeXGridlines = () => d3.axisBottom(x).ticks(10);
        const makeYGridlines = () => d3.axisLeft(y).ticks(10);

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

        const paths = [];

        const lineGenerator = d3.line()
            .x(d => x(d.x))
            .y(d => y(d.y))
            .curve(d3.curveBasis);

        hcn.forEach((lineData, index) => {
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

            paths.push({ originalPath, smoothedPath });

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
                .text(`${4043 + index}/hcn_ne001`);

            // 创建复选框
            d3.select(chart.value).append('div')
                .style('position', 'absolute')
                .style('left', `${width + margin.left + 110}px`)
                .style('top', `${margin.top + index * 20 + 18}px`)
                .html(`<input type="checkbox" checked="checked" id="checkbox-${index}" />`)
                .on('change', function () {
                    const checked = d3.select(`#checkbox-${index}`).property('checked');
                    d3.select(`.original-line-${index}`).style('display', checked ? null : 'none');
                    d3.select(`.smoothed-line-${index}`).style('display', checked ? null : 'none');
                    updateStore();
                });
        });

        // 添加全选和清空按钮
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
            .style('font-size', '12px')
            .on('click', () => {
                d3.selectAll('input[type=checkbox]').property('checked', true);
                d3.selectAll('.original-line').style('display', null);
                d3.selectAll('.smoothed-line').style('display', null);
                updateStore();
            });

        legendContainer.append('button')
            .text('清空')
            .attr('class', 'legend-button')
            .style('font-size', '12px')
            .on('click', () => {
                d3.selectAll('input[type=checkbox]').property('checked', false);
                d3.selectAll('.original-line').style('display', 'none');
                d3.selectAll('.smoothed-line').style('display', 'none');
                updateStore();
            });

        // Overview chart
        const overviewSvg = d3.select(overview.value)
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", overviewHeight + margin.top + margin.bottom)
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        const xOverview = d3.scaleLinear()
            .domain([xMin, xMax])
            .range([0, width]);

        const yOverview = d3.scaleLinear()
            .domain([yMin, yMax])
            .range([overviewHeight, 0]);

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
        }

        watch(smoothness, () => {
            paths.forEach((path, index) => {
                if (d3.select(`#checkbox-${index}`).property("checked")) {
                    const lineData = hcn[index].map((d, i) => ({ x: time[i], y: d })).filter(d => d.y !== null);
                    const interpolatedData = interpolateData(lineData, smoothness.value);
                    path.smoothedPath.datum(interpolatedData).attr("d", lineGenerator.curve(d3.curveBasis));
                    path.originalPath.attr("opacity", 0.5 - 0.3 * smoothness.value); // Adjust transparency
                    path.smoothedPath.attr("opacity", 1);
                }
            });
            updateStore();
        });

        function updateStore() {
            const selectedData = [];
            paths.forEach((path, index) => {
                if (d3.select(`#checkbox-${index}`).property("checked")) {
                    const data = path.smoothedPath.datum();
                    selectedData.push({ index, data });
                }
            });
            store.dispatch('updateSelectedSmoothedData', selectedData);
        }

        function interpolateData(data, t) {
            if (t === 0) {
                return data;
            } else {
                const steps = Math.ceil(t * 200); // 增加平滑步数
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
</style>
