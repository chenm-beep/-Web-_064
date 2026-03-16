<template>
  <div class="page">
    <div class="page-header">
      <h2>POC插件库</h2>
      <el-button type="primary" icon="Plus" @click="openDialog()">添加插件</el-button>
    </div>

    <el-card shadow="never">
      <el-table :data="plugins" v-loading="loading" stripe>
        <el-table-column label="插件名称" prop="name" min-width="160" show-overflow-tooltip />
        <el-table-column label="漏洞类型" prop="vuln_type" width="130" />
        <el-table-column label="严重程度" width="100">
          <template #default="{ row }">
            <el-tag :type="severityType(row.severity)" size="small">{{ severityLabel(row.severity) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="作者" prop="author" width="100" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_enabled"
              @change="togglePlugin(row)"
              active-text="启用"
              inactive-text="停用"
            />
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="110">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button size="small" icon="Edit" @click="openDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" icon="Delete" @click="deletePlugin(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @change="fetchPlugins"
        />
      </div>
    </el-card>

    <!-- Add/Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="editItem ? '编辑插件' : '添加插件'" width="640px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="插件名称" prop="name">
              <el-input v-model="form.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="漏洞类型" prop="vuln_type">
              <el-select v-model="form.vuln_type" style="width: 100%">
                <el-option label="SQL注入" value="sql_injection" />
                <el-option label="XSS" value="xss" />
                <el-option label="命令注入" value="command_injection" />
                <el-option label="路径遍历" value="path_traversal" />
                <el-option label="CSRF" value="csrf" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="严重程度" prop="severity">
              <el-select v-model="form.severity" style="width: 100%">
                <el-option label="严重" value="critical" />
                <el-option label="高危" value="high" />
                <el-option label="中危" value="medium" />
                <el-option label="低危" value="low" />
                <el-option label="信息" value="info" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="作者">
              <el-input v-model="form.author" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="脚本内容">
          <el-input
            v-model="form.script"
            type="textarea"
            :rows="8"
            placeholder="输入POC脚本代码..."
            style="font-family: monospace; font-size: 13px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.is_enabled" active-text="启用" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { formatDate } from '@/utils/format'
import { ref, reactive, onMounted } from 'vue'
import axios from '@/utils/axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const plugins = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const submitting = ref(false)
const editItem = ref(null)
const formRef = ref(null)

const form = reactive({
  name: '', vuln_type: 'xss', severity: 'medium', author: '',
  description: '', script: '', is_enabled: true,
})

const rules = {
  name: [{ required: true, message: '请输入插件名称', trigger: 'blur' }],
  vuln_type: [{ required: true, trigger: 'change' }],
  severity: [{ required: true, trigger: 'change' }],
}

function severityType(s) {
  const map = { critical: 'danger', high: 'warning', medium: '', low: 'success', info: 'info' }
  return map[s] || 'info'
}

function severityLabel(s) {
  const map = { critical: '严重', high: '高危', medium: '中危', low: '低危', info: '信息' }
  return map[s] || s
}

async function fetchPlugins() {
  loading.value = true
  try {
    const res = await axios.get('/api/scanner/poc-plugins/', {
      params: { page: page.value, page_size: pageSize.value },
    })
    plugins.value = Array.isArray(res.data) ? res.data : res.data.results || []
    total.value = res.data.count || plugins.value.length
  } catch {
    ElMessage.error('加载插件失败')
  } finally {
    loading.value = false
  }
}

function openDialog(item = null) {
  editItem.value = item
  if (item) {
    Object.assign(form, {
      name: item.name, vuln_type: item.vuln_type, severity: item.severity,
      author: item.author || '', description: item.description || '',
      script: item.script || '', is_enabled: item.is_enabled,
    })
  } else {
    Object.assign(form, { name: '', vuln_type: 'xss', severity: 'medium', author: '', description: '', script: '', is_enabled: true })
  }
  dialogVisible.value = true
}

async function submitForm() {
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      if (editItem.value) {
        await axios.put(`/api/scanner/poc-plugins/${editItem.value.id}/`, form)
        ElMessage.success('更新成功')
      } else {
        await axios.post('/api/scanner/poc-plugins/', form)
        ElMessage.success('添加成功')
      }
      dialogVisible.value = false
      fetchPlugins()
    } catch (err) {
      ElMessage.error(err.response?.data?.detail || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

async function togglePlugin(row) {
  try {
    await axios.patch(`/api/scanner/poc-plugins/${row.id}/`, { is_enabled: row.is_enabled })
    ElMessage.success(row.is_enabled ? '已启用' : '已停用')
  } catch {
    row.is_enabled = !row.is_enabled
    ElMessage.error('操作失败')
  }
}

async function deletePlugin(row) {
  await ElMessageBox.confirm(`确定删除插件"${row.name}"？`, '警告', { type: 'warning' })
  try {
    await axios.delete(`/api/scanner/poc-plugins/${row.id}/`)
    ElMessage.success('删除成功')
    fetchPlugins()
  } catch {
    ElMessage.error('删除失败')
  }
}

onMounted(fetchPlugins)
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: 16px; }
.page-header { display: flex; justify-content: space-between; align-items: center; }
.page-header h2 { margin: 0; font-size: 20px; color: #1a2332; }
.pagination { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
