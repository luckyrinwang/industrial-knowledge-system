<template>
  <div class="app-container">
    <el-container class="layout-container">
      <!-- 侧边栏 -->
      <el-aside
        width="220px"
        class="aside"
        :collapse="isCollapse"
        @mouseenter="handleMouseEnter"
        @mouseleave="handleMouseLeave"
      >
        <div class="logo">
          <img src="/logo192.png" class="logo-img" alt="logo" />
          <h1 v-show="!isCollapse">工业知识库系统</h1>
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

          <el-sub-menu index="/knowledge">
            <template #title>
              <el-icon><document /></el-icon>
              <span>知识库</span>
            </template>
            <el-menu-item index="/knowledge/search">
              <el-icon><search /></el-icon>
              <span>知识检索</span>
            </el-menu-item>
            <el-menu-item index="/knowledge/manage">
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
        <el-header class="header">
          <div class="header-left">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
              <el-breadcrumb-item v-if="$route.meta.title">{{ $route.meta.title }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <div class="header-right">
            <el-dropdown trigger="click" @command="handleCommand">
              <span class="dropdown-link">
                {{ authStore.currentUser?.username }}
                <el-icon class="el-icon--right"><arrow-down /></el-icon>
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

const isCollapse = ref(true)

const activeMenu = computed(() => route.path)

const handleMouseEnter = () => {
  isCollapse.value = false
}
const handleMouseLeave = () => {
  isCollapse.value = true
}

const handleCommand = (command) => {
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(async () => {
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
  background: linear-gradient(135deg, #263445 0%, #304156 100%);
  transition: width 0.3s ease-in-out;
  overflow-x: hidden;
}
.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding-left: 18px;
  gap: 12px;
}
.logo-img {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: #e3eafc;
}
.logo h1 {
  color: #ffffff;
  font-size: 18px;
  font-weight: 700;
  margin: 0;
  white-space: nowrap;
}
.el-menu-vertical {
  border-right: none;
  background: transparent;
  padding-top: 8px;
}
.el-menu-vertical:not(.el-menu--collapse) .el-sub-menu__title span,
.el-menu-vertical:not(.el-menu--collapse) .el-menu-item span {
  opacity: 1;
  transition: opacity 0.3s ease;
}
.el-menu--collapse .el-sub-menu__title span,
.el-menu--collapse .el-menu-item span {
  opacity: 0;
  transition: opacity 0.2s ease;
}
.el-menu-vertical .el-menu-item,
.el-menu-vertical .el-sub-menu__title {
  border-radius: 8px;
  margin: 4px 10px;
  font-size: 16px;
  font-weight: 500;
}
.el-menu-vertical .el-menu-item.is-active,
.el-menu-vertical .el-menu-item:hover,
.el-menu-vertical .el-sub-menu__title:hover {
  background: linear-gradient(90deg, #409EFF 0%, #1e3c72 100%);
  transform: scale(1.04);
}
.main-container {
  width: 100%;
  height: 100%;
}
.header {
  background: linear-gradient(to right, #ffffff, #f0f5ff);
  border-bottom: 1px solid #dcdfe6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 60px;
}
.header-left,
.header-right {
  display: flex;
  align-items: center;
}
.dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
  font-size: 15px;
  font-weight: 500;
  color: #303133;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background 0.2s;
}
.dropdown-link:hover {
  background: rgba(64, 158, 255, 0.1);
}
.main {
  background-color: #f0f2f5;
  padding: 20px;
  height: calc(100vh - 60px);
  overflow-y: auto;
}
</style>
