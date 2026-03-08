import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/components/Layout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Layout,
      redirect: '/dashboard',
      children: [
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('@/views/Dashboard.vue'),
          meta: { title: '数据大盘' }
        },
        {
          path: 'market',
          name: 'market',
          component: () => import('@/views/Market.vue'),
          meta: { title: '行情数据' }
        },
        {
          path: 'trades',
          name: 'trades',
          component: () => import('@/views/Trades.vue'),
          meta: { title: '交易分析' }
        },
        {
          path: 'onchain',
          name: 'onchain',
          component: () => import('@/views/OnChain.vue'),
          meta: { title: '链上数据' }
        },
        {
          path: 'alerts',
          name: 'alerts',
          component: () => import('@/views/Alerts.vue'),
          meta: { title: '告警管理' }
        },
        {
          path: 'analytics',
          name: 'analytics',
          component: () => import('@/views/Analytics.vue'),
          meta: { title: '数据分析' }
        },
      ]
    },
  ],
})

export default router
