<template>
  <div class="user-management-bg">
    <div class="user-management-container">
      <div class="page-header">
        <div class="header-left">
          <el-icon class="header-icon"><UserFilled /></el-icon>
          <h2>用户管理</h2>
        </div>
        <el-button type="primary" class="add-user-btn" @click="handleAddUser">
          <el-icon><plus /></el-icon>
          新增用户
        </el-button>
      </div>
      <!-- 脱机模式提示 -->
      <el-alert
        v-if="offlineMode"
        title="当前处于脱机模式，数据变更仅在本地有效，未保存到服务器"
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 15px"
      />
      <!-- 用户列表 -->
      <el-card shadow="always" class="user-table-card">
        <el-table
          :data="users"
          border
          stripe
          style="width: 100%"
          v-loading="loading"
          class="user-table"
        >
          <el-table-column prop="id" label="ID" width="80" align="center"/>
          <el-table-column prop="username" label="用户名" width="150" align="center"/>
          <el-table-column prop="email" label="邮箱" align="center"/>
          <el-table-column prop="full_name" label="姓名" width="150" align="center">
            <template #default="scope">
              <span>{{ scope.row.full_name || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="角色" width="200" align="center">
            <template #default="scope">
              <el-tag
                v-for="role in scope.row.roles"
                :key="role"
                :type="getRoleType(role)"
                size="small"
                effect="dark"
                style="margin-right: 5px"
              >
                {{ role }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100" align="center">
            <template #default="scope">
              <el-tag :type="scope.row.is_active ? 'success' : 'danger'" effect="plain">
                {{ scope.row.is_active ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" align="center">
            <template #default="scope">
              <el-button-group>
                <el-button 
                  size="small"
                  @click="handleEditUser(scope.row)"
                  :disabled="scope.row.username === 'admin' && userInfo.username !== 'admin'"
                  type="primary"
                  plain
                >
                  编辑
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  plain
                  @click="handleDeleteUser(scope.row)"
                  :disabled="scope.row.username === 'admin' || scope.row.id === userInfo.id"
                >
                  删除
                </el-button>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>
        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            background
            layout="total, sizes, prev, pager, next"
            :page-sizes="[10, 20, 50, 100]"
            :total="total"
            :page-size="pageSize"
            :current-page="currentPage"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
      <!-- 用户表单对话框 -->
      <el-dialog
        v-model="dialogVisible"
        :title="isEdit ? '编辑用户' : '新增用户'"
        width="480px"
        class="user-dialog"
      >
        <el-form
          ref="userFormRef"
          :model="userForm"
          :rules="userRules"
          label-width="80px"
          class="user-form"
        >
          <el-form-item label="用户名" prop="username" v-if="!isEdit">
            <el-input v-model="userForm.username" placeholder="请输入用户名" clearable size="large" />
          </el-form-item>
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="userForm.email" placeholder="请输入邮箱" clearable size="large" />
          </el-form-item>
          <el-form-item label="密码" prop="password" v-if="!isEdit">
            <el-input v-model="userForm.password" type="password" show-password placeholder="请输入密码" clearable size="large" />
          </el-form-item>
          <el-form-item label="姓名" prop="full_name">
            <el-input v-model="userForm.full_name" placeholder="请输入姓名" clearable size="large" />
          </el-form-item>
          <el-form-item label="状态" prop="is_active">
            <el-switch
              v-model="userForm.is_active"
              active-text="启用"
              inactive-text="禁用"
            />
          </el-form-item>
          <el-form-item label="角色" prop="roles">
            <el-checkbox-group v-model="userForm.roles">
              <el-checkbox v-for="role in roleOptions" :key="role.name" :label="role.name">
                {{ role.description }}
              </el-checkbox>
            </el-checkbox-group>
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" @click="submitUserForm" :loading="submitting">
              确定
            </el-button>
          </span>
        </template>
      </el-dialog>
    </div>
  </div>
</template>


<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/store/auth'
import { getUsers, createUser, updateUser, deleteUser, getRoles } from '@/api/user'
import { Plus, UserFilled } from '@element-plus/icons-vue'

// 用户列表数据
const users = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const userFormRef = ref(null)
const userInfo = ref({})
const offlineMode = ref(false) // 是否处于脱机模式

// 本地用户数据备份（在API未成功连接时使用）
const mockUsers = [
  {
    id: 1,
    username: 'admin',
    email: 'admin@example.com',
    full_name: '系统管理员',
    is_active: true,
    roles: ['admin'],
    created_at: new Date().toISOString()
  }
]

// 角色选项
const roleOptions = ref([
  { name: 'admin', description: '管理员' },
  { name: 'editor', description: '编辑' },
  { name: 'user', description: '普通用户' }
])

// 用户表单
const userForm = reactive({
  id: null,
  username: '',
  email: '',
  password: '',
  full_name: '',
  is_active: true,
  roles: []
})

// 表单验证规则
const userRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
  ],
  roles: [
    { type: 'array', required: true, message: '请至少选择一个角色', trigger: 'change' }
  ]
}

// 获取当前用户信息
onMounted(() => {
  // 尝试从localStorage获取用户信息
  const storedUser = localStorage.getItem('user') || localStorage.getItem('userInfo')
  if (storedUser) {
    try {
      userInfo.value = JSON.parse(storedUser)
    } catch (error) {
      console.error('解析用户信息失败:', error)
      // 创建一个默认的管理员用户信息
      userInfo.value = {
        id: 1,
        username: 'admin',
        roles: ['admin']
      }
      // 保存到localStorage
      localStorage.setItem('user', JSON.stringify(userInfo.value))
    }
  } else {
    // 创建一个默认的管理员用户信息
    userInfo.value = {
      id: 1,
      username: 'admin',
      roles: ['admin']
    }
    // 保存到localStorage
    localStorage.setItem('user', JSON.stringify(userInfo.value))
  }
  
  fetchUsers()
  fetchRoles()
})

// 获取角色类型样式
const getRoleType = (role) => {
  switch (role) {
    case 'admin':
      return 'danger'
    case 'editor':
      return 'warning'
    default:
      return 'info'
  }
}

// 获取用户列表
const fetchUsers = async () => {
  loading.value = true
  try {
    const response = await getUsers(currentPage.value, pageSize.value)
    users.value = response.items
    total.value = response.total
    offlineMode.value = false // 成功连接到后端，设置为在线模式
  } catch (error) {
    console.error('获取用户列表失败:', error.response?.data || error)
    ElMessage.warning('无法连接到后端服务，使用本地数据显示')
    
    // 使用本地数据
    users.value = mockUsers
    total.value = mockUsers.length
    offlineMode.value = true // 设置为脱机模式
  } finally {
    loading.value = false
  }
}

// 获取角色列表
const fetchRoles = async () => {
  try {
    const response = await getRoles()
    if (response && response.length > 0) {
      roleOptions.value = response.map(role => ({
        name: role.name,
        description: role.description || role.name
      }))
    }
  } catch (error) {
    console.error('获取角色列表失败', error)
  }
}

// 处理页码变化
const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchUsers()
}

// 处理每页数量变化
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchUsers()
}

// 新增用户
const handleAddUser = () => {
  isEdit.value = false
  resetUserForm()
  dialogVisible.value = true
}

// 编辑用户
const handleEditUser = (row) => {
  isEdit.value = true
  resetUserForm()
  userForm.id = row.id
  userForm.username = row.username
  userForm.email = row.email
  userForm.full_name = row.full_name || ''
  userForm.is_active = row.is_active
  userForm.roles = row.roles || []
  dialogVisible.value = true
}

// 删除用户
const handleDeleteUser = (row) => {
  ElMessageBox.confirm(`确定要删除用户 "${row.username}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteUser(row.id)
      ElMessage.success('删除成功')
      fetchUsers()
    } catch (error) {
      console.error('删除用户失败:', error.response?.data || error)
      ElMessage.warning('无法连接到后端服务，在本地进行模拟操作')
      
      // 本地模拟删除
      const index = mockUsers.findIndex(u => u.id === row.id)
      if (index !== -1) {
        mockUsers.splice(index, 1)
        users.value = mockUsers
        total.value = mockUsers.length
        ElMessage.success('已在本地删除（未保存到服务器）')
      }
    }
  }).catch(() => {})
}

// 重置表单
const resetUserForm = () => {
  userForm.id = null
  userForm.username = ''
  userForm.email = ''
  userForm.password = ''
  userForm.full_name = ''
  userForm.is_active = true
  userForm.roles = []
  if (userFormRef.value) {
    userFormRef.value.resetFields()
  }
}

// 提交用户表单
const submitUserForm = async () => {
  if (!userFormRef.value) return
  
  await userFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEdit.value) {
          // 编辑用户
          const { username, ...updateData } = userForm
          await updateUser(userForm.id, updateData)
          ElMessage.success('用户更新成功')
        } else {
          // 新增用户
          await createUser(userForm)
          ElMessage.success('用户创建成功')
        }
        
        dialogVisible.value = false
        fetchUsers()
      } catch (error) {
        console.error('用户操作失败:', error.response?.data || error)
        ElMessage.warning('无法连接到后端服务，在本地进行模拟操作')
        
        // 本地模拟操作
        if (isEdit.value) {
          // 编辑用户
          const index = mockUsers.findIndex(u => u.id === userForm.id)
          if (index !== -1) {
            mockUsers[index] = {
              ...mockUsers[index],
              ...userForm,
              updated_at: new Date().toISOString()
            }
          }
        } else {
          // 新增用户
          const newUser = {
            ...userForm,
            id: mockUsers.length > 0 ? Math.max(...mockUsers.map(u => u.id)) + 1 : 1,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          }
          mockUsers.push(newUser)
        }
        
        dialogVisible.value = false
        users.value = mockUsers
        total.value = mockUsers.length
        ElMessage.success('操作已在本地完成（未保存到服务器）')
      } finally {
        submitting.value = false
      }
    }
  })
}
</script>

<style scoped>
.user-management-bg {
  min-height: 80vh;
  width: 80vw;
  background: linear-gradient(135deg, #f5f7fa 0%, #e3eafc 100%);
  padding: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.user-management-container {
  width: 100%;
  max-width: 1100px;
  margin: 0 auto;
  padding: 32px 0 32px 0;
  box-sizing: border-box;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.header-icon {
  font-size: 32px;
  color: #1e3c72;
  background: #e3eafc;
  border-radius: 8px;
  padding: 4px;
  box-shadow: 0 2px 8px rgba(30,60,114,0.10);
}
.page-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #1e3c72;
  letter-spacing: 1px;
}
.add-user-btn {
  font-weight: 600;
  letter-spacing: 1px;
  border-radius: 8px;
  padding: 0 18px;
}
.user-table-card {
  border-radius: 16px;
  box-shadow: 0 4px 24px 0 rgba(30,60,114,0.10);
  margin-bottom: 32px;
}
.user-table {
  border-radius: 12px;
  overflow: hidden;
}
.el-table th {
  background: linear-gradient(90deg, #e3eafc 0%, #f5f7fa 100%);
  color: #1e3c72;
  font-weight: 600;
  font-size: 15px;
}
.el-table td {
  font-size: 15px;
}
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
.user-dialog >>> .el-dialog__header {
  background: linear-gradient(90deg, #e3eafc 0%, #f5f7fa 100%);
  border-radius: 12px 12px 0 0;
}
.user-dialog >>> .el-dialog__body {
  padding-top: 18px;
  padding-bottom: 0;
}
.user-form {
  padding: 0 8px;
}
.user-form .el-form-item {
  margin-bottom: 18px;
}
.user-form .el-input {
  border-radius: 8px;
}
.user-form .el-checkbox-group {
  display: flex;
  gap: 12px;
}
.user-form .el-checkbox {
  font-size: 15px;
}
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 8px 0 2px 0;
}
@media (max-width: 900px) {
  .user-management-container {
    max-width: 98vw;
    padding: 16px 2vw 16px 2vw;
  }
  .user-table-card {
    padding: 0;
  }
  .page-header h2 {
    font-size: 18px;
  }
  .header-icon {
    font-size: 24px;
    padding: 2px;
  }
}
</style>