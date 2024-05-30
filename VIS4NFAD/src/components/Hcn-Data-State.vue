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
        const response1 = await axios.get('/data/hcnData.json');
        const data = response1.data;
        const response2 = await axios.get('/data/hcnStateData.json');
        const stateData = response2.data;
        let {peaksList, statesList} = stateData;
        const hcn = data.hcn;
        const time = data.time.map(d => d[0]);

        console.log(peaksList, statesList)


        const margin = { top: 60, right: 160, bottom: 60, left: 60 },
            width = 1800 - margin.left - margin.right,
            height = 800 - margin.top - margin.bottom,
            sliderHeight = 50;
        const [rectH, rectW] = [40, width/2];
        const padding = 100;
        const svg = d3.select(chart.value)
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom);

        const chartArea = svg.append("g")
            .attr("clip-path", "url(#clip)")
            .attr("transform", `translate(${rectW + margin.left + padding},${margin.top})`);

        const xMin = d3.min(time);
        const xMax = d3.max(time);
        const x = d3.scaleLinear()
            .domain([xMin, xMax])
            .range([0, rectW]);

        const yMin = d3.min(hcn[0]) - 50;
        const yMax = d3.max(hcn[0]) + 50;
        const y = d3.scaleLinear()
            .domain([yMin, yMax])
            .range([height, 0]);

        // 绘制 overview version2
        const overview2 = svg.append('g')
            .attr('class', 'overviewV2')
            .attr("transform", `translate(${margin.left},${0})`);
        const container = overview2.append('g').attr('class', 'container');
        let rectHP = 10;
        container.append('g').attr('class', 'rectG')
            .selectAll('rect')
            .data(hcn)
            .join('rect')
            .attr('x', 0)
            .attr('y', (d, i) => (rectH+rectHP) * i)
            .attr('width', rectW)
            .attr('height', rectH)
            .attr('stroke', 'none')
            .attr('fill', 'none')
            .on('click', function (e, data) {
                let idx = hcn.indexOf(data);
                const yMin = d3.min(data) - 50;
                const yMax = d3.max(data) + 50;
                console.log('xxx')
                y.domain([yMin, yMax]);
                [data].forEach((lineData, index) => {
                    const path = lineChart.select('path')
                        .datum(lineData.map((d, i) => ({x: time[i], y: d})).filter(d => d.y !== null))
                        .attr("d", d3.line()
                            .x(d => x(d.x))
                            .y(d => y(d.y)));
                })


                // peak line change
                lineChart.selectAll('.segmentLine')
                    .data(peaksList[idx])
                    .join('line')
                    .attr('class', 'segmentLine')
                    .attr("x1", d => x(time[d]))
                    .attr("y1", 0)
                    .attr("x2", d => x(time[d]))
                    .attr("y2", height)
                    .attr("stroke", "black")
                    .attr("stroke-width", 2);


                // outlier and trend change
                lineChartStateG.selectAll('.stateTrendG').remove();
                lineChartStateG.selectAll('.stateTrendG')
                    .data(statesList[idx].map(d => d.trend))
                    .join('g')
                    .attr('class', 'stateTrendG')
                    .append('path')
                    .attr('d', (d, i) => d ? upArrowPath : downArrowPath)
                    .attr('transform', function(d, i) {
                        let rotate = d ? 45 : -45;
                        return `translate(${x(time[peaksList[idx][i]])}, 10) rotate(${rotate})`
                    })
                    .attr('stroke', '#000')

                lineChartStateG.selectAll('.stateOutlierG').remove();
                lineChartStateG.selectAll('.stateOutlierG')
                    .data(statesList[idx].map(t => t.outliers))
                    .join('g')
                    .attr('class', 'stateOutlierG')
                    .selectAll('.outlierCircle')
                    .data(d => d)
                    .join('circle')
                    .attr('class', 'outlierCircle')
                    .attr('r', 5)
                    .attr('cx', function(d, i) {
                        return x(time[d]);
                    })
                    .attr('cy', (d, i) => y(hcn[idx][d]))
                    .attr('fill', (d, i) => {
                        if(d) {
                            return 'red';
                        }
                        else {
                            return 'blue';
                        }
                    })


            })


        const peakG = container.selectAll('.peakG')
            .data(peaksList)
            .join('g')
            .attr('class', 'peakG')
            .attr('idx', (d, i) => i)
            .attr('transform', (d, i) => `translate(0, ${(rectH+rectHP) * i})`);
        peakG.selectAll('.peakSegmentG')
            .data(d => d)
            .join('g')
            .attr('class', 'peakSegmentG')
            .append('rect')
            .attr('x', (d, i) => {
                if(x(time[d]) == null) {
                    console.log('xxx')
                }
                return x(time[d]);
            })
            .attr('y', 0)
            .attr('width', (d, i, a) => {
                if(i === a.length-1) {
                    return 0
                } else {
                    let backX = d3.select(a[i+1]).attr('x');
                    if(backX - x(time[d]) < 0) {
                        console.log('xxx')
                    }
                    return backX - x(time[d]);
                }
            })
            .attr('height', rectH)
            .attr('stroke', '#aaa')
            .attr('fill', 'none');

        // 定义包含竖线的上箭头路径，适配20x20区域
        const upArrowPath = "M 10 0 L 5 8 L 8 8 L 8 20 L 12 20 L 12 8 L 15 8 Z";

        // 定义包含竖线的下箭头路径，适配20x20区域
        const downArrowPath = "M 10 20 L 5 12 L 8 12 L 8 0 L 12 0 L 12 12 L 15 12 Z";



        // draw outlier and trend
        const stateG = container.selectAll('.stateG')
            .data(statesList)
            .join('g')
            .attr('class', 'stateG')
            .attr('idx', (d, i) => i)
            .attr('transform', (d, i) => `translate(0, ${(rectH+rectHP) * i})`);
        stateG.selectAll('.stateTrendG')
            .data(d => d.map(t => t.trend))
            .join('g')
            .attr('class', 'stateTrendG')
            .append('circle')
            .attr('cx', function (d, i) {
                let idx = +d3.select(this.parentNode.parentNode).attr('idx');
                return x((time[peaksList[idx][i]] + time[peaksList[idx][i+1]]) / 2);
            })
            .attr('cy', (d, i) => d? 10 : 30)
            .attr('r', 2)
            .attr('stroke', '#000')

        stateG.selectAll('.stateOutlierG')
            .data(d => d.map(t => t.outliers))
            .join('g')
            .attr('class', 'stateOutlierG')
            .selectAll('.outlierCircle')
            .data(d => d)
            .join('circle')
            .attr('class', 'outlierCircle')
            .attr('r', 5)
            .attr('cx', function(d, i) {
                return x(time[d]);
            })
            .attr('cy', 10+10)
            .attr('fill', (d, i) => {
                if(d) {
                    return 'red';
                }
                else {
                    return 'blue';
                }
            })


        const lineChart = chartArea.append('g')
            .attr('class', 'lineChart');
        lineChart.selectAll('.segmentLine')
            .data(peaksList[0])
            .join('line')
            .attr('class', 'segmentLine')
            .attr("x1", d => x(time[d]))
            .attr("y1", 0)
            .attr("x2", d => x(time[d]))
            .attr("y2", height)
            .attr("stroke", "black")
            .attr("stroke-width", 2);


        [hcn[0]].forEach((lineData, index) => {
            const path = lineChart.append("path")
                .datum(lineData.map((d, i) => ({ x: time[i], y: d })).filter(d => d.y !== null))
                .attr("fill", "none")
                .attr("stroke", d3.schemeCategory10[index % 10])
                .attr("stroke-width", 1.5)
                .attr("class", `line line-${index}`)
                .attr("d", d3.line()
                    .x(d => x(d.x))
                    .y(d => y(d.y)));
        });

        const lineChartStateG = lineChart
            .append('g')
            .attr('class', 'stateG');
        lineChartStateG.selectAll('.stateTrendG')
            .data(statesList[0].map(d => d.trend))
            .join('g')
            .attr('class', 'stateTrendG')
            .append('path')
            .attr('d', (d, i) => d ? upArrowPath : downArrowPath)
            .attr('transform', function(d, i) {
                let idx = +d3.select(this.parentNode.parentNode).attr('idx');
                let rotate = d ? 45 : -45;
                return `translate(${x(time[peaksList[idx][i]])}, 10) rotate(${rotate})`
            })
            .attr('stroke', '#000')

        lineChartStateG.selectAll('.stateOutlierG')
            .data(statesList[0].map(t => t.outliers))
            .join('g')
            .attr('class', 'stateOutlierG')
            .selectAll('.outlierCircle')
            .data(d => d)
            .join('circle')
            .attr('class', 'outlierCircle')
            .attr('r', 5)
            .attr('cx', function(d, i) {
                return x(time[d]);
            })
            .attr('cy', (d, i) => y(hcn[0][d]))
            .attr('fill', (d, i) => {
                if(d) {
                    return 'red';
                }
                else {
                    return 'blue';
                }
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