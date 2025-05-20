<template>
  <div class="role-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>角色管理</h2>
          <el-button type="primary" @click="handleAdd">添加角色</el-button>
        </div>
      </template>
      
      <el-table
        v-loading="userStore.loading"
        :data="userStore.roles"
        border
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="角色名称" width="150" />
        <el-table-column prop="description" label="描述" />
        <el-table-column label="权限" min-width="300">
          <template #default="scope">
            <el-tag
              v-for="permission in scope.row.permissions"
              :key="permission"
              class="permission-tag"
            >
              {{ permission }}
            </el-tag>
            <span v-if="!scope.row.permissions || scope.row.permissions.length === 0">无权限</span>
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
              @click="handleDelete(scope.row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted } from "vue";
import { useUserStore } from "@/store/user";
import { ElMessage } from "element-plus";

const userStore = useUserStore();

onMounted(async () => {
  await userStore.fetchRoles();
  await userStore.fetchPermissions();
});

const handleAdd = () => {
  ElMessage.info("添加角色功能待实现");
};

const handleEdit = (row) => {
  ElMessage.info("编辑角色功能待实现");
};

const handleDelete = (row) => {
  ElMessage.info("删除角色功能待实现");
};
</script>

<style scoped>
.role-management {
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
.permission-tag {
  margin-right: 5px;
  margin-bottom: 5px;
}
</style> 