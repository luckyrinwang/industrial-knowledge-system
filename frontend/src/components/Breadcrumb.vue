<template>
  <el-breadcrumb separator="/">
    <el-breadcrumb-item v-for="(item, index) in breadcrumbs" :key="index" :to="item.path">
      {{ item.title }}
    </el-breadcrumb-item>
  </el-breadcrumb>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const breadcrumbs = ref([])

// 路由映射表
const routeMap = {
  '/': { title: '首页' },
  '/users': { title: '用户管理' },
  '/roles': { title: '角色管理' },
  '/permissions': { title: '权限管理' },
  '/profile': { title: '个人中心' },
  '/knowledge/search': { title: '知识检索' },
  '/knowledge/manage': { title: '知识管理' }
}

// 根据路由生成面包屑
const generateBreadcrumbs = (path) => {
  const result = []
  
  // 首页始终是第一个
  result.push({ path: '/', title: '首页' })
  
  // 如果不是首页，则添加当前页面
  if (path !== '/') {
    const pathSegments = path.split('/').filter(Boolean)
    let currentPath = ''
    
    for (let i = 0; i < pathSegments.length; i++) {
      currentPath += '/' + pathSegments[i]
      
      if (routeMap[currentPath]) {
        result.push({
          path: currentPath,
          title: routeMap[currentPath].title
        })
      }
    }
  }
  
  return result
}

// 监听路由变化
watch(
  () => route.path,
  (path) => {
    breadcrumbs.value = generateBreadcrumbs(path)
  },
  { immediate: true }
)
</script>

<style scoped>
.el-breadcrumb {
  line-height: 1;
}
</style> 