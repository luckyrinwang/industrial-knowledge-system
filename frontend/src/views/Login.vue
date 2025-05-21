<template>
  <div class="login-bg">
    <div class="login-container">
      <div class="login-box">
        <div class="login-title">
          <img src="/logo192.png" alt="logo" class="login-logo" />
          <h2>工业知识库系统</h2>
        </div>
        <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" class="login-form">
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              prefix-icon="el-icon-user"
              placeholder="用户名"
              size="large"
              clearable
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              prefix-icon="el-icon-lock"
              type="password"
              placeholder="密码"
              show-password
              size="large"
              clearable
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              :loading="loading"
              class="login-button"
              @click="handleLogin"
              size="large"
            >
              登录
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const loginFormRef = ref(null)

// 登录表单数据
const loginForm = reactive({
  username: '',
  password: ''
})

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
  ]
}

// 登录方法
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await authStore.loginUser(loginForm.username, loginForm.password)
        ElMessage.success('登录成功')
        
        // 跳转到首页
        router.push('/dashboard/home')
      } catch (error) {
        const message = error.response?.data?.message || '登录失败，请检查网络连接'
        ElMessage.error(message)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-bg {
  min-height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-box {
  width: 420px;
  padding: 40px 36px 32px 36px;
  background: rgba(255,255,255,0.98);
  border-radius: 18px;
  box-shadow: 0 8px 32px 0 rgba(30,60,114,0.18);
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: fadeIn 0.8s;
}

.login-title {
  text-align: center;
  margin-bottom: 32px;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.login-logo {
  width: 56px;
  height: 56px;
  margin-bottom: 10px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(30,60,114,0.12);
}
.login-title h2 {
  font-weight: 700;
  font-size: 26px;
  color: #1e3c72;
  letter-spacing: 2px;
}
.login-form {
  width: 100%;
  margin-bottom: 18px;
}
.login-button {
  width: 100%;
  background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
  border: none;
  font-weight: 600;
  letter-spacing: 1px;
  transition: box-shadow 0.2s, transform 0.2s;
  box-shadow: 0 2px 8px rgba(30,60,114,0.10);
}
.login-button:hover {
  transform: translateY(-2px) scale(1.03);
  box-shadow: 0 6px 18px rgba(30,60,114,0.18);
}
.login-tips {
  text-align: center;
  font-size: 15px;
  color: #409EFF;
  margin-top: 10px;
  background: rgba(64,158,255,0.08);
  border-radius: 8px;
  padding: 8px 0;
  width: 100%;
  letter-spacing: 1px;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>