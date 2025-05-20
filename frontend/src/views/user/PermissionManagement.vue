<template>
  <div class="permission-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>权限管理</h2>
          <el-button type="primary" @click="handleAdd">添加权限</el-button>
        </div>
      </template>
      
      <el-table
        v-loading="userStore.loading"
        :data="userStore.permissions"
        border
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="权限名称" width="200" />
        <el-table-column prop="description" label="描述" />
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
  await userStore.fetchPermissions();
});

const handleAdd = () => {
  ElMessage.info("添加权限功能待实现");
};

const handleEdit = (row) => {
  ElMessage.info("编辑权限功能待实现");
};

const handleDelete = (row) => {
  ElMessage.info("删除权限功能待实现");
};
</script>

<style scoped>
.permission-management {
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
</style> 