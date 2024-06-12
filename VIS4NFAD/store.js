import { createStore } from 'vuex';
import axios from 'axios';

export const store = createStore({
  state: {
    selectedSmoothedData: [],
    smoothness: 0.0,
    isProcessing: false,
    progress: 0,
    tableData: [],
  },
  mutations: {
    setSelectedSmoothedData(state, payload) {
      state.selectedSmoothedData = payload;
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
    updateSelectedSmoothedData({ commit }, data) {
      commit('setSelectedSmoothedData', data);
    },
    updateSmoothness({ commit }, smoothness) {
      commit('setSmoothness', smoothness);
    }
  }
});

export default store;
