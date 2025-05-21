// src/main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './assets/style/main.css'
import { useAuthStore } from './stores/authStore' // 1.引入我们写好的authStore

import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

import App from './App.vue'
import router from './router'


const app = createApp(App)
const pinia = createPinia() 

app.use(ElementPlus)
app.use(router)
app.use(pinia) // 确保在pinia实例创建后使用

const authStore = useAuthStore(pinia) // 2. 创建authStore实例


authStore.tryAutoLogin() // 3. 在应用加载时尝试自动登录

app.mount('#app')