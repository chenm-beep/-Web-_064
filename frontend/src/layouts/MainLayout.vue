<template>
  <div class="layout-wrapper">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ collapsed: isCollapsed }">
      <div class="sidebar-logo">
        <span class="logo-icon">🛡️</span>
        <span v-if="!isCollapsed" class="logo-text">漏洞扫描系统</span>
      </div>
      <el-menu
        :default-active="activeRoute"
        background-color="#1a2332"
        text-color="#c8d1d9"
        active-text-color="#ffffff"
        :collapse="isCollapsed"
        :collapse-transition="false"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>总览</template>
        </el-menu-item>
        <el-menu-item index="/sites">
          <el-icon><Monitor /></el-icon>
          <template #title>资产管理</template>
        </el-menu-item>
        <el-menu-item index="/tasks">
          <el-icon><Search /></el-icon>
          <template #title>扫描任务</template>
        </el-menu-item>
        <el-menu-item index="/vulnerabilities">
          <el-icon><Warning /></el-icon>
          <template #title>漏洞报告</template>
        </el-menu-item>
        <el-menu-item index="/port-scans">
          <el-icon><Share /></el-icon>
          <template #title>端口扫描</template>
        </el-menu-item>

        <template v-if="isAdmin">
          <div class="menu-divider">
            <span v-if="!isCollapsed">管理功能</span>
          </div>
          <el-menu-item index="/poc-plugins">
            <el-icon><Code /></el-icon>
            <template #title>POC插件库</template>
          </el-menu-item>
          <el-menu-item index="/scan-rules">
            <el-icon><List /></el-icon>
            <template #title>扫描规则</template>
          </el-menu-item>
          <el-menu-item index="/users">
            <el-icon><User /></el-icon>
            <template #title>用户管理</template>
          </el-menu-item>
          <el-menu-item index="/logs">
            <el-icon><Document /></el-icon>
            <template #title>操作日志</template>
          </el-menu-item>
        </template>
      </el-menu>
    </aside>

    <!-- Main content -->
    <div class="main-wrapper">
      <!-- Header -->
      <header class="main-header">
        <div class="header-left">
          <el-button
            :icon="isCollapsed ? 'Expand' : 'Fold'"
            text
            size="large"
            @click="isCollapsed = !isCollapsed"
          />
          <span class="header-title">🛡️ 智能漏洞扫描系统</span>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" style="background:#409EFF">
                {{ userInitial }}
              </el-avatar>
              <span class="username">{{ authStore.user?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon> 个人资料
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon> 退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- Page content -->
      <main class="main-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isCollapsed = ref(false)
const isAdmin = computed(() => authStore.isAdmin)
const activeRoute = computed(() => route.path)
const userInitial = computed(() =>
  (authStore.user?.username || 'U')[0].toUpperCase()
)

async function handleCommand(cmd) {
  if (cmd === 'logout') {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }).catch(() => {})

    await authStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.layout-wrapper {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  width: 220px;
  min-width: 220px;
  background-color: #1a2332;
  display: flex;
  flex-direction: column;
  transition: width 0.3s, min-width 0.3s;
  overflow: hidden;
}

.sidebar.collapsed {
  width: 64px;
  min-width: 64px;
}

.sidebar-logo {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  gap: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  flex-shrink: 0;
}

.logo-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.logo-text {
  color: #ffffff;
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
}

.sidebar :deep(.el-menu) {
  border-right: none;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

.sidebar :deep(.el-menu-item.is-active) {
  background-color: #409eff !important;
}

.sidebar :deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.08) !important;
}

.menu-divider {
  padding: 12px 16px 4px;
  font-size: 11px;
  color: rgba(200, 209, 217, 0.5);
  text-transform: uppercase;
  letter-spacing: 1px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  margin-top: 8px;
  white-space: nowrap;
  overflow: hidden;
  min-height: 32px;
}

.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: #f0f2f5;
}

.main-header {
  height: 60px;
  background: #ffffff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  flex-shrink: 0;
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a2332;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #333;
}

.username {
  font-size: 14px;
  font-weight: 500;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}
</style>
