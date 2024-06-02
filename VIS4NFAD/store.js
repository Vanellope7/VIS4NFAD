import { createStore } from 'vuex';

export const store = createStore({
    state: {
        selectedSmoothedData: [],
        smoothness: 0.0
    },
    mutations: {
        setSelectedSmoothedData(state, payload) {
            state.selectedSmoothedData = payload;
        },
        setSmoothness(state, payload) {
            state.smoothness = payload;
        }
    },
    actions: {
        updateSelectedSmoothedData({ commit }, data) {
            commit('setSelectedSmoothedData', data);
        },
        updateSmoothness({ commit }, smoothness) {
            commit('setSmoothness', smoothness);
        }
    }
});

export default store;
