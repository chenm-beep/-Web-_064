<template>
  <div class="dashboard">
    <!-- Stat cards -->
    <el-row :gutter="20" class="stat-row">
      <el-col :span="6" v-for="card in statCards" :key="card.label">
        <div class="stat-card" :style="{ borderLeftColor: card.color }">
          <div class="stat-icon" :style="{ background: card.color + '20' }">
            <el-icon :size="28" :color="card.color">
              <component :is="card.icon" />
            </el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ card.value }}</div>
            <div class="stat-label">{{ card.label }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Charts row -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <el-card shadow="never">
          <template #header>
            <span class="card-title">漏洞趋势（近7天）</span>
          </template>
          <v-chart
            :option="lineChartOption"
            style="height: 280px"
            autoresize
          />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <template #header>
            <span class="card-title">漏洞类型分布</span>
          </template>
          <v-chart
            :option="pieChartOption"
            style="height: 280px"
            autoresize
          />
        </el-card>
      </el-col>
    </el-row>

    <!-- Tables row -->
    <el-row :gutter="20" class="table-row">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <span class="card-title">最新漏洞</span>
          </template>
          <el-table
            :data="recentVulns"
            size="small"
            v-loading="loadingVulns"
            stripe
          >
            <el-table-column label="漏洞名称" prop="name" show-overflow-tooltip />
            <el-table-column label="严重程度" width="100">
              <template #default="{ row }">
                <el-tag :type="severityType(row.severity)" size="small">
                  {{ row.severity }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="时间" width="100">
              <template #default="{ row }">
                {{ formatDate(row.discovered_at) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <span class="card-title">最新任务</span>
          </template>
          <el-table
            :data="recentTasks"
            size="small"
            v-loading="loadingTasks"
            stripe
          >
            <el-table-column label="任务名称" prop="task_name" show-overflow-tooltip />
            <el-table-column label="状态" width="90">
              <template #default="{ row }">
                <el-tag :type="taskStatusType(row.status)" size="small">
                  {{ taskStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="时间" width="100">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { formatDate } from '@/utils/format'
import { ref, reactive, computed, onMounted } from 'vue'
import axios from '@/utils/axios'
import { ElMessage } from 'element-plus'

const stats = reactive({
  total_sites: 0,
  active_tasks: 0,
  total_vulnerabilities: 0,
  high_risk_count: 0,
})

const vuln_trend = ref([])
const vuln_types = ref([])
const recentVulns = ref([])
const recentTasks = ref([])
const loadingVulns = ref(false)
const loadingTasks = ref(false)

const statCards = computed(() => [
  { label: '站点总数', value: stats.total_sites, color: '#409EFF', icon: 'Monitor' },
  { label: '活跃任务', value: stats.active_tasks, color: '#E6A23C', icon: 'Loading' },
  { label: '漏洞总数', value: stats.total_vulnerabilities, color: '#F56C6C', icon: 'Warning' },
  { label: '高危漏洞', value: stats.high_risk_count, color: '#c0392b', icon: 'CircleClose' },
])

const lineChartOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 40, right: 20, top: 20, bottom: 30 },
  xAxis: {
    type: 'category',
    data: vuln_trend.value.map((d) => d.date),
    axisLabel: { fontSize: 12 },
  },
  yAxis: { type: 'value', minInterval: 1 },
  series: [
    {
      data: vuln_trend.value.map((d) => d.count),
      type: 'line',
      smooth: true,
      areaStyle: { opacity: 0.15 },
      itemStyle: { color: '#409EFF' },
    },
  ],
}))

const pieChartOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { orient: 'vertical', left: 'left', textStyle: { fontSize: 11 } },
  series: [
    {
      type: 'pie',
      radius: ['40%', '70%'],
      data: vuln_types.value.map((d) => ({ name: d.type, value: d.count })),
      emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.5)' } },
    },
  ],
}))

function severityType(s) {
  const map = { critical: 'danger', high: 'warning', medium: '', low: 'success', info: 'info' }
  return map[s] || 'info'
}

function taskStatusType(s) {
  const map = { pending: 'info', running: 'primary', completed: 'success', failed: 'danger', cancelled: 'warning' }
  return map[s] || 'info'
}

function taskStatusLabel(s) {
  const map = { pending: '待执行', running: '运行中', completed: '已完成', failed: '失败', cancelled: '已取消' }
  return map[s] || s
}

async function fetchDashboard() {
  try {
    const [statsRes, trendRes, typesRes] = await Promise.all([
      axios.get('/api/scanner/dashboard/stats/').catch(() => ({ data: {} })),
      axios.get('/api/scanner/dashboard/vuln-trend/').catch(() => ({ data: [] })),
      axios.get('/api/scanner/dashboard/vuln-types/').catch(() => ({ data: [] })),
    ])
    Object.assign(stats, statsRes.data)
    vuln_trend.value = Array.isArray(trendRes.data) ? trendRes.data : trendRes.data.results || []
    vuln_types.value = Array.isArray(typesRes.data) ? typesRes.data : typesRes.data.results || []
  } catch {
    ElMessage.error('加载统计数据失败')
  }
}

async function fetchRecentVulns() {
  loadingVulns.value = true
  try {
    const res = await axios.get('/api/scanner/vulnerabilities/', { params: { page_size: 5 } })
    recentVulns.value = Array.isArray(res.data) ? res.data : res.data.results || []
  } catch {
    //
  } finally {
    loadingVulns.value = false
  }
}

async function fetchRecentTasks() {
  loadingTasks.value = true
  try {
    const res = await axios.get('/api/scanner/tasks/', { params: { page_size: 5 } })
    recentTasks.value = Array.isArray(res.data) ? res.data : res.data.results || []
  } catch {
    //
  } finally {
    loadingTasks.value = false
  }
}

onMounted(() => {
  fetchDashboard()
  fetchRecentVulns()
  fetchRecentTasks()
})
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  border-left: 4px solid #409eff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1a2332;
  line-height: 1;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #1a2332;
}
</style>
