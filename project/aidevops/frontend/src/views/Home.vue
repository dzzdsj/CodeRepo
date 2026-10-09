<template>
  <el-card>
    <h2>欢迎使用 AIDevOps</h2>
    <p>AI赋能研发运维辅助系统 — 脚手架已就绪。</p>
    <p>后端健康检查：<el-tag>{{ health }}</el-tag></p>
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import axios from 'axios'

const health = ref('检测中...')

onMounted(async () => {
  try {
    const res = await axios.get('/api/v1/health')
    health.value = res.data?.status ?? 'unknown'
  } catch {
    health.value = '后端未启动'
  }
})
</script>
