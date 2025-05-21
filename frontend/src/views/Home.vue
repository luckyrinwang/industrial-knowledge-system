<template>
  <div class="home-bg">
    <div class="home-container">
      <!-- 顶部欢迎区 -->
      <el-card class="welcome-card">
        <template #header>
          <div class="card-header">
            <img src="/logo192.png" class="home-logo" alt="logo" />
            <div>
              <h3>欢迎来到工业知识库系统</h3>
              <div class="slogan">让工业知识更智能 · 更高效 · 更安全</div>
            </div>
          </div>
        </template>
        <div class="card-content">
          <el-row :gutter="30">
            <el-col :span="8">
              <div class="user-info-block">
                <el-icon class="user-icon"><UserFilled /></el-icon>
                <div class="info-label">当前用户</div>
                <div class="info-value">{{ userInfo.username }}</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="user-info-block">
                <el-icon class="user-icon"><Medal /></el-icon>
                <div class="info-label">角色</div>
                <div class="info-value">{{ userRoles }}</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="user-info-block">
                <el-icon class="user-icon"><Clock /></el-icon>
                <div class="info-label">登录时间</div>
                <div class="info-value">{{ loginTime }}</div>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-card>

      <!-- 统计区 -->
      <div class="stats-cards">
        <el-row :gutter="30">
          <el-col :span="8">
            <el-card shadow="hover" class="stat-card stat-blue">
              <div class="stat-icon"><el-icon :size="36"><Collection /></el-icon></div>
              <div class="stat-title">知识库条目总数</div>
              <div class="stat-value">324</div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover" class="stat-card stat-green">
              <div class="stat-icon"><el-icon :size="36"><TrendCharts /></el-icon></div>
              <div class="stat-title">本月新增条目</div>
              <div class="stat-value">42</div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover" class="stat-card stat-orange">
              <div class="stat-icon"><el-icon :size="36"><User /></el-icon></div>
              <div class="stat-title">系统用户数</div>
              <div class="stat-value">15</div>
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
              <div class="shortcut-icon shortcut-blue">
                <el-icon :size="32"><Document /></el-icon>
              </div>
              <div class="shortcut-title">操作日志</div>
              <div class="shortcut-desc">查看用户对文件的操作记录</div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { formatDate } from '@/utils/date'
import { Document, UserFilled, User, Medal, Clock, Collection, TrendCharts } from '@element-plus/icons-vue'

const router = useRouter()

const userInfo = ref({})
const userRoles = computed(() => {
  if (!userInfo.value.roles || userInfo.value.roles.length === 0) {
    return '无'
  }
  return userInfo.value.roles.join(', ')
})
const isAdmin = computed(() => {
  return userInfo.value.roles && userInfo.value.roles.includes('admin')
})
const loginTime = ref(formatDate(new Date()))

onMounted(() => {
  const storedUserInfo = localStorage.getItem('user')
  if (storedUserInfo) {
    userInfo.value = JSON.parse(storedUserInfo)
  }
})

const goToLogs = () => {
  router.push('/dashboard/logs')
}
</script>

<style scoped>
html, body, #app {
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
}

.home-bg {
  min-height: 100vh;
  width: 100%;
  background: linear-gradient(135deg, #f5f7fa 0%, #e3eafc 100%);
  padding: 0;
  overflow-x: hidden;
  overflow-y: auto;
  display: flex;
  justify-content: center;
  box-sizing: border-box;
}

.home-container {
  width: 100%;
  max-width: 1100px;
  padding: 16px 8px;
  box-sizing: border-box;
}

/* 以下保留原样，略去重复注释 */
.welcome-card {
  margin-bottom: 36px;
  border-radius: 18px;
  box-shadow: 0 4px 24px 0 rgba(30,60,114,0.10);
  background: #fff;
}
.card-header {
  display: flex;
  align-items: center;
  gap: 18px;
}
.home-logo {
  width: 60px;
  height: 60px;
  border-radius: 14px;
  box-shadow: 0 2px 8px rgba(30,60,114,0.10);
  background: #e3eafc;
}
.card-header h3 {
  margin: 0;
  font-size: 26px;
  font-weight: 700;
  color: #1e3c72;
  letter-spacing: 2px;
}
.slogan {
  font-size: 15px;
  color: #409EFF;
  margin-top: 4px;
  letter-spacing: 1px;
}
.card-content {
  margin-top: 10px;
  margin-bottom: 10px;
}
.user-info-block {
  background: linear-gradient(90deg, #e3eafc 0%, #f5f7fa 100%);
  border-radius: 12px;
  padding: 18px 0 10px 0;
  text-align: center;
  box-shadow: 0 2px 8px rgba(30,60,114,0.06);
  margin-bottom: 8px;
}
.user-icon {
  font-size: 28px;
  color: #1e3c72;
  margin-bottom: 6px;
}
.info-label {
  color: #909399;
  font-size: 14px;
}
.info-value {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-top: 2px;
}
.stats-cards {
  margin-top: 18px;
  margin-bottom: 36px;
}
.stat-card {
  text-align: center;
  border-radius: 16px;
  box-shadow: 0 2px 12px 0 rgba(30,60,114,0.08);
  padding: 28px 0 18px 0;
  color: #fff;
  position: relative;
  overflow: hidden;
}
.stat-blue {
  background: linear-gradient(120deg, #1e3c72 0%, #2a5298 100%);
}
.stat-green {
  background: linear-gradient(120deg, #43cea2 0%, #185a9d 100%);
}
.stat-orange {
  background: linear-gradient(120deg, #f7971e 0%, #ffd200 100%);
  color: #7a5c00;
}
.stat-icon {
  margin-bottom: 10px;
  font-size: 36px;
}
.stat-title {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 6px;
}
.stat-value {
  font-size: 32px;
  font-weight: bold;
  letter-spacing: 1px;
}
.shortcuts-section {
  margin-top: 36px;
}
.shortcuts-section h3 {
  margin-bottom: 20px;
  font-weight: 600;
  color: #1e3c72;
}
.shortcut-card {
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  padding: 28px 0 18px 0;
  border-radius: 14px;
  box-shadow: 0 2px 12px 0 rgba(30,60,114,0.08);
  background: #fff;
}
.shortcut-card:hover {
  transform: translateY(-5px) scale(1.03);
  box-shadow: 0 10px 24px rgba(30,60,114,0.13);
}
.shortcut-icon {
  margin-bottom: 12px;
  font-size: 32px;
}
.shortcut-blue {
  color: #409EFF;
}
.shortcut-title {
  font-weight: bold;
  font-size: 17px;
  margin-bottom: 8px;
}
.shortcut-desc {
  color: #909399;
  font-size: 13px;
}
</style>
