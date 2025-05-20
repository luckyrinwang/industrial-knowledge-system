<template>
  <div class="home-container">
    <el-card class="welcome-card">
      <template #header>
        <div class="card-header">
          <h3>欢迎使用工业知识库系统</h3>
        </div>
      </template>
      <div class="card-content">
        <p>您已成功登录系统。</p>
        <p>当前用户: {{ userInfo.username }}</p>
        <p>角色: {{ userRoles }}</p>
        <p>登录时间: {{ loginTime }}</p>
      </div>
    </el-card>

    <div class="stats-cards">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card shadow="hover" class="stat-card">
            <h4>知识库条目总数</h4>
            <div class="stat-value">
              <el-statistic :value="324" />
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" class="stat-card">
            <h4>本月新增条目</h4>
            <div class="stat-value">
              <el-statistic :value="42" />
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" class="stat-card">
            <h4>系统用户数</h4>
            <div class="stat-value">
              <el-statistic :value="15" />
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 快捷功能区域 -->
    <div class="shortcuts-section" v-if="isAdmin">
      <h3>系统管理</h3>
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card shadow="hover" class="shortcut-card" @click="goToLogs">
            <div class="shortcut-icon">
              <el-icon :size="30"><document /></el-icon>
            </div>
            <div class="shortcut-title">操作日志</div>
            <div class="shortcut-desc">查看用户对文件的操作记录</div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { formatDate } from '@/utils/date'
import { Document } from '@element-plus/icons-vue'

const router = useRouter()

// 用户信息
const userInfo = ref({})
// 用户角色
const userRoles = computed(() => {
  if (!userInfo.value.roles || userInfo.value.roles.length === 0) {
    return '无'
  }
  return userInfo.value.roles.join(', ')
})
// 是否为管理员
const isAdmin = computed(() => {
  return userInfo.value.roles && userInfo.value.roles.includes('admin')
})
// 登录时间
const loginTime = ref(formatDate(new Date()))

// 获取用户信息
onMounted(() => {
  const storedUserInfo = localStorage.getItem('user')
  if (storedUserInfo) {
    userInfo.value = JSON.parse(storedUserInfo)
  }
})

// 跳转到操作日志页面
const goToLogs = () => {
  router.push('/dashboard/logs')
}
</script>

<style scoped>
.home-container {
  padding: 10px;
}

.welcome-card {
  margin-bottom: 30px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
}

.card-content {
  line-height: 1.8;
  color: #606266;
}

.stats-cards {
  margin-top: 20px;
  margin-bottom: 30px;
}

.stat-card {
  text-align: center;
  padding: 10px;
}

.stat-card h4 {
  margin-top: 0;
  color: #606266;
}

.stat-value {
  margin-top: 15px;
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.shortcuts-section {
  margin-top: 30px;
}

.shortcuts-section h3 {
  margin-bottom: 20px;
  font-weight: 500;
  color: #303133;
}

.shortcut-card {
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  padding: 20px;
}

.shortcut-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

.shortcut-icon {
  margin-bottom: 15px;
  color: #409EFF;
}

.shortcut-title {
  font-weight: bold;
  font-size: 16px;
  margin-bottom: 8px;
}

.shortcut-desc {
  color: #909399;
  font-size: 13px;
}
</style> 