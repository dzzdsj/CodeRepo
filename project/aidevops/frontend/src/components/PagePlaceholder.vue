<template>
  <el-card>
    <div class="placeholder">
      <el-icon :size="40" color="var(--el-color-primary)">
        <component :is="icon" />
      </el-icon>
      <h2>{{ title }}</h2>
      <p class="desc">模块建设中，敬请期待</p>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import type { Component } from 'vue'
import { Document } from '@element-plus/icons-vue'

const route = useRoute()

const title = computed(() => (route.meta.title as string) ?? '页面')
const icon = computed<Component>(() => (route.meta.icon as Component) ?? Document)
</script>

<style scoped>
.placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 60px 0;
  color: var(--el-text-color-secondary);
}
.placeholder h2 {
  margin: 0;
  color: var(--el-text-color-primary);
}
.desc {
  margin: 0;
}
</style>
