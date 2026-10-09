<script setup lang="ts">
// import HelloWorld from './components/HelloWorld.vue'
import { useCounterStore } from './stores/counter'

const counterStore = useCounterStore()
</script>

<template>
  <nav>
    <RouterLink to="/">
      首页
    </RouterLink>

    <RouterLink to="/users">
      用户管理
    </RouterLink>
  </nav>

  <RouterView />

  <div>
    <h1>Counter</h1>

    <p>当前数量：{{ counterStore.count }}</p>
    <button @click="counterStore.increment">
      +1
    </button>
        <button @click="counterStore.decrement">
      -1
    </button>

    <button @click="counterStore.reset">
      Reset
    </button>
    <p>
      {{ counterStore.isEven ? '偶数' : '奇数' }}
    </p>
  </div>
</template>
