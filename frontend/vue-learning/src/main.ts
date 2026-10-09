import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
// createApp(App).mount('#app')
const app = createApp(App)

app.use(router)
app.use(createPinia())
app.mount('#app')
