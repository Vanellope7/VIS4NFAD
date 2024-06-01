// store.js
import { createStore } from 'vuex';

export const store = createStore({
    state: {
        selectedSmoothedData: []
    },
    mutations: {
        setSelectedSmoothedData(state, payload) {
            state.selectedSmoothedData = payload;
        }
    },
    actions: {
        updateSelectedSmoothedData({ commit }, data) {
            commit('setSelectedSmoothedData', data);
        }
    }
});

export default store;
