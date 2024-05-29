import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import SketchHcn from '@/components/Sketch-Hcn.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    }
    ,{
      path: '/sketch-hcn',
      name: 'sketch-hcn',
      component: SketchHcn
    }
  ]
})

export default router
