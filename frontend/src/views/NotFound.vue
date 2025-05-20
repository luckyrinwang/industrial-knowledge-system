<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <h1>404</h1>
      <h2>页面不存在</h2>
      <p>您访问的页面不存在或已被删除</p>
      <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
    </div>
  </div>
</template>

<style scoped>
.not-found-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}

.not-found-content {
  text-align: center;
  padding: 40px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.not-found-content h1 {
  font-size: 72px;
  color: #409eff;
  margin: 0 0 20px;
}

.not-found-content h2 {
  font-size: 24px;
  margin: 0 0 20px;
  color: #303133;
}

.not-found-content p {
  margin: 0 0 30px;
  color: #606266;
}
</style>
