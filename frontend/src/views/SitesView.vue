<template>
  <div class="page">
    <div class="page-header">
      <h2>资产管理</h2>
      <div class="toolbar">
        <el-input
          v-model="search"
          placeholder="搜索站点名称/URL"
          prefix-icon="Search"
          clearable
          style="width: 260px"
          @input="fetchSites"
        />
        <el-button type="primary" icon="Plus" @click="openDialog()">添加站点</el-button>
      </div>
    </div>

    <el-card shadow="never">
      <el-table :data="sites" v-loading="loading" stripe>
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column label="站点名称" prop="name" min-width="140" show-overflow-tooltip />
        <el-table-column label="URL" prop="url" min-width="200" show-overflow-tooltip />
        <el-table-column label="描述" prop="description" min-width="160" show-overflow-tooltip />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="110">
          <template #default="{ row }">{{ row.created_at?.slice(0, 10) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button size="small" icon="Edit" @click="openDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" icon="Delete" @click="deleteSite(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @change="fetchSites"
        />
      </div>
    </el-card>

    <!-- Add/Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="editItem ? '编辑站点' : '添加站点'" width="520px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="站点名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入站点名称" />
        </el-form-item>
        <el-form-item label="URL" prop="url">
          <el-input v-model="form.url" placeholder="https://example.com" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="可选描述" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from '@/utils/axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const sites = ref([])
const loading = ref(false)
const search = ref('')
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const submitting = ref(false)
const editItem = ref(null)
const formRef = ref(null)

const form = reactive({ name: '', url: '', description: '', is_active: true })

const rules = {
  name: [{ required: true, message: '请输入站点名称', trigger: 'blur' }],
  url: [{ required: true, message: '请输入URL', trigger: 'blur' }],
}

async function fetchSites() {
  loading.value = true
  try {
    const res = await axios.get('/api/scanner/sites/', {
      params: { search: search.value, page: page.value, page_size: pageSize.value },
    })
    sites.value = Array.isArray(res.data) ? res.data : res.data.results || []
    total.value = res.data.count || sites.value.length
  } catch {
    ElMessage.error('加载站点失败')
  } finally {
    loading.value = false
  }
}

function openDialog(item = null) {
  editItem.value = item
  if (item) {
    Object.assign(form, { name: item.name, url: item.url, description: item.description || '', is_active: item.is_active })
  } else {
    Object.assign(form, { name: '', url: '', description: '', is_active: true })
  }
  dialogVisible.value = true
}

async function submitForm() {
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      if (editItem.value) {
        await axios.put(`/api/scanner/sites/${editItem.value.id}/`, form)
        ElMessage.success('更新成功')
      } else {
        await axios.post('/api/scanner/sites/', form)
        ElMessage.success('添加成功')
      }
      dialogVisible.value = false
      fetchSites()
    } catch (err) {
      ElMessage.error(err.response?.data?.detail || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

async function deleteSite(row) {
  await ElMessageBox.confirm(`确定删除站点"${row.name}"？`, '警告', {
    type: 'warning',
    confirmButtonText: '删除',
    confirmButtonClass: 'el-button--danger',
  })
  try {
    await axios.delete(`/api/scanner/sites/${row.id}/`)
    ElMessage.success('删除成功')
    fetchSites()
  } catch {
    ElMessage.error('删除失败')
  }
}

onMounted(fetchSites)
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: 16px; }
.page-header { display: flex; justify-content: space-between; align-items: center; }
.page-header h2 { margin: 0; font-size: 20px; color: #1a2332; }
.toolbar { display: flex; gap: 12px; }
.pagination { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
