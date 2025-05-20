<template>
  <div class="operation-logs-container">
    <el-card class="filter-container">
      <el-form :inline="true" :model="queryParams" class="search-form">
        <el-form-item label="用户">
          <el-select v-model="queryParams.user_id" placeholder="选择用户" clearable style="min-width: 120px;">
            <el-option v-for="user in users" :key="user.id" :label="user.username" :value="String(user.id)"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="操作类型">
          <el-select v-model="queryParams.operation_type" placeholder="选择操作类型" clearable style="min-width: 120px;">
            <el-option label="创建" value="create"></el-option>
            <el-option label="查看" value="read"></el-option>
            <el-option label="更新" value="update"></el-option>
            <el-option label="删除" value="delete"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="文件ID">
          <el-input v-model="queryParams.file_id" placeholder="文件ID" clearable></el-input>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="queryParams.search" placeholder="搜索关键词" clearable></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-container">
      <div class="table-header">
        <h3>操作日志列表</h3>
        <div class="table-actions">
          <el-button type="primary" @click="handleExport">导出</el-button>
        </div>
      </div>
      
      <el-table
        v-loading="loading"
        :data="logsList"
        stripe
        border
        style="width: 100%"
      >
        <el-table-column type="index" width="50"></el-table-column>
        <el-table-column prop="operation_time" label="操作时间" width="180" sortable>
          <template #default="scope">
            {{ formatDate(scope.row.operation_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="user.username" label="操作用户" width="120">
          <template #default="scope">
            {{ scope.row.user ? scope.row.user.username : '未知用户' }}
          </template>
        </el-table-column>
        <el-table-column prop="operation_type" label="操作类型" width="100">
          <template #default="scope">
            <el-tag :type="getOperationTypeTag(scope.row.operation_type)">
              {{ getOperationTypeLabel(scope.row.operation_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="file.original_filename" label="操作文件" min-width="200">
          <template #default="scope">
            <template v-if="scope.row.file">
              {{ scope.row.file.original_filename }}
            </template>
            <template v-else-if="scope.row.file_name">
              <span :class="{'deleted-file': scope.row.operation_type === 'delete'}">
                {{ scope.row.file_name }}
                <el-tag v-if="scope.row.operation_type === 'delete'" size="small" type="danger">已删除</el-tag>
              </span>
            </template>
            <template v-else-if="scope.row.operation_type === 'delete' && scope.row.details">
              <span class="deleted-file">
                {{ getDeletedFileName(scope.row.details) }}
                <el-tag size="small" type="danger">已删除</el-tag>
              </span>
            </template>
            <template v-else>
              未知文件
            </template>
          </template>
        </el-table-column>
        <el-table-column prop="details" label="操作详情" min-width="200">
          <template #default="scope">
            {{ formatDetails(scope.row.details) }}
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP地址" width="130"></el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          v-model:current-page="queryParams.page"
          v-model:page-size="queryParams.per_page"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        ></el-pagination>
      </div>
    </el-card>

    <el-card class="stats-container" v-if="showStats">
      <h3>操作统计</h3>
      <el-row :gutter="20">
        <el-col :span="8">
          <div class="stats-chart">
            <h4>按操作类型</h4>
            <div ref="operationTypeChart" class="chart"></div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stats-chart">
            <h4>按用户</h4>
            <div ref="userStatsChart" class="chart"></div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stats-chart">
            <h4>按文件类型</h4>
            <div ref="fileTypeChart" class="chart"></div>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getLogs, getLogStats, exportLogs } from '@/api/log'
import { getUsers } from '@/api/user'
// 导入 ECharts
import * as echarts from 'echarts'

export default {
  name: 'OperationLogs',
  setup() {
    // 数据加载状态
    const loading = ref(false)
    // 统计图表实例
    const operationTypeChart = ref(null)
    const userStatsChart = ref(null)
    const fileTypeChart = ref(null)
    let charts = []
    
    // 显示统计信息
    const showStats = ref(true)
    
    // 查询参数
    const queryParams = reactive({
      page: 1,
      per_page: 20,
      user_id: '', // 默认查全部用户日志
      file_id: '',
      operation_type: '',
      start_date: '',
      end_date: '',
      search: ''
    })
    
    // 日期范围选择器
    const dateRange = ref([])
    
    // 用户列表
    const users = ref([])
    
    // 日志列表数据
    const logsList = ref([])
    const total = ref(0)
    
    // 监听日期范围变化
    const watchDateRange = computed(() => {
      if (dateRange.value && dateRange.value.length === 2) {
        queryParams.start_date = dateRange.value[0]
        queryParams.end_date = dateRange.value[1]
      } else {
        queryParams.start_date = ''
        queryParams.end_date = ''
      }
      return dateRange.value
    })
    
    // 初始化
    onMounted(() => {
      // 强制重置user_id，防止被意外赋值
      queryParams.user_id = ''
      fetchLogs()
      fetchUsers()
      fetchStats()
      
      // 添加窗口大小变化监听，以便重绘图表
      window.addEventListener('resize', handleResize)
    })
    
    // 组件卸载时清理资源
    onUnmounted(() => {
      window.removeEventListener('resize', handleResize)
      disposeCharts()
    })
    
    // 获取日志列表
    const fetchLogs = async () => {
      // 再次保护，防止user_id被意外赋值
      if (queryParams.user_id === undefined || queryParams.user_id === null) {
        queryParams.user_id = ''
      }
      loading.value = true
      try {
        const response = await getLogs({ ...queryParams })
        logsList.value = response.items
        total.value = response.total
      } catch (error) {
        console.error('获取日志列表失败:', error)
        ElMessage.error('获取日志列表失败')
      } finally {
        loading.value = false
      }
    }
    
    // 获取用户列表
    const fetchUsers = async () => {
      try {
        const response = await getUsers()
        users.value = response.items
      } catch (error) {
        console.error('获取用户列表失败:', error)
      }
    }
    
    // 获取统计数据
    const fetchStats = async () => {
      try {
        const response = await getLogStats()
        // 初始化统计图表
        nextTick(() => {
          initOperationTypeChart(response.operation_stats)
          initUserStatsChart(response.user_stats)
          initFileTypeChart(response.file_type_stats)
        })
      } catch (error) {
        console.error('获取统计数据失败:', error)
        showStats.value = false
      }
    }
    
    // 初始化操作类型统计图表
    const initOperationTypeChart = (data) => {
      if (operationTypeChart.value) {
        const chart = echarts.init(operationTypeChart.value)
        charts.push(chart)
        
        const options = {
          title: {
            text: '操作类型统计',
            left: 'center'
          },
          tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b} : {c} ({d}%)'
          },
          legend: {
            orient: 'vertical',
            left: 'left',
            data: Object.keys(data).map(type => getOperationTypeLabel(type))
          },
          series: [
            {
              name: '操作类型',
              type: 'pie',
              radius: '50%',
              data: Object.entries(data).map(([type, count]) => ({
                name: getOperationTypeLabel(type),
                value: count
              })),
              emphasis: {
                itemStyle: {
                  shadowBlur: 10,
                  shadowOffsetX: 0,
                  shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
              }
            }
          ]
        }
        
        chart.setOption(options)
      }
    }
    
    // 初始化用户统计图表
    const initUserStatsChart = (data) => {
      if (userStatsChart.value) {
        const chart = echarts.init(userStatsChart.value)
        charts.push(chart)
        
        const options = {
          title: {
            text: '用户操作统计',
            left: 'center'
          },
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow'
            }
          },
          xAxis: {
            type: 'category',
            data: Object.keys(data),
            axisLabel: {
              interval: 0,
              rotate: 30
            }
          },
          yAxis: {
            type: 'value'
          },
          series: [
            {
              name: '操作次数',
              type: 'bar',
              data: Object.values(data)
            }
          ]
        }
        
        chart.setOption(options)
      }
    }
    
    // 初始化文件类型统计图表
    const initFileTypeChart = (data) => {
      if (fileTypeChart.value) {
        const chart = echarts.init(fileTypeChart.value)
        charts.push(chart)
        
        const options = {
          title: {
            text: '文件类型统计',
            left: 'center'
          },
          tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b} : {c} ({d}%)'
          },
          legend: {
            orient: 'vertical',
            left: 'left',
            data: Object.keys(data)
          },
          series: [
            {
              name: '文件类型',
              type: 'pie',
              radius: '50%',
              data: Object.entries(data).map(([type, count]) => ({
                name: type,
                value: count
              })),
              emphasis: {
                itemStyle: {
                  shadowBlur: 10,
                  shadowOffsetX: 0,
                  shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
              }
            }
          ]
        }
        
        chart.setOption(options)
      }
    }
    
    // 处理窗口大小变化
    const handleResize = () => {
      charts.forEach(chart => {
        chart && chart.resize()
      })
    }
    
    // 清理图表实例
    const disposeCharts = () => {
      charts.forEach(chart => {
        chart && chart.dispose()
      })
      charts = []
    }
    
    // 搜索按钮事件
    const handleSearch = () => {
      queryParams.page = 1
      // 只有你手动选择了用户，才会带user_id，否则查全部
      fetchLogs()
    }
    
    // 重置查询
    const resetQuery = () => {
      Object.assign(queryParams, {
        page: 1,
        per_page: 20,
        user_id: '', // 重置为查全部
        file_id: '',
        operation_type: '',
        start_date: '',
        end_date: '',
        search: ''
      })
      dateRange.value = []
      fetchLogs()
    }
    
    // 导出日志
    const handleExport = async () => {
      try {
        const response = await exportLogs(queryParams)
        const blob = new Blob([response.data], { type: 'application/vnd.ms-excel' })
        const link = document.createElement('a')
        link.href = window.URL.createObjectURL(blob)
        link.download = `操作日志_${new Date().toISOString().slice(0, 10)}.xlsx`
        link.click()
      } catch (error) {
        console.error('导出日志失败:', error)
        ElMessage.error('导出日志失败')
      }
    }
    
    // 处理每页显示条数变化
    const handleSizeChange = (size) => {
      queryParams.per_page = size
      fetchLogs()
    }
    
    // 处理页码变化
    const handleCurrentChange = (page) => {
      queryParams.page = page
      fetchLogs()
    }
    
    // 格式化日期
    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`
    }
    
    // 格式化操作详情
    const formatDetails = (details) => {
      if (!details) return ''
      try {
        // 尝试解析JSON
        const detailObj = JSON.parse(details)
        return detailObj.message || details
      } catch (e) {
        return details
      }
    }
    
    // 获取操作类型标签文本
    const getOperationTypeLabel = (type) => {
      const types = {
        'create': '创建',
        'read': '查看',
        'update': '更新',
        'delete': '删除'
      }
      return types[type] || type
    }
    
    // 获取操作类型标签样式
    const getOperationTypeTag = (type) => {
      const types = {
        'create': 'success',
        'read': 'info',
        'update': 'warning',
        'delete': 'danger'
      }
      return types[type] || ''
    }
    
    // 获取已删除文件名
    const getDeletedFileName = (details) => {
      if (!details) return ''
      try {
        // 尝试解析JSON
        const detailObj = JSON.parse(details)
        if (detailObj.file_info && detailObj.file_info.original_filename) {
          return detailObj.file_info.original_filename
        }
        return ''
      } catch (e) {
        return ''
      }
    }
    
    return {
      loading,
      operationTypeChart,
      userStatsChart,
      fileTypeChart,
      showStats,
      queryParams,
      dateRange,
      watchDateRange,
      users,
      logsList,
      total,
      handleSearch,
      resetQuery,
      handleExport,
      handleSizeChange,
      handleCurrentChange,
      formatDate,
      formatDetails,
      getOperationTypeLabel,
      getOperationTypeTag,
      getDeletedFileName
    }
  }
}
</script>

<style scoped>
.operation-logs-container {
  padding: 20px;
}
.filter-container,
.table-container,
.stats-container {
  margin-bottom: 20px;
}
.search-form {
  display: flex;
  flex-wrap: wrap;
}
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.table-header h3 {
  margin: 0;
}
.pagination-container {
  margin-top: 20px;
  text-align: right;
}
.stats-chart {
  height: 300px;
  margin-bottom: 20px;
}
.chart {
  height: 250px;
}
.deleted-file {
  color: #f56c6c;
}
</style> 