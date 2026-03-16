<template>
  <div class="page">
    <div class="page-header">
      <h2>端口扫描</h2>
      <el-select
        v-model="selectedTask"
        placeholder="筛选任务"
        clearable
        style="width: 260px"
        @change="fetchPortScans"
      >
        <el-option v-for="t in tasks" :key="t.id" :label="t.task_name" :value="t.id" />
      </el-select>
    </div>

    <el-card shadow="never">
      <el-table :data="portScans" v-loading="loading" stripe>
        <el-table-column label="主机" prop="host" min-width="140" show-overflow-tooltip />
        <el-table-column label="端口" prop="port" width="80" />
        <el-table-column label="协议" prop="protocol" width="80" />
        <el-table-column label="服务" prop="service" width="100" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="stateType(row.state)" size="small">{{ stateLabel(row.state) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Banner" prop="banner" min-width="180" show-overflow-tooltip />
        <el-table-column label="版本" prop="version" width="120" show-overflow-tooltip />
        <el-table-column label="任务" min-width="130" show-overflow-tooltip>
          <template #default="{ row }">{{ row.task_name || row.task }}</template>
        </el-table-column>
        <el-table-column label="扫描时间" width="110">
          <template #default="{ row }">{{ row.scanned_at?.slice(0, 10) || '—' }}</template>
        </el-table-column>
        <el-table-column label="漏洞数" width="80">
          <template #default="{ row }">
            <el-badge
              v-if="row.vulnerability_count > 0"
              :value="row.vulnerability_count"
              type="danger"
            />
            <span v-else>0</span>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @change="fetchPortScans"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '@/utils/axios'
import { ElMessage } from 'element-plus'

const portScans = ref([])
const tasks = ref([])
const loading = ref(false)
const selectedTask = ref(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

function stateType(s) {
  const map = { open: 'success', closed: 'info', filtered: 'warning' }
  return map[s] || 'info'
}

function stateLabel(s) {
  const map = { open: '开放', closed: '关闭', filtered: '过滤' }
  return map[s] || s
}

async function fetchPortScans() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (selectedTask.value) params.task = selectedTask.value
    const res = await axios.get('/api/scanner/port-scans/', { params })
    portScans.value = Array.isArray(res.data) ? res.data : res.data.results || []
    total.value = res.data.count || portScans.value.length
  } catch (error) {
    ElMessage.error('加载端口扫描数据失败')
    console.error('Failed to fetch port scans:', error)
  } finally {
    loading.value = false
  }
}

async function fetchTasks() {
  try {
    const res = await axios.get('/api/scanner/tasks/', { params: { page_size: 200 } })
    tasks.value = Array.isArray(res.data) ? res.data : res.data.results || []
  } catch (error) {
    console.error('Failed to fetch tasks:', error)
  }
}

onMounted(() => {
  fetchTasks()
  fetchPortScans()
})
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: 16px; }
.page-header { display: flex; justify-content: space-between; align-items: center; }
.page-header h2 { margin: 0; font-size: 20px; color: #1a2332; }
.pagination { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
