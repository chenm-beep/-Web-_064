<template>
  <div class="page">
    <div class="page-header">
      <h2>操作日志</h2>
    </div>

    <!-- Filter bar -->
    <el-card shadow="never" class="filter-card">
      <el-row :gutter="12">
        <el-col :span="8">
          <el-input
            v-model="filters.username"
            placeholder="按用户名搜索"
            prefix-icon="User"
            clearable
            @input="fetchLogs"
          />
        </el-col>
        <el-col :span="10">
          <el-input
            v-model="filters.action"
            placeholder="按操作关键词搜索"
            prefix-icon="Search"
            clearable
            @input="fetchLogs"
          />
        </el-col>
        <el-col :span="6">
          <el-button icon="Refresh" @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>
    </el-card>

    <el-card shadow="never">
      <el-table :data="logs" v-loading="loading" stripe>
        <el-table-column label="用户" prop="username" width="110" />
        <el-table-column label="操作" prop="action" min-width="140" show-overflow-tooltip />
        <el-table-column label="目标" prop="target" min-width="130" show-overflow-tooltip />
        <el-table-column label="详情" prop="detail" min-width="200" show-overflow-tooltip />
        <el-table-column label="IP地址" prop="ip_address" width="130" />
        <el-table-column label="时间" width="160">
          <template #default="{ row }">{{ row.created_at?.slice(0, 19)?.replace('T', ' ') }}</template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @change="fetchLogs"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from '@/utils/axios'
import { ElMessage } from 'element-plus'

const logs = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const filters = reactive({ username: '', action: '' })

async function fetchLogs() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filters.username) params.username = filters.username
    if (filters.action) params.action = filters.action
    const res = await axios.get('/api/users/logs/', { params })
    logs.value = Array.isArray(res.data) ? res.data : res.data.results || []
    total.value = res.data.count || logs.value.length
  } catch {
    ElMessage.error('加载日志失败')
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  Object.assign(filters, { username: '', action: '' })
  page.value = 1
  fetchLogs()
}

onMounted(fetchLogs)
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: 16px; }
.page-header { display: flex; justify-content: space-between; align-items: center; }
.page-header h2 { margin: 0; font-size: 20px; color: #1a2332; }
.filter-card :deep(.el-card__body) { padding: 16px; }
.pagination { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
