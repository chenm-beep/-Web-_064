import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'
import LoginView from '@/views/LoginView.vue'
import DashboardView from '@/views/DashboardView.vue'
import SitesView from '@/views/SitesView.vue'
import TasksView from '@/views/TasksView.vue'
import VulnerabilitiesView from '@/views/VulnerabilitiesView.vue'
import PortScansView from '@/views/PortScansView.vue'
import PocPluginsView from '@/views/PocPluginsView.vue'
import ScanRulesView from '@/views/ScanRulesView.vue'
import UsersView from '@/views/UsersView.vue'
import LogsView from '@/views/LogsView.vue'

const routes = [
  {
    path: '/login',
    component: LoginView,
  },
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', component: DashboardView },
      { path: 'sites', component: SitesView },
      { path: 'tasks', component: TasksView },
      { path: 'vulnerabilities', component: VulnerabilitiesView },
      { path: 'port-scans', component: PortScansView },
      { path: 'poc-plugins', component: PocPluginsView, meta: { requiresAdmin: true } },
      { path: 'scan-rules', component: ScanRulesView, meta: { requiresAdmin: true } },
      { path: 'users', component: UsersView, meta: { requiresAdmin: true } },
      { path: 'logs', component: LogsView, meta: { requiresAdmin: true } },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || 'null')

  if (to.meta.requiresAuth && !token) {
    return next('/login')
  }

  if (to.meta.requiresAdmin && user?.role !== 'admin') {
    return next('/dashboard')
  }

  if (to.path === '/login' && token) {
    return next('/dashboard')
  }

  next()
})

export default router
