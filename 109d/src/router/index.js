/**
 * 路由配置
 */
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/customer'
  },
  {
    path: '/customer',
    name: 'Customer',
    component: () => import('@/views/Customer.vue'),
    meta: { title: '客户界面' }
  },
  {
    path: '/reception',
    name: 'Reception',
    component: () => import('@/views/Reception.vue'),
    meta: { title: '前台管理' }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/Admin.vue'),
    meta: { title: '监控界面' }
  },
  {
    path: '/manager',
    name: 'Manager',
    component: () => import('@/views/Manager.vue'),
    meta: { title: '经理界面' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 酒店中央空调管理系统` : '酒店中央空调管理系统'
  next()
})

export default router

