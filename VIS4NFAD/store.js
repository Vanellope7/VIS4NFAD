import { createStore } from 'vuex';
import axios from 'axios';

export const store = createStore({
  state: {
    highlightedSegments: [], // 存储高亮段及其异常信息
    selectedSmoothedData: [],
    smoothness: 0.0,
    isProcessing: false,
    progress: 0,
    tableData: [],
  },
  mutations: {
    updateHighlightedSegment(state, { index, type, description }) {
      if (state.highlightedSegments[index]) {
        state.highlightedSegments[index].type = type;
        state.highlightedSegments[index].description = description;
      }
    },
    setHighlightedSegments(state, segments) {
      state.highlightedSegments = segments;
    },
    removeHighlightedSegmentById(state, id) {
      state.highlightedSegments = state.highlightedSegments.filter(segment => segment.id !== id);
    },
    addHighlightedSegment(state, segment) {
      state.highlightedSegments.push(segment);
    },
    removeHighlightedSegment(state, segment) {
      state.highlightedSegments = state.highlightedSegments.filter(s => s.name !== segment.name);
    },
    setSmoothness(state, payload) {
      state.smoothness = payload;
    },
    setIsProcessing(state, status) {
      state.isProcessing = status;
    },
    setProgress(state, progress) {
      state.progress = progress;
    },
    setTableData(state, tableData) {
      state.tableData = tableData;
    },
    clearTableData(state) {
      state.tableData = [];
    },
    updateSelectedSmoothedData(state, data) {
      state.selectedSmoothedData = data;
    },
  },
  actions: {
    fetchData({ commit }) {
      axios.get('http://127.0.0.1:5000/get_table_data')
        .then(response => {
          commit('setTableData', response.data);
        })
        .catch(error => {
          console.error('Error fetching table data:', error);
        });
    },
    updateHighlightedSegment({ commit }, payload) {
      commit('updateHighlightedSegment', payload);
    },
    setHighlightedSegments({ commit }, segments) {
      commit('setHighlightedSegments', segments);
    },
    removeHighlightedSegmentById({ commit }, id) {
      commit('removeHighlightedSegmentById', id);
    },
    addHighlightedSegment({ commit }, segment) {
      commit('addHighlightedSegment', segment);
    },
    removeHighlightedSegment({ commit }, segment) {
      commit('removeHighlightedSegment', segment);
    },
    updateSmoothness({ commit }, smoothness) {
      commit('setSmoothness', smoothness);
    },
    updateSelectedSmoothedData({ commit }, data) {
      commit('updateSelectedSmoothedData', data);
    },
  }
});

export default store;
