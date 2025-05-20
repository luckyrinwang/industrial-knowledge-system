import { createRouter, createWebHistory } from 'vue-router'

// 路由配置
const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard/home'
      },
      {
        path: 'home',
        name: 'Home',
        component: () => import('../views/Home.vue'),
        meta: { title: '首页', requiresAuth: true }
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: () => import('../views/UserManagement.vue'),
        meta: { title: '用户管理', requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'files',
        name: 'FileManagement',
        component: () => import('../views/FileManagement.vue'),
        meta: { title: '文件管理', requiresAuth: true }
      },
      {
        path: 'logs',
        name: 'OperationLogs',
        component: () => import('../views/OperationLogs.vue'),
        meta: { title: '操作日志', requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('../views/Profile.vue'),
        meta: { title: '个人中心', requiresAuth: true }
      },
      {
        path: 'knowledge',
        name: 'Knowledge',
        component: () => import('../views/Knowledge.vue'),
        meta: { title: '知识库', requiresAuth: true }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 导航守卫
router.beforeEach((to, from, next) => {
  // 暂时禁用认证检查，直接允许所有路由访问
  // next() // 注释掉或删除这一行，以启用下面的认证逻辑
  
  // 以下是原有的认证逻辑
  const token = localStorage.getItem('token')
  const userInfo = JSON.parse(localStorage.getItem('user') || '{}')
  // 确保 userInfo 和 userInfo.roles 存在，避免运行时错误
  const isAdmin = userInfo && userInfo.roles && userInfo.roles.includes('admin')
  
  // 检查页面是否需要认证
  if (to.meta.requiresAuth && !token) {
    next({ name: 'Login' }) // 如果没有token且页面需要认证，则跳转到登录页
  } 
  // 检查页面是否需要管理员权限
  else if (to.meta.requiresAdmin && !isAdmin) {
    // 如果需要管理员权限但当前用户不是管理员，则跳转到首页
    next({ name: 'Home' }) 
  } 
  else {
    next() // 其他情况允许访问
  }
})

export default router