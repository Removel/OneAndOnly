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
  {
    path: '/test',
    name: 'test',
    component: () => import('@/views/TestView.vue'),
  },
  {
    path: '/diagnostic',
    name: 'diagnostic',
    component: () => import('@/views/DiagnosticView.vue'),
  },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
