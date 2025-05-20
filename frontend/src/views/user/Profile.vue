<template>
  <div class="profile-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>个人中心</h2>
        </div>
      </template>
      <div class="profile-content">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="用户名">{{ user.username }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ user.email }}</el-descriptions-item>
          <el-descriptions-item label="角色">{{ userRoles }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useAuthStore } from "@/store/auth";

const authStore = useAuthStore();
const user = computed(() => authStore.currentUser || {});
const userRoles = computed(() => {
  if (user.value.is_superadmin) return "超级管理员";
  return user.value.roles?.join(", ") || "普通用户";
});
</script>

<style scoped>
.profile-container {
  max-width: 800px;
  margin: 0 auto;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.profile-content {
  margin-top: 20px;
}
</style> 