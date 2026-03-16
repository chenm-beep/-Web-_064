<template>
  <div class="page">
    <div class="page-header">
      <h2>用户管理</h2>
      <el-button type="primary" icon="Plus" @click="openDialog()">添加用户</el-button>
    </div>

    <el-card shadow="never">
      <el-table :data="users" v-loading="loading" stripe>
        <el-table-column label="用户名" prop="username" min-width="120" />
        <el-table-column label="邮箱" prop="email" min-width="180" show-overflow-tooltip />
        <el-table-column label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="roleType(row.role)" size="small">{{ roleLabel(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_active"
              :disabled="row.id === currentUserId"
              @change="toggleUser(row)"
            />
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="110">
          <template #default="{ row }">{{ row.created_at?.slice(0, 10) || row.date_joined?.slice(0, 10) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button size="small" icon="Edit" @click="openDialog(row)">编辑</el-button>
            <el-button
              size="small"
              type="danger"
              icon="Delete"
              :disabled="row.id === currentUserId"
              @click="deleteUser(row)"
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
          @change="fetchUsers"
        />
      </div>
    </el-card>

    <!-- Add/Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="editItem ? '编辑用户' : '添加用户'" width="480px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="!!editItem" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" type="email" />
        </el-form-item>
        <el-form-item label="密码" :prop="editItem ? '' : 'password'">
          <el-input
            v-model="form.password"
            type="password"
            show-password
            :placeholder="editItem ? '留空则不修改密码' : '请输入密码'"
          />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="分析员" value="analyst" />
            <el-option label="查看者" value="viewer" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="停用" />
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
import { ref, reactive, computed, onMounted } from 'vue'
import axios from '@/utils/axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const currentUserId = computed(() => authStore.user?.id)

const users = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const submitting = ref(false)
const editItem = ref(null)
const formRef = ref(null)

const form = reactive({ username: '', email: '', password: '', role: 'viewer', is_active: true })

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }, { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur', min: 6 }],
  role: [{ required: true, trigger: 'change' }],
}

function roleType(r) {
  const map = { admin: 'danger', analyst: 'warning', viewer: 'info' }
  return map[r] || 'info'
}

function roleLabel(r) {
  const map = { admin: '管理员', analyst: '分析员', viewer: '查看者' }
  return map[r] || r
}

async function fetchUsers() {
  loading.value = true
  try {
    const res = await axios.get('/api/users/users/', {
      params: { page: page.value, page_size: pageSize.value },
    })
    users.value = Array.isArray(res.data) ? res.data : res.data.results || []
    total.value = res.data.count || users.value.length
  } catch {
    ElMessage.error('加载用户失败')
  } finally {
    loading.value = false
  }
}

function openDialog(item = null) {
  editItem.value = item
  if (item) {
    Object.assign(form, { username: item.username, email: item.email || '', password: '', role: item.role, is_active: item.is_active })
  } else {
    Object.assign(form, { username: '', email: '', password: '', role: 'viewer', is_active: true })
  }
  dialogVisible.value = true
}

async function submitForm() {
  const requiredRules = editItem.value
    ? { username: rules.username, email: rules.email, role: rules.role }
    : rules
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      const payload = { ...form }
      if (editItem.value && !payload.password) delete payload.password
      if (editItem.value) {
        await axios.put(`/api/users/users/${editItem.value.id}/`, payload)
        ElMessage.success('更新成功')
      } else {
        await axios.post('/api/users/users/', payload)
        ElMessage.success('添加成功')
      }
      dialogVisible.value = false
      fetchUsers()
    } catch (err) {
      const errData = err.response?.data
      const msg = typeof errData === 'object' ? JSON.stringify(errData) : '操作失败'
      ElMessage.error(msg)
    } finally {
      submitting.value = false
    }
  })
}

async function toggleUser(row) {
  try {
    await axios.patch(`/api/users/users/${row.id}/`, { is_active: row.is_active })
    ElMessage.success(row.is_active ? '已启用' : '已停用')
  } catch {
    row.is_active = !row.is_active
    ElMessage.error('操作失败')
  }
}

async function deleteUser(row) {
  if (row.id === currentUserId.value) {
    ElMessage.warning('不能删除自己的账号')
    return
  }
  await ElMessageBox.confirm(`确定删除用户"${row.username}"？`, '警告', { type: 'warning' })
  try {
    await axios.delete(`/api/users/users/${row.id}/`)
    ElMessage.success('删除成功')
    fetchUsers()
  } catch {
    ElMessage.error('删除失败')
  }
}

onMounted(fetchUsers)
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: 16px; }
.page-header { display: flex; justify-content: space-between; align-items: center; }
.page-header h2 { margin: 0; font-size: 20px; color: #1a2332; }
.pagination { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
