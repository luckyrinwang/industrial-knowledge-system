import { defineStore } from 'pinia'
import { 
  getUsers, getUser, createUser, updateUser, deleteUser,
  getRoles, getRole, createRole, updateRole, deleteRole,
  getPermissions, getPermission, createPermission, updatePermission, deletePermission
} from '../api/user'

export const useUserStore = defineStore('user', {
  state: () => ({
    users: [],
    roles: [],
    permissions: [],
    totalUsers: 0,
    totalPages: 1,
    currentPage: 1,
    loading: false,
    error: null
  }),
  
  actions: {
    // 用户管理
    async fetchUsers(page = 1, perPage = 10) {
      this.loading = true
      try {
        const response = await getUsers(page, perPage)
        this.users = response.users
        this.totalUsers = response.total
        this.totalPages = response.pages
        this.currentPage = page
        this.error = null
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
    
    async addUser(userData) {
      this.loading = true
      try {
        await createUser(userData)
        await this.fetchUsers(this.currentPage)
        this.error = null
        return true
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async editUser(userId, userData) {
      this.loading = true
      try {
        await updateUser(userId, userData)
        await this.fetchUsers(this.currentPage)
        this.error = null
        return true
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async removeUser(userId) {
      this.loading = true
      try {
        await deleteUser(userId)
        await this.fetchUsers(this.currentPage)
        this.error = null
        return true
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 角色管理
    async fetchRoles() {
      this.loading = true
      try {
        const response = await getRoles()
        this.roles = response
        this.error = null
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
    
    async addRole(roleData) {
      this.loading = true
      try {
        await createRole(roleData)
        await this.fetchRoles()
        this.error = null
        return true
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async editRole(roleId, roleData) {
      this.loading = true
      try {
        await updateRole(roleId, roleData)
        await this.fetchRoles()
        this.error = null
        return true
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async removeRole(roleId) {
      this.loading = true
      try {
        await deleteRole(roleId)
        await this.fetchRoles()
        this.error = null
        return true
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 权限管理
    async fetchPermissions() {
      this.loading = true
      try {
        const response = await getPermissions()
        this.permissions = response
        this.error = null
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
    
    async addPermission(permissionData) {
      this.loading = true
      try {
        await createPermission(permissionData)
        await this.fetchPermissions()
        this.error = null
        return true
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async editPermission(permissionId, permissionData) {
      this.loading = true
      try {
        await updatePermission(permissionId, permissionData)
        await this.fetchPermissions()
        this.error = null
        return true
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async removePermission(permissionId) {
      this.loading = true
      try {
        await deletePermission(permissionId)
        await this.fetchPermissions()
        this.error = null
        return true
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    }
  }
}) 