<template>
  <el-container class="layout">
    <el-header class="header">
      <span class="title">AIDevOps 研发运维辅助系统</span>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
// 布局骨架，后续按模块扩展侧边栏导航
</script>

<style scoped>
.layout {
  min-height: 100vh;
}
.header {
  display: flex;
  align-items: center;
  border-bottom: 1px solid var(--el-border-color);
}
.title {
  font-size: 18px;
  font-weight: 600;
}
</style>
