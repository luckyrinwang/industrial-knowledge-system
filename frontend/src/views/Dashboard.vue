<template>
  <div class="dashboard-container">
    <!-- 顶部导航栏 -->    <el-header class="header">
      <div class="logo">
        <h2>{{ config.system.title }}</h2>
      </div>
      <div class="user-info">
        <el-dropdown @command="handleCommand">
          <span class="user-name">
            {{ userInfo.full_name || userInfo.username }}
            <el-icon><arrow-down /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人中心</el-dropdown-item>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    
    <el-container class="main-container">
      <!-- 侧边菜单 -->
      <el-aside width="220px">
        <el-menu
          :default-active="activeMenu"
          class="menu"
          router
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
        >
          <el-menu-item index="/dashboard/home">
            <el-icon><home-filled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          
          <el-menu-item v-if="isAdmin" index="/dashboard/users">
            <el-icon><user /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
          
          <el-menu-item index="/dashboard/files">
            <el-icon><folder /></el-icon>
            <span>文件管理</span>
          </el-menu-item>
          
          <el-menu-item index="/dashboard/knowledge">
            <el-icon><chat-dot-round /></el-icon>
            <span>知识库</span>
          </el-menu-item>
          
          <el-menu-item v-if="isAdmin" index="/dashboard/logs">
            <el-icon><document /></el-icon>
            <span>操作日志</span>
          </el-menu-item>
          
          <el-menu-item index="/dashboard/profile">
            <el-icon><setting /></el-icon>
            <span>个人中心</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <!-- 主内容区 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { HomeFilled, User, Setting, ArrowDown, Folder, Document, ChatDotRound } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import config from '@/config'

const router = useRouter()
const route = useRoute()

// 用户信息
const userInfo = ref({})
// 是否为管理员
const isAdmin = computed(() => {
  return userInfo.value.roles && userInfo.value.roles.includes('admin')
})
// 当前激活的菜单项
const activeMenu = computed(() => route.path)

// 在组件挂载时获取用户信息
onMounted(() => {
  const storedUserInfo = localStorage.getItem('user')
  if (storedUserInfo) {
    userInfo.value = JSON.parse(storedUserInfo)
  } else {
    router.push('/login')
  }
})

// 处理下拉菜单命令
const handleCommand = (command) => {
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      // 清除登录信息
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      // 跳转到登录页
      router.push('/login')
    }).catch(() => {})
  } else if (command === 'profile') {
    router.push('/dashboard/profile')
  }
}
</script>

<style scoped>
.dashboard-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.header {
  background-color: #ffffff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 60px;
}

.logo h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.user-info {
  display: flex;
  align-items: center;
}

.user-name {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
  color: #606266;
}

.main-container {
  flex: 1;
  overflow: hidden;
}

.menu {
  height: 100%;
  border-right: none;
}

.main-content {
  padding: 20px;
  background-color: #f0f2f5;
  height: 100%;
  overflow: auto;
}
</style>