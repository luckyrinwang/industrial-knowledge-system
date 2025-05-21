<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <div class="avatar-box">
            <el-avatar :size="64" icon="el-icon-user-solid" style="background: linear-gradient(135deg, #6fa1f7 0%, #a1e3ff 100%); color: #fff; font-size: 32px;">
              {{ userInfo.full_name ? userInfo.full_name[0] : (userInfo.username ? userInfo.username[0] : 'U') }}
            </el-avatar>
          </div>
          <div class="header-title-box">
            <h3>个人信息</h3>
            <div class="header-sub">完善您的个人资料，提升账户安全性</div>
          </div>
          <el-button type="primary" size="small" @click="editMode = true" v-if="!editMode">
            <el-icon><Edit /></el-icon> 编辑资料
          </el-button>
        </div>
      </template>

      <div v-if="!editMode" class="user-info">
        <el-descriptions :column="1" border size="small">
          <el-descriptions-item label="用户名">
            <el-tag type="info" effect="plain">{{ userInfo.username }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="邮箱">
            <el-tag type="success" effect="plain">{{ userInfo.email }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="姓名">
            <el-tag v-if="userInfo.full_name" type="primary" effect="plain">{{ userInfo.full_name }}</el-tag>
            <span v-else class="text-muted">未设置</span>
          </el-descriptions-item>
          <el-descriptions-item label="角色">
            <el-tag type="warning" effect="plain">{{ userRoles }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="注册时间">
            <span v-if="userInfo.created_at">
              {{ formatDate(userInfo.created_at) || userInfo.created_at }}
              <span class="text-muted">（{{ timeAgo(userInfo.created_at) }}）</span>
            </span>
            <span v-else>--</span>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <el-form 
        v-else
        ref="profileFormRef"
        :model="profileForm"
        :rules="formRules"
        label-width="80px"
        class="profile-edit-form"
      >
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="profileForm.email" placeholder="请输入邮箱" clearable prefix-icon="el-icon-message" />
        </el-form-item>
        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="profileForm.full_name" placeholder="请输入姓名" clearable prefix-icon="el-icon-user" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="updateProfile" :loading="loading"><el-icon><Check /></el-icon> 保存</el-button>
          <el-button @click="cancelEdit"><el-icon><Close /></el-icon> 取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="password-card">
      <template #header>
        <div class="card-header">
          <el-icon style="margin-right:8px;"><Lock /></el-icon>
          <h3>修改密码</h3>
        </div>
      </template>

      <el-form 
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="100px"
        class="password-form"
      >
        <el-form-item label="原密码" prop="old_password">
          <el-input
            v-model="passwordForm.old_password"
            type="password"
            show-password
            placeholder="请输入原密码"
            prefix-icon="el-icon-lock"
          />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="passwordForm.new_password"
            type="password"
            show-password
            placeholder="请输入新密码"
            prefix-icon="el-icon-key"
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input
            v-model="passwordForm.confirm_password"
            type="password"
            show-password
            placeholder="请再次输入新密码"
            prefix-icon="el-icon-key"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="changePassword" :loading="loading">
            <el-icon><Refresh /></el-icon> 修改密码
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
/* 个人中心美化样式 */
.profile-container {
  max-width: 600px;
  margin: 32px auto 0 auto;
  padding-bottom: 32px;
}

.profile-card, .password-card {
  margin-bottom: 24px;
  border-radius: 14px;
  box-shadow: 0 4px 24px 0 rgba(64,158,255,0.08);
  border: none;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 18px;
  padding-bottom: 4px;
}

.avatar-box {
  margin-right: 10px;
}

.header-title-box {
  flex: 1;
}

.header-title-box h3 {
  margin: 0 0 2px 0;
  font-size: 22px;
  font-weight: 600;
  color: #222;
}

.header-sub {
  font-size: 13px;
  color: #8a99b3;
}

.user-info {
  padding: 18px 0 6px 0;
}

.el-descriptions {
  background: #f8fafc;
  border-radius: 8px;
  padding: 10px 0 0 0;
}

.el-descriptions__label {
  color: #6c7a89;
  font-weight: 500;
}

.el-tag {
  font-size: 13px;
  padding: 0 10px;
}

.text-muted {
  color: #b0b8c9;
  font-size: 13px;
}

.profile-edit-form {
  padding: 18px 0 6px 0;
}

.profile-edit-form .el-input {
  max-width: 320px;
}

.profile-edit-form .el-button {
  min-width: 90px;
}

.password-card {
  background: linear-gradient(135deg, #f8fbff 0%, #eaf6ff 100%);
}

.password-form {
  padding: 18px 0 6px 0;
}

.password-form .el-input {
  max-width: 320px;
}

.password-form .el-button {
  min-width: 120px;
}
</style> 