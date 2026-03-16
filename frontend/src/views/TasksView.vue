<template>
  <div class="page">
    <div class="page-header">
      <h2>扫描任务</h2>
      <el-button type="primary" icon="Plus" @click="openDialog()">创建扫描任务</el-button>
    </div>

    <el-card shadow="never">
      <el-table :data="tasks" v-loading="loading" stripe>
        <el-table-column label="任务名称" prop="task_name" min-width="150" show-overflow-tooltip />
        <el-table-column label="站点" min-width="130" show-overflow-tooltip>
          <template #default="{ row }">{{ row.site_name || row.site }}</template>
        </el-table-column>
        <el-table-column label="扫描类型" width="110">
          <template #default="{ row }">{{ scanTypeLabel(row.scan_type) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="进度" width="140">
          <template #default="{ row }">
            <el-progress
              :percentage="row.progress || 0"
              :status="row.status === 'failed' ? 'exception' : row.status === 'completed' ? 'success' : undefined"
              :stroke-width="8"
            />
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="110">
          <template #default="{ row }">{{ row.created_at?.slice(0, 10) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="210" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending'"
              size="small"
              type="success"
              icon="VideoPlay"
              @click="startTask(row)"
            >启动</el-button>
            <el-button
              v-if="row.status === 'running'"
              size="small"
              type="warning"
              icon="VideoPause"
              @click="cancelTask(row)"
            >取消</el-button>
            <el-button size="small" icon="View" @click="viewTask(row)">详情</el-button>
            <el-button
              v-if="['completed', 'failed', 'cancelled'].includes(row.status)"
              size="small"
              type="danger"
              icon="Delete"
              @click="deleteTask(row)"
            >删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @change="fetchTasks"
        />
      </div>
    </el-card>

    <!-- Create Task Dialog -->
    <el-dialog v-model="dialogVisible" title="创建扫描任务" width="520px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="任务名称" prop="task_name">
          <el-input v-model="form.task_name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="目标站点" prop="site">
          <el-select v-model="form.site" placeholder="请选择站点" style="width: 100%" filterable>
            <el-option v-for="s in allSites" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="扫描类型" prop="scan_type">
          <el-select v-model="form.scan_type" style="width: 100%">
            <el-option label="全面扫描" value="full_scan" />
            <el-option label="快速扫描" value="quick_scan" />
            <el-option label="自定义扫描" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">创建</el-button>
      </template>
    </el-dialog>

    <!-- Detail Drawer -->
    <el-drawer v-model="detailVisible" title="任务详情" size="480px">
      <div v-if="detailTask" class="task-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="任务名称">{{ detailTask.task_name }}</el-descriptions-item>
          <el-descriptions-item label="站点">{{ detailTask.site_name || detailTask.site }}</el-descriptions-item>
          <el-descriptions-item label="扫描类型">{{ scanTypeLabel(detailTask.scan_type) }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="statusType(detailTask.status)">{{ statusLabel(detailTask.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="进度">{{ detailTask.progress || 0 }}%</el-descriptions-item>
          <el-descriptions-item label="漏洞数量">{{ detailTask.vulnerability_count || 0 }}</el-descriptions-item>
          <el-descriptions-item label="描述">{{ detailTask.description || '—' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ detailTask.created_at?.slice(0, 19) }}</el-descriptions-item>
          <el-descriptions-item label="完成时间">{{ detailTask.completed_at?.slice(0, 19) || '—' }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from '@/utils/axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const tasks = ref([])
const allSites = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const detailVisible = ref(false)
const detailTask = ref(null)

const form = reactive({ task_name: '', site: '', scan_type: 'full_scan', description: '' })

const rules = {
  task_name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  site: [{ required: true, message: '请选择站点', trigger: 'change' }],
  scan_type: [{ required: true, message: '请选择扫描类型', trigger: 'change' }],
}

function statusType(s) {
  const map = { pending: 'info', running: 'primary', completed: 'success', failed: 'danger', cancelled: 'warning' }
  return map[s] || 'info'
}

function statusLabel(s) {
  const map = { pending: '待执行', running: '运行中', completed: '已完成', failed: '失败', cancelled: '已取消' }
  return map[s] || s
}

function scanTypeLabel(s) {
  const map = { full_scan: '全面扫描', quick_scan: '快速扫描', custom: '自定义' }
  return map[s] || s
}

async function fetchTasks() {
  loading.value = true
  try {
    const res = await axios.get('/api/scanner/tasks/', {
      params: { page: page.value, page_size: pageSize.value },
    })
    tasks.value = Array.isArray(res.data) ? res.data : res.data.results || []
    total.value = res.data.count || tasks.value.length
  } catch {
    ElMessage.error('加载任务失败')
  } finally {
    loading.value = false
  }
}

async function fetchSites() {
  try {
    const res = await axios.get('/api/scanner/sites/', { params: { page_size: 1000 } })
    allSites.value = Array.isArray(res.data) ? res.data : res.data.results || []
  } catch {}
}

function openDialog() {
  Object.assign(form, { task_name: '', site: '', scan_type: 'full_scan', description: '' })
  dialogVisible.value = true
}

async function submitForm() {
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      await axios.post('/api/scanner/tasks/', form)
      ElMessage.success('创建成功')
      dialogVisible.value = false
      fetchTasks()
    } catch (err) {
      ElMessage.error(err.response?.data?.detail || '创建失败')
    } finally {
      submitting.value = false
    }
  })
}

async function startTask(row) {
  try {
    await axios.post(`/api/scanner/tasks/${row.id}/start/`)
    ElMessage.success('任务已启动')
    fetchTasks()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '启动失败')
  }
}

async function cancelTask(row) {
  try {
    await axios.post(`/api/scanner/tasks/${row.id}/cancel/`)
    ElMessage.success('任务已取消')
    fetchTasks()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '取消失败')
  }
}

async function deleteTask(row) {
  await ElMessageBox.confirm(`确定删除任务"${row.task_name}"？`, '警告', { type: 'warning' })
  try {
    await axios.delete(`/api/scanner/tasks/${row.id}/`)
    ElMessage.success('删除成功')
    fetchTasks()
  } catch {
    ElMessage.error('删除失败')
  }
}

function viewTask(row) {
  detailTask.value = row
  detailVisible.value = true
}

onMounted(() => {
  fetchTasks()
  fetchSites()
})
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: 16px; }
.page-header { display: flex; justify-content: space-between; align-items: center; }
.page-header h2 { margin: 0; font-size: 20px; color: #1a2332; }
.pagination { margin-top: 16px; display: flex; justify-content: flex-end; }
.task-detail { padding: 8px; }
</style>
