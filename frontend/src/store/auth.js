import { defineStore } from 'pinia'
import { login, logout } from '../api/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user') || 'null')
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => {
      if (!state.user) return false
      
      return state.user.is_superadmin || 
             (state.user.roles && state.user.roles.includes('admin'))
    },
    currentUser: (state) => state.user
  },
  
  actions: {
    async loginUser(username, password) {
      try {
        const response = await login(username, password)
        this.token = response.access_token
        this.user = response.user
        
        // 保存到本地存储
        localStorage.setItem('token', this.token)
        localStorage.setItem('user', JSON.stringify(this.user))
        
        return true
      } catch (error) {
        this.clearAuth()
        throw error
      }
    },
    
    async logoutUser() {
      try {
        if (this.token) {
          await logout()
        }
      } catch (error) {
        console.error('登出错误', error)
      } finally {
        this.clearAuth()
      }
    },
    
    clearAuth() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },
    
    hasPermission(permission) {
      if (!this.user) return false
      if (this.user.is_superadmin) return true
      
      // TODO: 实现根据用户角色判断权限的逻辑
      return false
    }
  }
}) 