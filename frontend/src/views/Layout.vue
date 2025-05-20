<div>HELLO TEST</div>
<template>
  <div class="app-container">
    <el-container class="layout-container">
      <!-- 侧边栏 -->
      <el-aside width="220px" class="aside">
        <div class="logo">
          <h1>工业知识库系统</h1>
        </div>
        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical"
          :collapse="isCollapse"
          background-color="#304156"
          text-color="#fff"
          active-text-color="#409EFF"
          :router="true"
        >
          <el-menu-item index="/">
            <el-icon><icon-menu /></el-icon>
            <span>首页</span>
          </el-menu-item>

          <el-menu-item index="/test">
            <el-icon><time /></el-icon>
            <span>测试菜单</span>
          </el-menu-item>
          
          <el-sub-menu v-if="authStore.isAdmin" index="/admin">
            <template #title>
              <el-icon><setting /></el-icon>
              <span>系统管理</span>
            </template>
            <el-menu-item index="/users">
              <el-icon><user /></el-icon>
              <span>用户管理</span>
            </el-menu-item>
            <el-menu-item index="/roles">
              <el-icon><connection /></el-icon>
              <span>角色管理</span>
            </el-menu-item>
            <el-menu-item index="/permissions">
              <el-icon><lock /></el-icon>
              <span>权限管理</span>
            </el-menu-item>
            <el-menu-item index="/dashboard/logs">
              <el-icon><time /></el-icon>
              <span>操作日志</span>
            </el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="/knowledge">
            <template #title>
              <el-icon><document /></el-icon>
              <span>知识库</span>
            </template>
            <el-menu-item index="/knowledge/search">
              <el-icon><search /></el-icon>
              <span>知识检索</span>
            </el-menu-item>
            <el-menu-item v-if="authStore.isAdmin" index="/knowledge/manage">
              <el-icon><edit-pen /></el-icon>
              <span>知识管理</span>
            </el-menu-item>
          </el-sub-menu>
          
          <el-menu-item index="/dashboard/files">
            <el-icon><folder-opened /></el-icon>
            <span>文件管理</span>
          </el-menu-item>
          
          <el-menu-item index="/dashboard/logs">
            <el-icon><time /></el-icon>
            <span>操作日志</span>
          </el-menu-item>
          
          <el-menu-item index="/profile">
            <el-icon><avatar /></el-icon>
            <span>个人中心</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <!-- 主体区域 -->
      <el-container class="main-container">
        <!-- 顶部导航 -->
        <el-header height="60px" class="header">
          <div class="header-left">
            <el-icon @click="toggleSidebar" class="toggle-btn">
              <fold v-if="!isCollapse" />
              <expand v-else />
            </el-icon>
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
              <el-breadcrumb-item v-if="$route.meta.title">{{ $route.meta.title }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <div class="header-right">
            <el-dropdown trigger="click" @command="handleCommand">
              <span class="dropdown-link">
                {{ authStore.currentUser?.username }}
                <el-icon class="el-icon--right">
                  <arrow-down />
                </el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                  <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        
        <!-- 内容区域 -->
        <el-main class="main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { ElMessageBox } from 'element-plus'
import { 
  Menu as IconMenu, 
  Setting, 
  User, 
  Connection, 
  Lock, 
  Document, 
  Search, 
  EditPen, 
  Avatar, 
  Fold, 
  Expand, 
  ArrowDown,
  FolderOpened,
  Timer as Time
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const isCollapse = ref(false)

// 获取当前活动菜单
const activeMenu = computed(() => {
  return route.path
})

// 切换侧边栏折叠状态
const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

// 处理下拉菜单命令
const handleCommand = (command) => {
  if (command === 'logout') {
    ElMessageBox.confirm(
      '确定要退出登录吗?',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(async () => {
      await authStore.logoutUser()
      router.push('/login')
    }).catch(() => {})
  } else if (command === 'profile') {
    router.push('/profile')
  }
}
</script>

<style scoped>
.app-container {
  height: 100vh;
}

.layout-container {
  height: 100%;
}

.aside {
  background-color: #304156;
  color: #ffffff;
  transition: width 0.3s;
  overflow-x: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #263445;
}

.logo h1 {
  color: #ffffff;
  font-size: 18px;
  margin: 0;
  white-space: nowrap;
}

.el-menu-vertical {
  border-right: none;
}

.main-container {
  width: 100%;
  height: 100%;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #ebeef5;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left,
.header-right {
  display: flex;
  align-items: center;
}

.toggle-btn {
  font-size: 20px;
  cursor: pointer;
  margin-right: 20px;
}

.dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
  font-size: 14px;
}

.main {
  background-color: #f0f2f5;
  padding: 20px;
  height: calc(100vh - 60px);
  overflow-y: auto;
}
</style> 