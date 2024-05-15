<template>
    <div ref="chartContainer" class="chart-container">
      <div ref="chart"></div>
      <div ref="slider" class="slider-container"></div>
    </div>
  </template>
  
  <script setup>
  import * as d3 from 'd3';
  import axios from 'axios';
  import { onMounted, ref } from 'vue';
  
  const chart = ref(null);
  const slider = ref(null);
  
  onMounted(async () => {
    try {
      const response = await axios.get('/data/hcnData.json');
      const data = response.data;
  
      const hcn = data.hcn;
      const time = data.time;
  
      const margin = { top: 20, right: 120, bottom: 60, left: 60 },
        width = 1250 - margin.left - margin.right,
        height = 600 - margin.top - margin.bottom,
        sliderHeight = 50;
  
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
  
      svg.append("g")
        .attr("class", "x-axis")
        .attr("transform", `translate(${margin.left},${margin.top + height})`)
        .call(xAxis);
  
      svg.append("g")
        .attr("class", "y-axis")
        .attr("transform", `translate(${margin.left},${margin.top})`)
        .call(yAxis);
  
      const xSubAxis = d3.axisBottom(x)
        .ticks(100)
        .tickSize(-6)
        .tickFormat('');
  
      const ySubAxis = d3.axisLeft(y)
        .ticks(50)
        .tickSize(-6)
        .tickFormat('');
  
      svg.append("g")
        .attr("class", "x-sub-axis")
        .attr("transform", `translate(${margin.left},${margin.top + height})`)
        .call(xSubAxis);
  
      svg.append("g")
        .attr("class", "y-sub-axis")
        .attr("transform", `translate(${margin.left},${margin.top})`)
        .call(ySubAxis);
  
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
        .attr("transform", `translate(${margin.left + width / 2}, ${margin.top + height + margin.bottom - 10})`)
        .attr("text-anchor", "middle")
        .style("font-size", "16px")
        .text("Time(s)");
  
      svg.append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", margin.left - 40)
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
  
      hcn.forEach((lineData, index) => {
        chartArea.append("path")
          .datum(lineData.map((d, i) => ({ x: time[i], y: d })).filter(d => d.y !== null))
          .attr("fill", "none")
          .attr("stroke", d3.schemeCategory10[index % 10])
          .attr("stroke-width", 1.5)
          .attr("class", "line")
          .attr("d", d3.line()
            .x(d => x(d.x))
            .y(d => y(d.y)));
  
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
          .attr("y", index * 20 + 10)
          .attr("fill", "black")
          .style("font-size", "10px")
          .attr("transform", `translate(${margin.left},${margin.top})`)
          .text(`${4043 + index}/hcn_ne001`);
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
  
        chartArea.selectAll(".line")
          .attr("d", d3.line()
            .x(d => newX(d.x))
            .y(d => y(d.y)));
  
        svg.selectAll(".grid-x")
          .call(makeXGridlines().scale(newX).tickSize(-height).tickFormat(""))
          .selectAll("line")
          .style("stroke-dasharray", ("3, 3"))
          .style("opacity", 0.3);
  
        // 更新滑块
        d3.select(slider.current).call(brush.move, newX.range().map(event.transform.invertX, event.transform));
      }
  
      // 创建滑块
      const sliderSvg = d3.select(slider.value)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", sliderHeight)
        .append("g")
        .attr("transform", `translate(${margin.left},${sliderHeight / 4})`);
  
      const xSlider = d3.scaleLinear()
        .domain([xMin, xMax])
        .range([0, width]);
  
      sliderSvg.append("g")
        .attr("class", "x-axis")
        .attr("transform", `translate(0,${sliderHeight / 4})`)
        .call(d3.axisBottom(xSlider).ticks(10).tickFormat(d3.format(".1f")));
  
      const brush = d3.brushX()
        .extent([[0, 0], [width, sliderHeight / 2]])
        .on("brush end", brushed);
  
      sliderSvg.append("g")
        .attr("class", "brush")
        .call(brush)
        .call(brush.move, x.range());
  
      function brushed(event) {
        if (event.sourceEvent && event.sourceEvent.type === "zoom") return; // 忽略 zoom 事件触发的 brush 事件
  
        const selection = event.selection || xSlider.range();
        const newX = selection.map(xSlider.invert, xSlider);
  
        x.domain(newX);
        svg.selectAll(".x-axis").call(d3.axisBottom(x).ticks(10));
        svg.selectAll(".x-sub-axis").call(d3.axisBottom(x).ticks(100).tickSize(-6).tickFormat(''));
  
        chartArea.selectAll(".line")
          .attr("d", d3.line()
            .x(d => x(d.x))
            .y(d => y(d.y)));
  
        svg.selectAll(".grid-x")
          .call(makeXGridlines().scale(x).tickSize(-height).tickFormat(""))
          .selectAll("line")
          .style("stroke-dasharray", ("3, 3"))
          .style("opacity", 0.3);
  
        svg.call(zoom.transform, d3.zoomIdentity
          .scale(width / (selection[1] - selection[0]))
          .translate(-selection[0], 0));
      }
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  });
  </script>
  
  <style scoped>
  .chart-container {
    width: 100%;
    height: 100%;
  }
  
  .slider-container {
    width: 100%;
    height: 50px;
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
  