import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import HcnDataMulti from "@/components/Hcn-Data-Multi.vue";
import HcnDataStreaming from "@/components/Hcn-Data-Streaming.vue";
import HcnDataState from "@/components/Hcn-Data-State.vue";
import HcnDataMultiCanvas from "@/components/Hcn-Data-Multi-canvas.vue";
import HcnDataStateAvg from "@/components/Hcn-Data-State-avg.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HcnDataState
    },
    {
      path: '/HcnDataStateAvg',
      name: 'HcnDataStateAvg',
      component: HcnDataStateAvg
    },
    {
      path: '/HcnDataMulti',
      name: 'HcnDataMulti',
      component: HcnDataMulti
    },
    {
      path: '/HcnDataMultiCanvas',
      name: 'HcnDataMultiCanvas',
      component: HcnDataMultiCanvas
    },
    {
      path: '/HcnDataStreaming',
      name: 'HcnDataStreaming',
      component: HcnDataStreaming
    },
  ]
})

export default router
