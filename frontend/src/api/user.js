import request from '@/utils/request'

// 用户管理 API
export function getUsers(page = 1, perPage = 10) {
  return request({
    url: '/api/users/',
    method: 'get',
    params: { page, per_page: perPage }
  })
}

export function getUser(userId) {
  return request({
    url: `/api/users/${userId}`,
    method: 'get'
  })
}

export function createUser(data) {
  return request({
    url: '/api/users/',
    method: 'post',
    data
  })
}

export function updateUser(userId, data) {
  return request({
    url: `/api/users/${userId}`,
    method: 'put',
    data
  })
}

export function deleteUser(userId) {
  return request({
    url: `/api/users/${userId}`,
    method: 'delete'
  })
}

// 角色管理 API
export function getRoles() {
  return request({
    url: '/api/users/roles',
    method: 'get'
  })
}

export function getRole(roleId) {
  return request({
    url: `/api/users/roles/${roleId}`,
    method: 'get'
  })
}

export function createRole(data) {
  return request({
    url: '/api/users/roles',
    method: 'post',
    data
  })
}

export function updateRole(roleId, data) {
  return request({
    url: `/api/users/roles/${roleId}`,
    method: 'put',
    data
  })
}

export function deleteRole(roleId) {
  return request({
    url: `/api/users/roles/${roleId}`,
    method: 'delete'
  })
}

// 权限管理 API
export function getPermissions() {
  return request({
    url: '/api/users/permissions',
    method: 'get'
  })
}

export function getPermission(permissionId) {
  return request({
    url: `/api/users/permissions/${permissionId}`,
    method: 'get'
  })
}

export function createPermission(data) {
  return request({
    url: '/api/users/permissions',
    method: 'post',
    data
  })
}

export function updatePermission(permissionId, data) {
  return request({
    url: `/api/users/permissions/${permissionId}`,
    method: 'put',
    data
  })
}

export function deletePermission(permissionId) {
  return request({
    url: `/api/users/permissions/${permissionId}`,
    method: 'delete'
  })
} 