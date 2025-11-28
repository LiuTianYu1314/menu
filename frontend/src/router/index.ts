// router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')  // 指向新的登录组件
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue')
  },
  {
    path: '/root',
    name: 'Root',
    component: () => import('../views/root.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
