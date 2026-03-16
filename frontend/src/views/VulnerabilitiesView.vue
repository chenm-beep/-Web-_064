<template>
  <div class="page">
    <div class="page-header">
      <h2>漏洞报告</h2>
      <el-button type="success" icon="Download" @click="exportReport">导出报告</el-button>
    </div>

    <!-- Filter bar -->
    <el-card shadow="never" class="filter-card">
      <el-row :gutter="12">
        <el-col :span="5">
          <el-select v-model="filters.severity" placeholder="严重程度" clearable @change="fetchVulns">
            <el-option label="严重" value="critical" />
            <el-option label="高危" value="high" />
            <el-option label="中危" value="medium" />
            <el-option label="低危" value="low" />
            <el-option label="信息" value="info" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-select v-model="filters.vuln_type" placeholder="漏洞类型" clearable @change="fetchVulns">
            <el-option label="SQL注入" value="sql_injection" />
            <el-option label="XSS" value="xss" />
            <el-option label="命令注入" value="command_injection" />
            <el-option label="路径遍历" value="path_traversal" />
            <el-option label="CSRF" value="csrf" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-select v-model="filters.status" placeholder="状态" clearable @change="fetchVulns">
            <el-option label="待处理" value="open" />
            <el-option label="已修复" value="fixed" />
            <el-option label="已忽略" value="ignored" />
            <el-option label="误报" value="false_positive" />
          </el-select>
        </el-col>
        <el-col :span="9">
          <el-input
            v-model="filters.search"
            placeholder="搜索漏洞名称"
            prefix-icon="Search"
            clearable
            @input="fetchVulns"
          />
        </el-col>
      </el-row>
    </el-card>

    <el-card shadow="never">
      <el-table :data="vulns" v-loading="loading" stripe>
        <el-table-column label="漏洞名称" prop="name" min-width="180" show-overflow-tooltip />
        <el-table-column label="严重程度" width="100">
          <template #default="{ row }">
            <el-tag :type="severityType(row.severity)" size="small">
              {{ severityLabel(row.severity) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="120">
          <template #default="{ row }">{{ row.vuln_type }}</template>
        </el-table-column>
        <el-table-column label="站点" min-width="130" show-overflow-tooltip>
          <template #default="{ row }">{{ row.site_name || row.site }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="vulnStatusType(row.status)" size="small">
              {{ vulnStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="发现时间" width="110">
          <template #default="{ row }">{{ formatDate(row.discovered_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="170" fixed="right">
          <template #default="{ row }">
            <el-button size="small" icon="View" @click="viewDetail(row)">详情</el-button>
            <el-dropdown size="small" @command="(cmd) => updateStatus(row, cmd)">
              <el-button size="small" icon="Edit">状态</el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="open">待处理</el-dropdown-item>
                  <el-dropdown-item command="fixed">已修复</el-dropdown-item>
                  <el-dropdown-item command="ignored">已忽略</el-dropdown-item>
                  <el-dropdown-item command="false_positive">误报</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @change="fetchVulns"
        />
      </div>
    </el-card>

    <!-- Detail Drawer -->
    <el-drawer v-model="detailVisible" title="漏洞详情" size="560px">
      <div v-if="detailVuln" class="detail-content">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="漏洞名称">{{ detailVuln.name }}</el-descriptions-item>
          <el-descriptions-item label="严重程度">
            <el-tag :type="severityType(detailVuln.severity)">{{ severityLabel(detailVuln.severity) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="漏洞类型">{{ detailVuln.vuln_type }}</el-descriptions-item>
          <el-descriptions-item label="站点">{{ detailVuln.site_name || detailVuln.site }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="vulnStatusType(detailVuln.status)">{{ vulnStatusLabel(detailVuln.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="URL">{{ detailVuln.url || '—' }}</el-descriptions-item>
          <el-descriptions-item label="参数">{{ detailVuln.parameter || '—' }}</el-descriptions-item>
          <el-descriptions-item label="发现时间">{{ detailVuln.discovered_at?.slice(0, 19) }}</el-descriptions-item>
        </el-descriptions>
        <div v-if="detailVuln.description" class="detail-section">
          <h4>漏洞描述</h4>
          <p>{{ detailVuln.description }}</p>
        </div>
        <div v-if="detailVuln.proof" class="detail-section">
          <h4>漏洞证明</h4>
          <pre class="code-block">{{ detailVuln.proof }}</pre>
        </div>
        <div v-if="detailVuln.solution" class="detail-section">
          <h4>修复建议</h4>
          <p>{{ detailVuln.solution }}</p>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { formatDate } from '@/utils/format'
import { ref, reactive, onMounted } from 'vue'
import axios from '@/utils/axios'
import { ElMessage } from 'element-plus'

const vulns = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const detailVisible = ref(false)
const detailVuln = ref(null)

const filters = reactive({ severity: '', vuln_type: '', status: '', search: '' })

function severityType(s) {
  const map = { critical: 'danger', high: 'warning', medium: '', low: 'success', info: 'info' }
  return map[s] || 'info'
}

function severityLabel(s) {
  const map = { critical: '严重', high: '高危', medium: '中危', low: '低危', info: '信息' }
  return map[s] || s
}

function vulnStatusType(s) {
  const map = { open: 'danger', fixed: 'success', ignored: 'info', false_positive: 'warning' }
  return map[s] || 'info'
}

function vulnStatusLabel(s) {
  const map = { open: '待处理', fixed: '已修复', ignored: '已忽略', false_positive: '误报' }
  return map[s] || s
}

async function fetchVulns() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
      ...Object.fromEntries(Object.entries(filters).filter(([, v]) => v)),
    }
    const res = await axios.get('/api/scanner/vulnerabilities/', { params })
    vulns.value = Array.isArray(res.data) ? res.data : res.data.results || []
    total.value = res.data.count || vulns.value.length
  } catch {
    ElMessage.error('加载漏洞失败')
  } finally {
    loading.value = false
  }
}

async function updateStatus(row, status) {
  try {
    await axios.patch(`/api/scanner/vulnerabilities/${row.id}/`, { status })
    ElMessage.success('状态已更新')
    fetchVulns()
  } catch {
    ElMessage.error('更新失败')
  }
}

function viewDetail(row) {
  detailVuln.value = row
  detailVisible.value = true
}

async function exportReport() {
  try {
    const res = await axios.get('/api/scanner/reports/', { responseType: 'blob' })
    const url = URL.createObjectURL(new Blob([res.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = `vulnerability_report_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    ElMessage.warning('导出功能暂不可用')
  }
}

onMounted(fetchVulns)
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: 16px; }
.page-header { display: flex; justify-content: space-between; align-items: center; }
.page-header h2 { margin: 0; font-size: 20px; color: #1a2332; }
.filter-card :deep(.el-card__body) { padding: 16px; }
.filter-card .el-select { width: 100%; }
.pagination { margin-top: 16px; display: flex; justify-content: flex-end; }
.detail-content { padding: 8px; }
.detail-section { margin-top: 20px; }
.detail-section h4 { margin: 0 0 8px; color: #1a2332; font-size: 14px; }
.detail-section p { margin: 0; color: #606266; line-height: 1.6; }
.code-block { background: #f5f7fa; padding: 12px; border-radius: 6px; font-size: 12px; overflow-x: auto; white-space: pre-wrap; word-break: break-all; }
</style>
