<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <h3>个人信息</h3>
          <el-button type="primary" size="small" @click="editMode = true" v-if="!editMode">
            编辑资料
          </el-button>
        </div>
      </template>
      
      <div v-if="!editMode" class="user-info">
        <div class="info-item">
          <span class="label">用户名：</span>
          <span>{{ userInfo.username }}</span>
        </div>
        <div class="info-item">
          <span class="label">邮箱：</span>
          <span>{{ userInfo.email }}</span>
        </div>
        <div class="info-item">
          <span class="label">姓名：</span>
          <span>{{ userInfo.full_name || '未设置' }}</span>
        </div>
        <div class="info-item">
          <span class="label">角色：</span>
          <span>{{ userRoles }}</span>
        </div>
        <div class="info-item">
          <span class="label">注册时间：</span>
          <span v-if="userInfo.created_at">
            {{ formatDate(userInfo.created_at) || userInfo.created_at }}
            <span style="color:#999;font-size:12px;">（{{ timeAgo(userInfo.created_at) }}）</span>
          </span>
          <span v-else>--</span>
        </div>
      </div>
      
      <el-form 
        v-else
        ref="profileFormRef"
        :model="profileForm"
        :rules="formRules"
        label-width="80px"
      >
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="profileForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="profileForm.full_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="updateProfile">保存</el-button>
          <el-button @click="cancelEdit">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card class="password-card">
      <template #header>
        <div class="card-header">
          <h3>修改密码</h3>
        </div>
      </template>
      
      <el-form 
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="100px"
      >
        <el-form-item label="原密码" prop="old_password">
          <el-input
            v-model="passwordForm.old_password"
            type="password"
            show-password
            placeholder="请输入原密码"
          />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="passwordForm.new_password"
            type="password"
            show-password
            placeholder="请输入新密码"
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input
            v-model="passwordForm.confirm_password"
            type="password"
            show-password
            placeholder="请再次输入新密码"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="changePassword" :loading="loading">
            修改密码
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { formatDate, timeAgo } from '@/utils/date'

// 新增：获取用户信息API
const fetchProfile = async () => {
  try {
    const res = await axios.get('/api/auth/profile', {
      headers: {
        Authorization: 'Bearer ' + localStorage.getItem('token')
      }
    })
    userInfo.value = res.data
    // 初始化编辑表单
    profileForm.email = userInfo.value.email || ''
    profileForm.full_name = userInfo.value.full_name || ''
  } catch (e) {
    ElMessage.error('获取用户信息失败')
  }
}

// 用户信息
const userInfo = ref({})
// 编辑模式
const editMode = ref(false)
// 加载状态
const loading = ref(false)
// 表单引用
const profileFormRef = ref(null)
const passwordFormRef = ref(null)

// 个人信息表单
const profileForm = reactive({
  email: '',
  full_name: ''
})

// 密码表单
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 用户角色
const userRoles = computed(() => {
  if (!userInfo.value.roles || userInfo.value.roles.length === 0) {
    return '无'
  }
  return userInfo.value.roles.join(', ')
})

// 表单验证规则
const formRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  full_name: [
    { max: 50, message: '姓名长度不能超过50个字符', trigger: 'blur' }
  ]
}

// 密码验证规则
const passwordRules = {
  old_password: [
    { required: true, message: '请输入原密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 获取用户信息
onMounted(() => {
  fetchProfile()
})

// 取消编辑
const cancelEdit = () => {
  editMode.value = false
  profileForm.email = userInfo.value.email || ''
  profileForm.full_name = userInfo.value.full_name || ''
}

// 更新个人信息
const updateProfile = async () => {
  if (!profileFormRef.value) return
  
  await profileFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        // 获取token
        const token = localStorage.getItem('token')
        
        // 发送更新请求
        const response = await axios.put(`/api/users/${userInfo.value.id}`, profileForm, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        })
        
        // 更新本地存储的用户信息
        userInfo.value = response.data.user
        localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
        
        // 保存成功后刷新用户信息
        await fetchProfile()
        editMode.value = false
      } catch (error) {
        const message = error.response?.data?.message || '更新失败，请稍后再试'
        ElMessage.error(message)
      } finally {
        loading.value = false
      }
    }
  })
}

// 修改密码
const changePassword = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        // 获取token
        const token = localStorage.getItem('token')
        
        // 发送修改密码请求
        await axios.post('/api/auth/change-password', {
          old_password: passwordForm.old_password,
          new_password: passwordForm.new_password
        }, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        })
        
        ElMessage.success('密码修改成功')
        // 清空密码表单
        passwordForm.old_password = ''
        passwordForm.new_password = ''
        passwordForm.confirm_password = ''
      } catch (error) {
        const message = error.response?.data?.message || '密码修改失败，请稍后再试'
        ElMessage.error(message)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.profile-container {
  max-width: 800px;
  margin: 0 auto;
}

.profile-card, .password-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
}

.user-info {
  padding: 10px 0;
}

.info-item {
  margin-bottom: 15px;
  line-height: 1.5;
}

.label {
  font-weight: bold;
  color: #606266;
  margin-right: 10px;
  display: inline-block;
  width: 80px;
}
</style> 