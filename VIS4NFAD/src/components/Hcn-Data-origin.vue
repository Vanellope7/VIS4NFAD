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
import { onMounted, ref } from 'vue';

const chart = ref(null);
const slider = ref(null);
const legend = ref(null);

onMounted(async () => {
    try {
        const response = await axios.get('/data/hcnData.json');
        const data = response.data;

        const hcn = data.hcn;
        const time = data.time;

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
        const yMin = d3.min(hcn, d => d3.min(d.filter(val => val !== null))) - 50;
        const yMax = d3.max(hcn, d => d3.max(d.filter(val => val !== null))) + 50;

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

        // {
        //     // 绘制 overview version2
        //     const overview2 = svg.append('g')
        //         .attr('class', 'overviewV2')
        //         .attr("transform", `translate(${margin.left},${0})`);
        //     const colorScale = d3.scaleLinear()
        //         .domain([yMin, 0, yMax])
        //         .range([d3.interpolateBlues(1), d3.interpolateBlues(0), d3.interpolateReds(1)])
        //         .interpolate(d3.interpolateRgb);
        //     for(let t = 0;t<5;t++) {
        //         let sampledData = [];
        //         let interval = 27;
        //         for (let i = 0; i < hcn[t].length; i += interval) {
        //             sampledData.push(hcn[t][i]);
        //         }
        //         const container = overview2.append('g').attr('class', 'container');
        //         container.selectAll('rect')
        //             .data(sampledData)
        //             .join('rect')
        //             .attr('x', (d, i) => width/2 + 20 + i*3)
        //             .attr('y', 20 + 20*t)
        //             .attr('width', 5)
        //             .attr('height', 15)
        //             .attr('fill', (d, i) => colorScale(d));
        //
        //     }
        // }



        // svg.append("g")
        //     .attr("class", "x-axis")
        //     .attr("transform", `translate(${margin.left},${margin.top + height})`)
        //     .call(xAxis);
        //
        // svg.append("g")
        //     .attr("class", "y-axis")
        //     .attr("transform", `translate(${margin.left},${margin.top})`)
        //     .call(yAxis);

        const xSubAxis = d3.axisBottom(x)
            .ticks(100)
            .tickSize(-6)
            .tickFormat('');

        const ySubAxis = d3.axisLeft(y)
            .ticks(50)
            .tickSize(-6)
            .tickFormat('');

        // svg.append("g")
        //     .attr("class", "x-sub-axis")
        //     .attr("transform", `translate(${margin.left},${margin.top + height})`)
        //     .call(xSubAxis);
        //
        // svg.append("g")
        //     .attr("class", "y-sub-axis")
        //     .attr("transform", `translate(${margin.left},${margin.top})`)
        //     .call(ySubAxis);



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

        const focus = chartArea.append("g")
            .attr("class", "focus")
            .style("display", "none");

        focus.append("circle")
            .attr("r", 4.5);

        focus.append("text")
            .attr("x", 9)
            .attr("dy", ".35em");

        svg.append("rect")
            .attr("class", "overlay")
            .attr("width", width)
            .attr("height", height)
            .style("fill", "none")
            .style("pointer-events", "all")
            .attr("transform", `translate(${margin.left},${margin.top})`)
            .on("mouseover", () => focus.style("display", null))
            .on("mouseout", () => focus.style("display", "none"))
            .on("mousemove", mousemove);

        const bisectTime = d3.bisector(d => d).left;

        function mousemove(event) {
            const x0 = x.invert(d3.pointer(event)[0]);
            const i = bisectTime(time, x0, 1);
            const d0 = time[i - 1];
            const d1 = time[i];
            const d = x0 - d0 > d1 - x0 ? d1 : d0;

            focus.attr("transform", `translate(${x(d)},${y(hcn[0][time.indexOf(d)])})`);
            focus.select("text").text(d);
        }

        const paths = [];

        // hcn.forEach((lineData, index) => {
        //     const path = chartArea.append("path")
        //         .datum(lineData.map((d, i) => ({ x: time[i], y: d })).filter(d => d.y !== null))
        //         .attr("fill", "none")
        //         .attr("stroke", d3.schemeCategory10[index % 10])
        //         .attr("stroke-width", 1.5)
        //         .attr("class", `line line-${index}`)
        //         .attr("d", d3.line()
        //             .x(d => x(d.x))
        //             .y(d => y(d.y)));
        //
        //     paths.push(path);
        // });

        // 添加全选和清空按钮
        const legendContainer = d3.select(legend.value)
            .append('div')
            .style('position', 'absolute')
            .style('left', `${width + margin.left + 10}px`)
            .style('top', `${margin.top + hcn.length * 20 + 10}px`)
            .style('display', 'flex')
            .style('gap', '10px')
            .style('align-items', 'center'); // 垂直居中对齐

        // 获取图例复选框的右边界
        const legendRightBoundary = width + margin.left + 160;

        // 将按钮右边界与图例对齐
        legendContainer.style('left', `${legendRightBoundary - legendContainer.node().getBoundingClientRect().width}px`);

        legendContainer.append('button')
            .text('全选')
            .attr('class', 'legend-button')
            .style('font-size', '12px') // 调整字体大小
            .on('click', () => {
                d3.selectAll('input[type=checkbox]').property('checked', true);
                d3.selectAll('.line').style('display', null);
            });

        legendContainer.append('button')
            .text('清空')
            .attr('class', 'legend-button')
            .style('font-size', '12px') // 调整字体大小
            .on('click', () => {
                d3.selectAll('input[type=checkbox]').property('checked', false);
                d3.selectAll('.line').style('display', 'none');
            });


        const zoom = d3.zoom()
            .scaleExtent([1, 10])
            .translateExtent([[0, 0], [width, height]])
            .extent([[0, 0], [width, height]])
            .on("zoom", zoomed);

        svg.append("rect")
            .attr("class", "zoom")
            .attr("width", width)
            .attr("height", height)
            .style("fill", "none")
            .style("pointer-events", "all")
            .attr("transform", `translate(${margin.left},${margin.top})`)
            .call(zoom);

        function zoomed(event) {
            const newX = event.transform.rescaleX(x);

            svg.selectAll(".x-axis").call(d3.axisBottom(newX).ticks(10));
            svg.selectAll(".x-sub-axis").call(d3.axisBottom(newX).ticks(100).tickSize(-6).tickFormat(''));

            paths.forEach((path, index) => {
                if (d3.select(`#checkbox-${index}`).property("checked")) {
                    path.attr("d", d3.line()
                        .x(d => newX(d.x))
                        .y(d => y(d.y)));
                }
            });

            svg.selectAll(".grid-x")
                .call(makeXGridlines().scale(newX).tickSize(-height).tickFormat(""))
                .selectAll("line")
                .style("stroke-dasharray", ("3, 3"))
                .style("opacity", 0.3);

            // 更新滑块
            d3.select(slider.value).call(brush.move, newX.range().map(event.transform.invertX, event.transform));
        }

        // 创建滑块
        const sliderSvg = svg
            .append("g")
            .attr("transform", `translate(${margin.left},${sliderHeight/2})`);

        const xSlider = d3.scaleLinear()
            .domain([xMin, xMax])
            .range([0, width]);

        // sliderSvg.append("g")
        //     .attr("class", "x-axis")
        //     .attr("transform", `translate(0,${sliderHeight / 4})`)
        //     .call(d3.axisBottom(xSlider).ticks(10).tickFormat(d3.format(".1f")));
        let range = JSON.parse(JSON.stringify(x.range()));
        range[1] = range[1] / 2

        let x2 = range[1] - range[0];



        const brush = d3.brushX()
            .extent([[0, 0], [width, height-25]])
            .on('start', debounce(brushStart, 200))
            .on('brush', brushing)
            .on("end", brushed);



        sliderSvg.append("g")
            .attr("class", "brush")
            .call(brush)
            .call(brush.move, null);

        let gapPadding = 60;
        sliderSvg.selectAll('.brush .selection')
            .attr('fill', 'none').attr('stroke', 'none')


        let isResizing = false;
        let selectedRect = null;
        function brushStart(event) {
            if(!event.selection) return;
            if (event.sourceEvent.target.classList.contains('overlay')) {
                isResizing = false;
                selectedRect = null;
            } else {
                isResizing = true;
                selectedRect = event.sourceEvent.target.parentNode;
            }
            if(!isResizing) {
                const bgcRect = bgcG.append('rect')

                    .attr('x', 0)
                    .attr('width', 0)
                    .attr('y', 0)
                    .attr('height', height)
                    .attr('fill', '#cdc9e4')
                    .attr('fill-opacity', 0.3)

                const bgcPath = bgcG.append('path')
                    .attr('fill', '#cdc9e4')
                    .attr('fill-opacity', 0.3)
                    .attr('stroke', '#ccc');
            }
        }

        function brushing(event) {
            if(!event.selection) return;


            if (event.sourceEvent && event.sourceEvent.type === "zoom") return; // 忽略 zoom 事件触发的 brush 事件

            const selection = event.selection || xSlider.range();
            const newX = selection.map(xSlider.invert, xSlider);

            const bgcRect = svg.select('.bgcG rect:last-of-type');
            const bgcPath = svg.select('.bgcG path:last-of-type');

            bgcRect.attr('x', selection[0]).attr('width', selection[1] - selection[0])
            bgcPath.attr('d', `M${selection[0]} ${height} L${selection[1]} ${height} Q${selection[1]+(width-selection[1])/4} ${height+3*gapPadding/4} ${width} ${height+gapPadding}
                L${0} ${height+gapPadding} Q${3*selection[0]/4} ${height+3*gapPadding/4} ${selection[0]} ${height}
            `)

            x.domain(newX);
            svg.selectAll(".x-axis").call(d3.axisBottom(x).ticks(10));
            svg.selectAll(".x-sub-axis").call(d3.axisBottom(x).ticks(100).tickSize(-6).tickFormat(''));

            paths.forEach((path, index) => {
                path.attr("d", d3.line()
                    .x(d => x(d.x))
                    .y(d => y(d.y)));
            });

            svg.selectAll(".grid-x")
                .call(makeXGridlines().scale(x).tickSize(-height).tickFormat(""))
                .selectAll("line")
                .style("stroke-dasharray", ("3, 3"))
                .style("opacity", 0.3);
        }

        function brushed(event) {


        }

        // 防抖函数
        function debounce(func, wait) {
            let timeout;
            return function(...args) {
                clearTimeout(timeout);
                timeout = setTimeout(() => func.apply(this, args), wait);
            };
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