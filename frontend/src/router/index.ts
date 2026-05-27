import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
  },
  {
    path: '/help',
    name: 'help',
    component: () => import('@/views/HelpView.vue'),
  },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
