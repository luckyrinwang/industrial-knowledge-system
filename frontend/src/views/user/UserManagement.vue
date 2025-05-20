<template>
  <div class="user-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>用户管理</h2>
          <el-button type="primary" @click="handleAdd">添加用户</el-button>
        </div>
      </template>
      
      <el-table
        v-loading="userStore.loading"
        :data="userStore.users"
        border
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column label="状态" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="管理员" width="120">
          <template #default="scope">
            <el-tag v-if="scope.row.is_superadmin" type="warning">超级管理员</el-tag>
            <el-tag v-else-if="hasAdminRole(scope.row)" type="info">管理员</el-tag>
            <span v-else>否</span>
          </template>
        </el-table-column>
        <el-table-column label="角色" min-width="200">
          <template #default="scope">
            <el-tag
              v-for="role in scope.row.roles"
              :key="role"
              class="role-tag"
            >
              {{ role }}
            </el-tag>
            <span v-if="!scope.row.roles || scope.row.roles.length === 0">无角色</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button
              size="small"
              type="primary"
              @click="handleEdit(scope.row)"
            >
              编辑
            </el-button>
            <el-button
              size="small"
              type="danger"
              :disabled="scope.row.id === authStore.currentUser?.id"
              @click="handleDelete(scope.row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="userStore.totalUsers"
          layout="total, prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
    
    <!-- 用户表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑用户' : '添加用户'"
      width="500px"
    >
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userRules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item v-if="!isEdit" label="密码" prop="password">
          <el-input v-model="userForm.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item v-else label="密码" prop="password">
          <el-input v-model="userForm.password" type="password" placeholder="不修改请留空" show-password />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="userForm.is_active" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select
            v-model="userForm.roles"
            multiple
            placeholder="请选择角色"
            style="width: 100%"
          >
            <el-option
              v-for="role in userStore.roles"
              :key="role.id"
              :label="role.name"
              :value="role.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="管理员">
          <el-switch
            v-model="userForm.is_superadmin"
            :disabled="currentUserId === userForm.id"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useUserStore } from '@/store/user'
import { useAuthStore } from '@/store/auth'
import { ElMessage, ElMessageBox } from 'element-plus'

const userStore = useUserStore()
const authStore = useAuthStore()
const currentPage = ref(1)
const pageSize = ref(10)
const dialogVisible = ref(false)
const isEdit = ref(false)
const userFormRef = ref(null)
const submitting = ref(false)
const currentEditId = ref(null)

// 当前用户ID
const currentUserId = computed(() => authStore.currentUser?.id)

// 用户表单
const userForm = reactive({
  username: '',
  email: '',
  password: '',
  is_active: true,
  is_superadmin: false,
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
    { required: !isEdit.value, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }
  ]
}

// 检查用户是否具有管理员角色
const hasAdminRole = (user) => {
  return user.roles && user.roles.includes('admin')
}

// 加载用户数据
onMounted(async () => {
  await userStore.fetchUsers(currentPage.value, pageSize.value)
  await userStore.fetchRoles()
})

// 页码变化处理
const handlePageChange = (page) => {
  currentPage.value = page
  userStore.fetchUsers(page, pageSize.value)
}

// 添加用户
const handleAdd = () => {
  isEdit.value = false
  currentEditId.value = null
  resetForm()
  dialogVisible.value = true
}

// 编辑用户
const handleEdit = (row) => {
  isEdit.value = true
  currentEditId.value = row.id
  
  // 填充表单
  userForm.username = row.username
  userForm.email = row.email
  userForm.password = '' // 编辑时不回显密码
  userForm.is_active = row.is_active
  userForm.is_superadmin = row.is_superadmin
  
  // 转换角色ID
  if (row.roles && Array.isArray(row.roles)) {
    userForm.roles = userStore.roles
      .filter(role => row.roles.includes(role.name))
      .map(role => role.id)
  } else {
    userForm.roles = []
  }
  
  dialogVisible.value = true
}

// 删除用户
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除用户 "${row.username}" 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await userStore.removeUser(row.id)
      ElMessage.success('删除成功')
    } catch (error) {
      ElMessage.error(`删除失败: ${error.message}`)
    }
  }).catch(() => {})
}

// 提交表单
const submitForm = async () => {
  if (!userFormRef.value) return
  
  try {
    await userFormRef.value.validate()
    
    submitting.value = true
    const userData = { ...userForm }
    
    // 如果密码为空且为编辑模式，则移除密码字段
    if (isEdit.value && !userData.password) {
      delete userData.password
    }
    
    if (isEdit.value) {
      await userStore.editUser(currentEditId.value, userData)
      ElMessage.success('用户更新成功')
    } else {
      await userStore.addUser(userData)
      ElMessage.success('用户添加成功')
    }
    
    dialogVisible.value = false
  } catch (error) {
    console.error('表单验证失败:', error)
  } finally {
    submitting.value = false
  }
}

// 重置表单
const resetForm = () => {
  userForm.username = ''
  userForm.email = ''
  userForm.password = ''
  userForm.is_active = true
  userForm.is_superadmin = false
  userForm.roles = []
  
  if (userFormRef.value) {
    userFormRef.value.resetFields()
  }
}
</script>

<style scoped>
.user-management {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 18px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.role-tag {
  margin-right: 5px;
  margin-bottom: 5px;
}
</style> 