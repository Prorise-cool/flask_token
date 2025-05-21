## 第四章: 全栈 Token 认证 – Vue.js 前端与 Flask 后端实现用户注册登录

在本章中，我们将构建一个完整的用户注册和登录认证流程。前端将采用我们在第三章搭建的 Vue 3 技术栈（Vite 构建，集成 Element Plus、Tailwind CSS 和 DaisyUI+pinia），负责用户界面和 API 交互逻辑。Flask 后端则提供认证 API，并通过 `Flask-JWT-Extended` 库来签发和验证 JSON Web Tokens (JWT)。Token 相关的核心概念和安全考量将在实际的编码实现过程中穿插讲解。

**本章目标：**

  * 构建美观且用户友好的前端注册和登录表单界面。
  * 实现前端调用后端 API 进行用户注册和登录的完整逻辑。
  * 深入理解如何在前端安全地存储、管理和发送从后端获取的 JWT。
  * 掌握 Flask 后端 API 如何处理用户注册请求，并安全地（当前为内存）存储用户凭证（哈希密码）。
  * 掌握 Flask 后端 API 如何处理用户登录请求，并签发 JWT Access Token 和 Refresh Token。
  * 实现一个受 Token 保护的后端 API，并确保前端在用户认证后能够成功访问该 API。
  * 全面理解 Token 在现代前后端分离应用认证流程中的核心作用、生命周期管理及相关安全实践。

#### 8.1 前端准备：构建注册与登录界面 (Vue.js)

我们将首先创建用户交互的界面和基础的前端路由。

##### 8.1.1 创建 Vue 组件: `Register.vue` 与 `Login.vue`

在 Vue 项目 `frontend/src/components/` 目录下创建或修改以下两个组件。

1.  **`Register.vue`**: 用户注册组件

```vue
<template>
    <div class="container mx-auto h-screen flex items-center justify-center">
        <div class="form-container">
            <form class="form">
                <p class="form-title">注册您的账户</p>
                <div class="form-control w-full max-w-xs">
                    <label class="floating-label">
                        <span>邮箱</span>
                    <input type="email" id="email" placeholder="请输入邮箱" v-model="form.username"
                            class="input input-bordered w-full">
                    </label>
                </div>
                <div class="form-control w-full max-w-xs mt-4">
                    <label class="floating-label">
                        <span>密码</span>
                        <input type="password" id="password" placeholder="请输入密码" v-model="form.password"
                            class="input input-bordered w-full">
                    </label>
                </div>
            <button type="submit" class="btn btn-neutral w-full mt-6" @click.prevent="handleRegister">
                    注册
                </button>

                <p class="signup-link mt-4 text-center">
                    已有账户？
                    <router-link to="/login"
                        class="text-blue-500 hover:text-blue-600 cursor-pointer underline">登录</router-link>
                </p>
            </form>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import authService from '../apis/authService';



const form = ref({
    username: '',
password: '',
});

const router = useRouter();

const handleRegister = async () => {
    // TODO：连接注册函数
}

</script>


<style lang="scss" scoped>
.form-container {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    
.form {
        width: 90%;
        max-width: 400px;
        background-color: #fff;
        display: block;
        padding: 2rem;
    border-radius: 0.75rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);

    &-title {
        font-size: 1.25rem;
        line-height: 1.75rem;
        font-weight: 600;
        text-align: center;
    color: #000;
    }

    button {
    outline: none;
        border: 1px solid #e5e7eb;
        margin: 8px 0;
    }
}
}


.signup-link {
    color: #6B7280;
    font-size: 0.875rem;
    line-height: 1.25rem;
    text-align: center;

    a {
        text-decoration: underline;
}
}
</style>

```

2.  **`Login.vue`**: 用户登录组件

```vue
<template>
    <div class="container mx-auto h-screen flex items-center justify-center">
        <div class="form-container">
            <form class="form">
                <p class="form-title">登录您的账户</p>
                <div class="form-control w-full max-w-xs">
                    <label class="floating-label">
                        <span>邮箱</span>
                        <input type="email" id="email" placeholder="请输入邮箱" v-model="form.username"
                            class="input input-bordered w-full">
                    </label>
                </div>
                <div class="form-control w-full max-w-xs mt-4">
                    <label class="floating-label">
                        <span>密码</span>
                        <input type="password" id="password" placeholder="请输入密码" v-model="form.password"
                            class="input input-bordered w-full">
                    </label>
                </div>
                <button type="submit" class="btn btn-primary w-full mt-6" @click.prevent="handleLogin">
                    登录
                </button>

                <p class="signup-link mt-4 text-center">
                    没有账户？
                    <router-link to="/register"
                        class="text-blue-500 hover:text-blue-600 cursor-pointer underline">注册</router-link>
                </p>
            </form>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElNotification } from 'element-plus';
const form = ref({ username: '', password: '' });
 
    
    
</script>

<style lang="scss" scoped>
.form-container {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    
    .form {
        width: 90%;
        max-width: 400px;
        background-color: #fff;
        display: block;
        padding: 2rem;
        border-radius: 0.75rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);

    &-title {
        font-size: 1.25rem;
        line-height: 1.75rem;
        font-weight: 600;
        text-align: center;
        color: #000;
    }

    button {
        outline: none;
        border: 1px solid #e5e7eb;
        margin: 8px 0;
    }
}
}


.signup-link {
    color: #6B7280;
    font-size: 0.875rem;
    line-height: 1.25rem;
    text-align: center;

    a {
        text-decoration: underline;
    }
}
</style>
```








##### 8.1.2 配置前端路由 (Vue Router)

确保你的 `frontend/src/router/index.js` 文件包含登录和注册页面的路由，并可以添加一个简单的个人资料页面（`Profile.vue`）用于后续测试受保护的路由。

> pnpm install vue-router@4

``` js

import { createRouter, createWebHistory } from 'vue-router'
import Register from '../components/Register.vue'
import Login from '../components/Login.vue'

// 路由配置
const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

```

在main.js中导入路由

``` js
// src/main.js
import {
    createApp
} from 'vue'
import './assets/style/main.css' // 引入 tailwindcss 样式

import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css' // 引入 Element Plus 的 CSS

import App from './App.vue'
import router from './router' // 导入路由配置

const app = createApp(App)

app.use(ElementPlus) // 注册 Element Plus 插件
app.use(router) // 使用路由
app.mount('#app')
```



1.  **创建 `frontend/src/views/ProfileView.vue` (简单的个人资料页占位符)**
```vue
<template>
    <div class="p-8">
        <h1 class="text-3xl font-bold text-gray-700"> 用户中心 </h1>
        <div v-if="user" class="mt-4 p-4 bg-gray-100 rounded shadow">
            <p class="text-lg"> 欢迎, <span class="font-semibold">{{ user.username }}</span>! </p>
            <p class="text-sm text-gray-600 mt-2"> 这是您的个人资料页面。</p>
            <button @click="handleLogout" class="btn btn-warning btn-sm mt-4"> 登出 </button>
            
            <!-- 文件展示区域 - 瀑布流布局 -->
            <div class="mt-6">
                <h2 class="text-xl font-semibold mb-4"> 我的文件 </h2>
                <div class="waterfall-wrapper">
                    <div v-for="file in files" :key="file.source" class="waterfall-item">
                        <div class="group overflow-hidden rounded-lg bg-gray-100 focus-within:ring-2 focus-within:ring-indigo-500 focus-within:ring-offset-2 focus-within:ring-offset-gray-100">
                            < img
                                alt = ""
                                : src = "file.source"
                                class = "pointer-events-none w-full object-cover group-hover: opacity-75"
                            />
                            <button type="button" class="absolute inset-0 focus:outline-none">
                                <span class="sr-only"> 查看详情: {{ file.title }}</span>
                            </button>
                        </div>
                        <p class="pointer-events-none mt-2 block truncate text-sm font-medium text-gray-900">{{ file.title }}</p>
                        <p class="pointer-events-none block text-sm font-medium text-gray-500">{{ file.size }}</p>
                    </div>
                </div>
            </div>
        </div>
        <div v-else>
            <p> 请先 <router-link :to="{ name: 'Login' }" class="link link-primary"> 登录 </router-link>。</p>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
// import { useAuthStore } from '../stores/authStore'; // 稍后引入

const user = ref(null);
const router = useRouter();
// const authStore = useAuthStore(); // 稍后引入

// 文件数据
const files = ref([]);

// 生成随机文件大小
const generateRandomSize = () => {
    const size = (Math.random() * 5 + 1).toFixed(1);
    return `${size} MB`;
};

// 生成随机文件名
const generateRandomFileName = () => {
    const prefix = 'IMG_';
    const number = Math.floor(Math.random() * 9000) + 1000;
    return `${prefix}${number}.HEIC`;
};

// 使用 Picsum Photos 获取随机图片
const getRandomImage = (index) => {
    // 使用不同的随机 ID 获取不同的图片
    const randomId = Math.floor(Math.random() * 1000) + 100;
    return `https://picsum.photos/id/${randomId}/512/512`;
};

// 初始化文件数据
const initializeFiles = () => {
    const fileCount = Math.floor(Math.random() * 50) + 3; // 生成 50 个文件
    const tempFiles = [];
    
    for (let i = 0; i < fileCount; i++) {
        tempFiles.push({
            title: generateRandomFileName(),
            size: generateRandomSize(),
            source: getRandomImage(i),
        });
    }
    
    files.value = tempFiles;
};

// 调用初始化函数
initializeFiles();

onMounted(() => {
    // TODO: 从状态管理或 localStorage 获取用户信息 (将在 8.7 节实现)
    // 暂时让他为 True
    user.value = true;
});

const handleLogout = () => {
    user.value = null;
    router.push({ name: 'Login' });
};
</script>

<style scoped>
/* 瀑布流布局样式 */
.waterfall-wrapper {
    column-count: 4; /* 默认 4 列 */
    column-gap: 16px;
}

.waterfall-item {
    break-inside: avoid; /* 防止内容被折断 */
    margin-bottom: 16px;
    position: relative;
}
</style>
```



1.  **更新 `frontend/src/router/index.js`**
```js
import { createRouter, createWebHistory } from 'vue-router'
import Register from '../components/Register.vue'
import Login from '../components/Login.vue'
import Profile from '../views/ProfileVaiew.vue'

// 路由配置
const routes = [
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { guestOnly: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { guestOnly: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})
export default router
```

**3.创建导航栏组件`src/layout/Navigation.vue`**

```vue
<template>
    <div>
        <nav class="bg-gray-800">
            <div class="mx-auto max-w-7xl px-2 sm:px-6 lg:px-8">
                <div class="relative flex h-16 items-center justify-between">
                    <div class="absolute inset-y-0 left-0 flex items-center sm:hidden">
                        <!-- Mobile menu button-->
                        <button @click="toggleMobileMenu"
                            class="relative inline-flex items-center justify-center rounded-md p-2 text-gray-400 hover:bg-gray-700 hover:text-white focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white">
                            <span class="absolute -inset-0.5"></span>
                            <span class="sr-only">Open main menu</span>
                            <!-- 菜单图标 -->
                            <span v-if="!mobileMenuOpen" class="block h-6 w-6">☰</span>
                            <span v-else class="block h-6 w-6">✕</span>
                        </button>
                    </div>
                    <div class="flex flex-1 items-center justify-center sm:items-stretch sm:justify-start">
                        <div class="flex shrink-0 items-center">
                            <img class="h-8 w-auto" src="../assets/images/user.png" alt="" />
                        </div>
                        <div class="hidden sm:ml-6 sm:block">
                            <div class="flex space-x-4">
                                <a v-for="item in navigation" :key="item.name" :href="item.href"
                                    :class="[item.current ? 'bg-gray-900 text-white' : 'text-gray-300 hover:bg-gray-700 hover:text-white', 'rounded-md px-3 py-2 text-sm font-medium']">
                                    {{ item.name }}</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div v-if="mobileMenuOpen" class="sm:hidden">
                <div class="space-y-1 px-2 pb-3 pt-2">
                    <router-link v-for="item in navigation" :key="item.name" :to="item.href"
                        :class="[item.current ? 'bg-gray-900 text-white' : 'text-gray-300 hover:bg-gray-700 hover:text-white', 'block rounded-md px-3 py-2 text-base font-medium']">
                        {{ item.name }}</router-link>
                </div>
            </div>
        </nav>

        <!-- 路由视图 -->
        <router-view />
    </div>
</template>

<script setup>
import { ref } from 'vue'

const mobileMenuOpen = ref(false)

const toggleMobileMenu = () => {
    mobileMenuOpen.value = !mobileMenuOpen.value
}

const navigation = [
    { name: '首页', href: '/', current: true },
    { name: '登录', href: '/login', current: false },
    { name: '注册', href: '/register', current: false },
    { name: '个人中心', href: '/profile', current: false },
]
</script>
```

##### 8.1.3 在 `App.vue` 中使用 `<router-view/>`

确保你的 `frontend/src/App.vue` 包含 `<router-view/>` 以渲染当前路由匹配的组件。包含一个导航栏。

``` vue
<template>
  <Navigation />
</template>

<script setup>
import Navigation from './layout/Navigation.vue'

</script>
```

#### 8.2 前端API服务层封装 (`axios`)

为了使API请求更易于管理和维护，我们创建一个服务层。

##### 8.2.1 安装 `axios`

如果尚未安装：

``` bash
cd frontend
pnpm add axios
```

##### 8.2.2 创建API服务文件 `frontend/src/utils/http.js` (配置基础实例)

``` javascript
// frontend/src/utils/http.js
import axios from 'axios';

const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

export default apiClient;
```

确保在 `frontend/.env.development` (或 `.env`) 文件中定义 `VITE_API_BASE_URL`：

``` env
VITE_API_BASE_URL = http://127.0.0.1:5000/api
```

##### 8.2.3 创建 `frontend/src/apis/authService.js`

``` javascript
// frontend/src/apis/authService.js
import apiClient from "../utils/http"

export default {
    register(userData) {
        // userData: { username, password }
        return apiClient.post('/auth/register', userData);
    },

    login(credentials) {
        // credentials: { username, password }
        return apiClient.post('/auth/login', credentials);
    },

    // 登出接口 (如果后端实现了 Token 吊销)
    logout() {
        // 假设后端有一个 /auth/logout 接口来吊销 Token
        // 注意: 即使调用失败，前端也应该清理本地 Token
        return apiClient.delete('/auth/logout');
    },

    // 获取用户资料 (受保护的接口)
    getProfile() {
        return apiClient.get('/me'); // 假设后端有一个 /me 接口
    },

    // 刷新 Token (将在 8.8 节实现)
    refreshToken() {
        const currentRefreshToken = localStorage.getItem('refresh_token');
        if (!currentRefreshToken) {
            return Promise.reject(new Error("没有可用的刷新令牌"));
        }
        // Refresh token 通常通过 POST 请求发送，有时在 body 中，有时也用 Authorization Bearer 头部
        // Flask-JWT-Extended @jwt_required(refresh = True) 默认期望它在 Authorization Bearer 头部
        return apiClient.post('/auth/refresh', {}, { // body 可以为空，因为 refresh token 在头部
            headers: {
                'Authorization': `Bearer ${currentRefreshToken}`
            }
        });
    }
};
```

##### 8.2.4 配置前端反向代理与全局路径别名（最重要）

在`vite.config.js`文件中配置跨域请求

```js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'), // 配置 @ 指向 src 目录
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})

```

前端部分的基础框架和API调用逻辑已经就绪。现在，我们可以开始实现Flask后端的对应API。

#### 8.3 后端实现：用户注册API (Flask)

我们回到 `backend/app.py` 文件。

##### 8.3. `/api/auth/register` 端点

``` python
# backend/app.py
from datetime import timedelta
import os

from flask import Flask, request, jsonify  # 确保 request 已导入
from flask_cors import CORS
from flask_jwt_extended import JWTManager  # create_access_token 等函数稍后导入
from pyexpat.errors import messages
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
# 引入我们基础篇章用到的日志库
from loguru import logger  # 导入 Loguru


# from datetime import timedelta # 如果需要配置 token 有效期

load_dotenv()
app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "default-super-secret-key-for-dev")  # 设置 JWT 密钥
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)  # 设置访问令牌的有效期为 15 分钟
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)  # 设置刷新令牌的有效期为 7 天
app.config["JWT_BLACKLIST_ENABLED"] = True  # 为后续登出吊销 Token 做准备
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access", "refresh"]  # 检查吊销的 Token 类型

CORS(app, resources={r"/api/*": {" origins ": "*"}})  # 允许所有来源访问/api/*路径
jwt = JWTManager(app)

# 简易内存用户存储和 Token 黑名单
users_in_memory_store: dict[str, dict] = {}
TOKEN_BLOCKLIST: set[str] = set()  # 为后续登出吊销 Token 做准备


# --- Token 知识点：密码哈希 ---
# 永远不要存储明文密码！密码必须经过哈希处理。
# 哈希是将任意长度的输入通过哈希算法转换成固定长度的输出（哈希值）。
# 好的哈希算法具有以下特点：
# 1. 单向性：从哈希值很难（计算上不可行）反推出原始输入。
# 2. 抗碰撞性：很难找到两个不同的输入产生相同的哈希值。
# 3. 雪崩效应：原始输入的微小改变会导致哈希值巨大变化。
# `werkzeug.security.generate_password_hash` 会自动使用安全的哈希算法（如 scrypt 或 pbkdf2_sha256）并加入“盐”（salt），
# “盐”是一个随机数据，与密码结合后再进行哈希，使得相同的密码也会产生不同的哈希值，能有效抵抗彩虹表攻击。
@app.route('/api/auth/register', methods=['POST'])
def register_user_api() -> tuple[jsonify, int]:
    data = request.get_json()
    if not data:
        return jsonify({"messages": "请求体不能为空且必须为Json格式"}), 400

    username: str = data.get("username")
    password: str = data.get("password")

    if not username or not password:
        return jsonify({"messages": "用户名和密码不能为空"}), 400
    if len(password) < 6:
        return jsonify({"messages": "密码不能少于六位数！"}), 400

    if not username.strip():  # 去除字符串开头和结尾的空白字符
        return jsonify({"messages": "用户名不能全为空白字符！"}), 400

    if username in users_in_memory_store:
        return jsonify({"messages": f"用户名 {username}已存在"}), 400

    hashed_password = generate_password_hash(password)
    users_in_memory_store[username] = {"hashed_password": hashed_password}
    logger.info(f"用户 '{username}' 注册成功。当前用户池: {users_in_memory_store}")
    return jsonify({"message": "注册成功", "status": 200}), 201

if __name__ == '__main__':
    app.run(debug=True)
```

我们简单的实现了注册接口，现在他会像前端产出一个Json字符串，我们将服务引入登录插件试试

```vue
<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import authService from '../apis/authService';
import { ElNotification } from 'element-plus';

const form = ref({
    username: '',
    password: '',
});

const router = useRouter();
const handleRegister = async () => {
    try {
        const response = await authService.register(form.value);
        console.log("response====>>>>>>", response);
        
        if (response.data.status == 200) {
            ElNotification({
                title: '注册成功',
                message: '请登录您的账户',
                type: 'success',
            });
            router.push('/login');
        } else {
            ElNotification({
                title: '注册失败',
                message: response.data.message,
                type: 'error',
            });
        }
    } catch (error) {
        if (error.response && error.response.status === 400) {
            // 显示后端返回的具体错误信息
            ElNotification({
                title: '注册失败',
                message: error.response.data.message || '请检查输入信息',
                type: 'error',
            });
        } else {
            ElNotification({
                title: '网络错误',
                message: '请稍后重试',
                type: 'error',
            });
        }
        console.error('注册失败:', error);
    }
}

</script>
```

#### 8.4 后端实现：用户登录API与Token签发 (Flask)

##### 8.4.1 `/api/auth/login` 端点

此端点验证用户凭证，如果成功，则签发Access Token和Refresh Token。

``` python
@app.route("/api/auth/login", methods=["POST"])
def login_user_pai() -> tuple[jsonify, int]:
    data = request.get_json()
    if not data:
        return jsonify({"messages": "请求体不能为空且必须为Json格式"}), 400

    username: str = data.get("username")
    password: str = data.get("password")

    if not username or not password:
        return jsonify({"messages": "用户名和密码不能为空"}), 400

    user_data = users_in_memory_store.get(username)

    # --- Token 知识点：密码验证 ---
    # 使用 `check_password_hash` 来比较用户输入的密码（会自动哈希）与存储的哈希值。
    # 不能直接比较明文密码或自己哈希后再比较，因为盐值不同会导致相同明文密码的哈希值也不同
    if user_data and check_password_hash(user_data["hashed_password"], password):
        # --- Token 知识点：Token的两个核心函数与参数 ---
        # 1. `identity`: 唯一标识用户。可以是用户 ID、用户名等。它将成为 JWT Payload 中 `sub` (Subject)声明的值。
        # 2. `fresh=True`: 表示这个 Access Token 是通过用户直接输入凭证获得的，是“新鲜的”。
        #    某些敏感操作可能要求 Token 必须是新鲜的。
        # 3. `create_access_token`: 生成寿命较短的 Access Token，用于访问受保护资源。
        # 4. `create_refresh_token`: 生成寿命较长的 Refresh Token，用于在 Access Token 过期后获取新的 Access Token。
        access_token: str = create_access_token(identity=username, fresh=True)
        refresh_token: str = create_refresh_token(identity=username)

        return jsonify({
            "messages": f"用户登录成功",
            "status": 200,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {"username": username}
        }), 200
    return jsonify({"messages": "用户名或密码错误"}), 401
```

在实现了后端的登录端点后，我们回到前端进行api的对接....

```js
<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import authService from '../apis/authService';

const form = ref({
    username: '',
    password: '',
});

// 使用 Vue Router 的 useRouter 钩子来获取路由实例
const router = useRouter();

// 处理登录的方法
const handleLogin = async () => {
    try {
        const response = await authService.login(form.value);
        
        if (response.data.status == 200) {
            // 下面是临时方案，要改掉的！
            localStorage.setItem('access_token', response.data.access_token);
            localStorage.setItem('refresh_token', response.data.refresh_token);
            router.push('/profile');
        } else {
            console.error('登录失败:', response.data.message);
        }
    } catch (error) {
        console.error('登录失败:', error);
    }
}
</script>
```

在处理前端持久化存储时，我们来完善一下路由守卫的设计与axios的请求拦截器与响应拦截器

##### 8.4.2 前端路由守卫与axios拦截器封装

修改`router/index.js`的内容如下：

```js
import { createRouter, createWebHistory } from 'vue-router'
import Register from '../components/Register.vue'
import Login from '../components/Login.vue'
import Profile from '../views/ProfileVaiew.vue'

// 路由配置
const routes = [
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { guestOnly: true } // 仅限未登录用户访问
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { guestOnly: true } // 仅限未登录用户访问
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true } // 需要认证
  },

]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由前台守卫：当用户访问需要认证的页面时，如果未登录，则重定向到登录页
// 全局前置导航守卫
// 每次路由跳转时都会触发此函数
// to: 即将要进入的目标路由对象
// from: 当前导航正要离开的路由对象
// next: 钩子函数，确定下一步的路由导航
//   - next(): 放行，继续导航
//   - next('/path'): 中断当前导航，跳转到指定路径
//   - next({ name: 'routeName' }): 中断当前导航，跳转到命名路由
//   - next(false): 中断当前导航，回到 from 路由
//   - next(error): 导航终止并触发 router.onError() 注册过的回调

router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth); // 是否需要认证
  const guestOnly = to.matched.some(record => record.meta.guestOnly); // 是否仅限未登录用户访问
  
  // Token知识点: 客户端身份验证状态检查
  // 实际应用中，我们会检查Token的有效性，而不仅仅是它是否存在。
  // 这里使用localStorage作为简化的Token存储示例。
    // 两个!!是指：如果localStorage.getItem('access_token')为空，则返回false，否则返回true
  const isAuthenticated = !!localStorage.getItem('access_token');

  if (requiresAuth && !isAuthenticated) {
    // 如果目标路由需要认证，但用户未认证，则重定向到登录页
    next({ name: 'Login', query: { redirect: to.fullPath } });
  } else if (guestOnly && isAuthenticated) {
    // 如果目标路由仅限未登录用户访问（如登录/注册页），但用户已认证，则重定向到个人资料页
    next({ name: 'Profile' }); 
  } else {
    // 其他情况，正常导航
    next();
  }
});

export default router

```

封装全局axios响应拦截器

```js
// Token 知识点: Axios 请求拦截器 - 自动添加 Authorization 头部
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Token 知识点: Axios 响应拦截器 - 处理 Token 过期和刷新
apiClient.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error) => {
        const originalRequest = error.config;
        if (error.response && error.response.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            console.log('Token 过期或无效');
            localStorage.removeItem('access_token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

```





-----

#### 8.5 前端Token处理与Pinia状态管理 (Vue.js)

在前端应用中，当用户登录并从后端获取到 Tokens (Access Token 和 Refresh Token) 后，需要一种健壮且集中的方式来存储这些 Tokens，并在整个应用中管理用户的认证状态。Pinia，作为Vue官方推荐的状态管理库，为此提供了优秀的解决方案。它能帮助我们响应式地管理状态，并使组件间的状态共享变得简单。

##### 8.5.1 Token知识点回顾：客户端Token存储策略

在实现具体的 Pinia store 之前，简要回顾客户端存储Token的常见策略：

  * **`localStorage`**: 数据持久，除非主动清除或浏览器策略限制，否则会一直存在。跨浏览器标签页共享。主要缺点是易受XSS攻击。
  * **`sessionStorage`**: 数据仅在当前浏览器标签页的会话期间有效，关闭标签页即清除。同样易受XSS攻击。
  * **内存中 (例如，通过Pinia的state)**: 这是最安全的方式，因为JavaScript不能轻易跨域访问其他脚本的内存。但主要缺点是当用户刷新页面或关闭标签页时，内存中的状态会丢失。
  * **`HttpOnly` Cookie**: 由服务器设置，JavaScript无法访问，因此能有效防御XSS攻击。浏览器会自动在每次请求时携带。缺点是需要后端API配合，并且需要处理CSRF攻击的风险。

**我们的策略**：我们将结合使用 Pinia 的内存状态和 `localStorage`。Pinia store 将作为应用内部获取认证状态和 Tokens 的主要数据源 。`localStorage` 则用于持久化这些关键信息，以便在用户刷新页面或重新打开应用时能够恢复认证状态。

##### 8.5.2 安装与配置 Pinia

1.  **安装 Pinia**
    如果尚未在 `frontend` 目录中安装 Pinia，请执行：

    ```bash
    pnpm add pinia
    ```

2.  **在 `frontend/src/main.js` 中创建并使用 Pinia 实例**
    确保 Pinia 实例被创建并提供给Vue应用。
    
    ```js
    // src/main.js
    import { createApp } from 'vue'
    import { createPinia } from 'pinia' // 引入Pinia
    import './assets/style/main.css'
    
    
    import ElementPlus from 'element-plus'
    import 'element-plus/dist/index.css'
    
    import App from './App.vue'
    import router from './router'
    
    
    const app = createApp(App)
    const pinia = createPinia() // 创建pinia示例
    
    app.use(ElementPlus)
    app.use(router)
    app.use(pinia) // 确保在pinia实例创建后使用
    
    
    
    app.mount('#app')
    ```
    
    

##### 8.5.3 创建认证相关的 Pinia Store (`authStore.js`)

这是管理认证状态的核心。在 `frontend/src/stores/` 目录下创建 `authStore.js` 文件。

```javascript
// frontend/src/stores/authStore.js
import { defineStore } from 'pinia';
import authApiService from '../apis/authService'; // 引入之前创建的authService
import apiClient from '../utils/http'; // 引入axios实例以便更新默认头部
import router from '../router'; // 引入router实例用于导航


export const useAuthStore = defineStore('auth', {
    state: () => ({
        accessToken: localStorage.getItem('access_token') || null,
        refreshToken: localStorage.getItem('refresh_token') || null,
        user: JSON.parse(localStorage.getItem('user')) || null, // 用户信息，如 { username: 'test' }
    }),

    // Getters：计算属性，用于方便地获取状态
    getters: {
        isAuthenticated: (state) => !!state.accessToken, // 判断是否已认证
        currentUser: (state) => state.user, // 当前用户信息
        getAccessToken: (state) => state.accessToken, // 获取accessToken
        getRefreshToken: (state) => state.refreshToken, // 获取refreshToken
    },

    // Actions：包含异步操作和修改状态的逻辑
    actions: {
        // 清理认证相关的状态和localStorage
        clearAuthData() {
            this.accessToken = null;
            this.refreshToken = null;
            this.user = null;

            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');

            // 清除axios实例的默认Authorization头部
            delete apiClient.defaults.headers.common['Authorization'];
        },

        // 在应用加载时尝试从localStorage恢复会话
        tryAutoLogin() {
            const token = localStorage.getItem('access_token');
            const storedUser = localStorage.getItem('user');
            const storedRefreshToken = localStorage.getItem('refresh_token');

            if (token && storedUser) {
                this.accessToken = token;
                this.user = JSON.parse(storedUser);
                this.refreshToken = storedRefreshToken;
                apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
                return true; // 表示自动登录成功
            }
            return false; // 表示自动登录失败
        },

        // 当通过刷新机制获取到新的Access Token时，调用此action更新状态
        setNewAccessToken(newAccessToken) {
            this.accessToken = newAccessToken;
            localStorage.setItem('access_token', newAccessToken);
            apiClient.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`;
        },

        // 用于在获取到新的用户信息后更新store和localStorage
        updateUser(userData) {
            this.user = userData
            localStorage.setItem('user', JSON.stringify(this.user));
        },

        // 从后端API获取用户资料并更新store
        async fetchAndSetUser() {
            try {
                const response = await authApiService.getProfile();
                console.log("获取用户资料:", response);
                if (response && response.data) {
                    this.updateUser(response.data);
                    return response.data;
                }
            } catch (error) {
                console.error("无法加载用户资料:", error);
                // 如果是401未授权错误，可能是token过期
                if (error.response && error.response.status === 401) {
                    // 可以在这里处理token刷新逻辑，或者直接登出
                    await this.logout();
                }
                throw error;
            }
        },

        // 登录操作
        async login(credentials) {
            try {
                const response = await authApiService.login(credentials);
                // 结构响应数据
                const { access_token, refresh_token, message, user: userInfoFromServer } = response.data;

                this.accessToken = access_token;
                this.refreshToken = refresh_token;
                // 后端登录成功可能返回部分用户信息，或者前端使用登录时的用户名...
                this.user = userInfoFromServer || { username: credentials.username };

                // 进行持久化存储
                localStorage.setItem('access_token', access_token);
                localStorage.setItem('refresh_token', refresh_token);
                localStorage.setItem('user', JSON.stringify(this.user));

                // 更新axios实例的默认头部
                apiClient.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

                // 返回成功消息给组件
                return message || "登录成功";

            } catch (error) {
                // 登录失败时，确保清理可能部分设置的状态
                this.clearAuthData();
                // 抛出错误信息给组件
                throw error.response?.data || error;
            }
        },

        // 注册操作
        async register(userData) {
            try {
                const response = await authApiService.register(userData)
                return response.data.message || "注册成功";
            } catch (error) {
                throw error.response?.data || error;
            }
        },

        // 登出操作 (参数 callApiBackend 用于控制是否调用后端登出API)
        async logout(callApiBackend = true) {
            if (callApiBackend && this.accessToken) {
                try {
                    await authApiService.logout(); // 调用后端吧token加入黑名单
                } catch (error) {
                    // 即便后端登出失败（例如网络问题或Token已过期），前端也必须完成登出流程
                    console.warn('后台服务出错', error.response?.data || error.message);
                }
            }
            // 清理认证相关的状态和localStorage
            this.clearAuthData();
            // 登出后通常导航到登录页
            router.push({ name: 'Login' });
        }
    }
})
```

**Token知识点：Pinia Store与认证状态**

  * **State持久化**：通过在`state`函数中从`localStorage`读取初始值，并在`actions`（如`login`, `logout`, `setNewAccessToken`）中同步更新`localStorage`和state，实现了认证状态的持久化。
  * **Getters的便利性**：`isAuthenticated` getter提供了一个响应式的、集中的方式来检查用户是否登录。
  * **Actions的职责**：
      * 封装了与认证相关的异步操作（调用`authApiService`）。
      * 统一处理认证成功或失败后的状态更新和`localStorage`操作。
      * 管理`apiClient`的默认请求头，确保Token被正确发送。
      * `tryAutoLogin` action对于单页应用(SPA)在加载时恢复用户会话至关重要。

##### 8.5.4 在 `main.js` 中调用 `tryAutoLogin`

为了在应用启动时尝试恢复登录状态，我们需要在 `main.js` 中，Pinia实例创建并被应用使用后，调用 `authStore` 的 `tryAutoLogin` action。

```javascript
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
```

##### 8.5.5 更新Vue组件以使用 `authStore`

现在，各个Vue组件将通过 `authStore` 来管理认证逻辑和状态，而不是直接操作 `localStorage` 或依赖自定义事件。

1.  **`frontend/src/views/LoginView.vue`**

    ```vue
    <script setup>
    import { ref } from 'vue';
    import { useRouter } from 'vue-router';
    import { ElNotification } from 'element-plus';
    
    import { useAuthStore } from '../stores/authStore'; // 1.引入Pinia状态管理
    
    const form = ref({ username: '', password: '' });
    const authStore = useAuthStore(); // 2. 获取store实例
    const router = useRouter();
        
    // 处理登录的方法
    const handleLogin = async () => {
        try { 
            // 3.调用store的login action
            const successMessageText = await authStore.login(form.value);
            ElNotification({
                title: '登录成功',
                message: successMessageText,
                type: 'success',
            })
            router.push('/profile');
        } catch (error) {
            ElNotification({
                title: '登录失败',
                message: error.message,
                type: 'error',
            })
        }
    }
    </script>
    ```

2.  **`frontend/src/views/RegisterView.vue`**

    ```vue
    <script setup>
    import { ref } from 'vue';
    import { useRouter } from 'vue-router';
    import { ElNotification } from 'element-plus';
    import { useAuthStore } from '@/stores/authStore';

    
    const authStore = useAuthStore();
    
    const form = ref({ username: '', password: '' });
    
    const router = useRouter();
    const handleRegister = async () => {
    try {
            const successMessageText = await authStore.register(form.value);
            ElNotification({
                title: '注册成功',
            message: successMessageText,
                type: 'success',
            })
            router.push('/login');
    } catch (error) {
            ElNotification({
                title: '注册失败',
                message: error.message,
                type: 'error',
            })
        }
    }
    
    </script>
    ```
    
3.  **`frontend/src/views/ProfileView.vue`**

    ```vue
    <script setup>
    import { ref, onMounted, computed } from 'vue';
    import { useAuthStore } from '@/stores/authStore';
    
    const authStore = useAuthStore();
    
    const user = computed(() => authStore.currentUser);
    const token = computed(() => authStore.getAccessToken);
    
    const files = ref([]);
    const loadingProfile = ref(false);
    
    // 使用Picsum API获取随机图片
    const getRandomImage = () => {
        const randomId = Math.floor(Math.random() * 1000) + 100;
        return `https://picsum.photos/512/512?random=${randomId}`;
    };
    
    
    // 初始化文件数据
    const initializeFiles = () => {
        const fileCount = Math.floor(Math.random() * 30) + 3;
        const tempFiles = [];
        
        for (let i = 0; i < fileCount; i++) {
            tempFiles.push({
                title: `图片 ${i+1}`,
                source: getRandomImage(),
                size: `${Math.floor(Math.random() * 900) + 100} KB`
            });
        }
        
        files.value = tempFiles;
    };
    
    onMounted(async () => {
        if (authStore.isAuthenticated) {
            try {
                loadingProfile.value = true;
                // 确保在组件挂载后初始化文件
                initializeFiles();
            } catch (error) {
                console.error('加载图片数据失败:', error);
            } finally {
                loadingProfile.value = false;
            }
        }
    });
    
    const handleLogout = async () => {
        await authStore.logout();
    };
    </script>
    ```



#### 8.6 后端实现：受保护API与Token验证 (Flask)

现在前端已经准备好发送带有Token的请求了，我们需要在后端创建一个受保护的API端点，并确保它能正确验证Token。

##### 8.6.1 `/api/me` 端点 (获取当前用户信息)

我们在 `backend/app.py` 中创建或确认此端点。这个端点将用于获取当前登录用户的信息，因此必须受到Token的保护。

```python
@app.route("/api/me", methods=["GET"])
@jwt_required()
def get_my_profile_api() -> tuple[jsonify, int]:
    # --- Token知识点：服务器端Token验证流程 ---
    # 当一个请求到达被`@jwt_required()`装饰的端点时，Flask-JWT-Extended会自动执行以下操作：
    # 1. 提取Token: 从预设的位置查找Token。默认情况下，它会查找HTTP请求的`Authorization`头部，
    # 并期望Token的格式为 `Bearer <JWT_STRING>`。Token的查找位置可以通过配置`JWT_TOKEN_LOCATION`来修改。
    # 2. 验证Token类型: 确保这是一个"access"类型的Token（因为`@jwt_required()`默认需要Access Token，
    #    而`@jwt_required(refresh=True)`则需要Refresh Token）
    # 3. 验证签名 (Signature): 使用在Flask应用配置中设置的`JWT_SECRET_KEY`和JWT头部声明的算法(alg)，
    #    来验证Token的签名部分。如果签名无效（说明Token可能被篡改或密钥不匹配），请求将被拒绝。
    # 4. 验证标准声明 (Standard Claims):
    #    - `exp` (Expiration Time): 检查Token是否已过期。如果过期，请求将被拒绝。
    #    - `nbf` (Not Before): 如果存在此声明，检查Token是否已到达其生效时间。
    #    - `iat` (Issued At): 记录Token的签发时间。
    #    - `jti` (JWT ID): 每个Token的唯一标识符，主要用于Token吊销（黑名单机制）。
    # 5. 黑名单检查 (Blocklist Check): 如果应用配置中启用了`JWT_BLACKLIST_ENABLED = True`，
    #    并且定义了`@jwt.token_in_blocklist_loader`回调函数，那么`Flask-JWT-Extended`会调用这个回调，
    #    传入Token的`jti`，以检查该Token是否已被吊销。如果回调返回`True`，请求将被拒绝。
    #
    # 如果上述任何一步验证失败，`Flask-JWT-Extended`会自动返回一个相应的HTTP错误响应，
    # 通常是 `401 Unauthorized` (例如Token缺失、过期、被吊销) 或 `422 Unprocessable Entity` (例如Token格式错误、签名无效)。
    # 开发者可以通过 `@jwt.expired_token_loader`, `@jwt.invalid_token_loader` 等回调来定制这些错误响应的格式。
    # 如果所有验证都通过，则请求被允许进入被装饰的路由函数。

    # 获取通过Token传递的identity (即登录时create_access_token的identity参数)
    current_user_identity: str = get_jwt_identity()

    # (可选) 获取Token 中的所有声明，包括自定义声明
    jwt_claims: dict = get_jwt()

    # 从内存存储中获取用户信息(实际上这里要查询数据库，等待我们学习到数据库章...)
    user_data_from_store = users_in_memory_store.get(current_user_identity)

    # 为了安全，不要直接返回存储中的哈希密码
    # 此处可以构建一个包含安全信息的用户对象返回给前端
    user_profile_data = {
        "username":current_user_identity,
        "login_time": jwt_claims.get("iat"),
        "expiration_time": jwt_claims.get("exp"),
        "token_type": jwt_claims.get("type")
    }

    return jsonify(user_profile_data), 200


```

**后端代码要点**：

  * `@jwt_required()`: 核心装饰器，用于保护此API端点。
  * `get_jwt_identity()`: 用于从有效的Token中提取用户身份。
  * `get_jwt()`: 用于获取Token的完整Payload，包含所有标准声明和自定义声明。
  * 我们从内存存储`users_in_memory_store`中查找用户信息（模拟数据库查询），并返回一个安全的、不含敏感信息的用户资料对象。

#### 8.7 前端访问受保护API并展示用户信息 (Vue.js)

现在后端有了受保护的`/api/me`接口，前端的`ProfileView.vue`可以尝试调用它来获取并展示用户信息。

##### 8.7.1 确认 `authService.js` 中有 `getProfile` 方法

此方法已在 `8.2.3` 节中定义：

```javascript
// 获取用户资料 (受保护的接口)
getProfile() {
    return apiClient.get('/me');
},
```

##### 8.7.2 在 `ProfileView.vue` 中调用并处理用户信息

我们需要修改 `ProfileView.vue` 的 `<script setup>` 部分，以在组件挂载后（如果用户已认证）调用 `authStore` 中获取用户资料的action（例如，我们之前定义的 `WorkspaceAndSetUser` action，它内部会调用 `authService.getProfile`）。

```vue
<template>
  <div class="p-8">
    <h1 class="text-3xl font-bold text-gray-700 mb-6">用户中心</h1>
    
    <div v-if="loadingProfile" class="text-center py-10">
      <span class="loading loading-lg loading-spinner text-primary"></span>
      <p class="mt-2 text-gray-500">正在加载用户数据...</p>
    </div>

    <div v-else-if="userProfile" class="p-6 bg-white rounded-lg shadow-md">
      <h2 class="text-2xl font-semibold text-gray-800">欢迎, {{ userProfile.username }}!</h2>
      <p class="text-gray-600 mt-2">这是从受保护的后端API获取到的信息。</p>
      
      <p class="text-gray-600 mt-1"><span class="font-medium">Token签发时间:</span> {{ formatTimestamp(userProfile.login_time) || 'N/A' }}</p>
      <p class="text-gray-600 mt-1"><span class="font-medium">Token过期时间:</span> {{ formatTimestamp(userProfile.expiration_time) || 'N/A' }}</p>
      <p class="text-gray-600 mt-1"><span class="font-medium">Token类型:</span> {{ userProfile.token_type || 'N/A' }}</p>
      
      <button @click="performUserLogout" class="btn btn-outline btn-error btn-sm mt-6">
        安全登出
      </button>
    </div>

    <div v-else class="p-6 bg-yellow-50 border-l-4 border-yellow-400 text-yellow-700">
      <p>无法加载用户资料。您可能需要 <router-link :to="{name: 'Login'}" class="link link-primary">登录</router-link>。</p>
    </div>

    <div class="mt-10" v-if="isAuthenticated && files.length">
      <h2 class="text-xl font-semibold mb-4 text-gray-700">我的文件 (示例)</h2>
      <div class="waterfall-wrapper">
        <div v-for="(file, index) in files" :key="index" class="waterfall-item group">
          <div class="overflow-hidden rounded-lg bg-gray-200 aspect-w-1 aspect-h-1">
            <img :src="file.source" :alt="file.title" class="w-full h-full object-cover object-center group-hover:opacity-75"/>
          </div>
          <p class="mt-2 block text-sm font-medium text-gray-900 truncate">{{ file.title }}</p>
          <p class="block text-sm font-medium text-gray-500">{{ file.size }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from '@/stores/authStore';
import { ElMessage } from 'element-plus';

const authStore = useAuthStore();


// 从Pinia store获取响应式的用户数据和认证状态
const userProfile = computed(() => authStore.currentUser); 
const isAuthenticated = computed(() => authStore.isAuthenticated);

const loadingProfile = ref(false);
const files = ref([]); // 文件数据，保持您的瀑布流示例


// 格式化时间戳的辅助函数
const formatTimestamp = (timestamp) => {
  if (!timestamp) return null;
  return new Date(timestamp * 1000).toLocaleString(); // JWT时间戳是秒，Date需要毫秒
};

onMounted(async () => {
  if (isAuthenticated.value) { // 仅当Pinia store认为已认证时才尝试获取
    loadingProfile.value = true;
    try {
      // 调用Pinia store的action来获取并设置用户信息
      // 这个action内部会调用authService.getProfile()
      await authStore.fetchAndSetUser(); 
      // 只有在成功获取用户资料后才加载文件示例
      if(userProfile.value) initializeFiles(); 
    } catch (error) {
      // 错误通常已在authStore的action或apiClient的响应拦截器中处理
      // (例如，Token无效导致401，拦截器会尝试刷新或登出)
      ElMessage.error(`加载用户资料失败，${error.message}`);
    } finally {
      loadingProfile.value = false;
    }
  } else {
    // 如果store认为未认证，导航守卫通常会重定向到登录页
    // 但如果用户直接访问此页面且未登录，这里可以再做一次判断
    console.log("用户中心: 在挂载时未认证 (通过Pinia store检查)。");
    router.push({ name: 'Login' }); // 可选：强制导航
  }
});


const performUserLogout = async () => {
  await authStore.logout();
  ElMessage.success('您已成功登出。');
};


// --- 瀑布流示例数据生成逻辑 ---
const getRandomImage = () => `https://picsum.photos/500/500?random=${Math.random()}`;
const initializeFiles = () => {
  const fileCount = Math.floor(Math.random() * 30);
  const tempFiles = [];
  for (let i = 0; i < fileCount; i++) {
    tempFiles.push({
      title: `图片 ${i+1}`,
      source: getRandomImage(),
    });
  }
  files.value = tempFiles;
};
// --- 结束瀑布流示例数据 ---
</script>

<style scoped>
/* 瀑布流布局样式 */
.waterfall-wrapper {
    column-count: 4; /* 默认4列 */
    column-gap: 16px;
}
.waterfall-item {
    break-inside: avoid; /* 防止内容被折断 */
    margin-bottom: 16px;
    position: relative;
}
</style>
```

1.  **认证状态驱动**：`ProfileView.vue` 现在依赖 `authStore.isAuthenticated` 和 `authStore.currentUser` 来决定显示内容和行为。
2.  **API调用**：在 `onMounted`钩子中，如果用户已认证（根据Pinia store的状态），则调用`authStore.fetchAndSetUser()`。这个action会进一步调用`authService.getProfile()`，最终向后端的`/api/me`发送请求。
3.  **自动携带Token**：由于`apiClient.js`中配置了请求拦截器，它会自动从`authStore`读取`accessToken`并添加到`Authorization`头部。
4.  **后端验证**：Flask后端的`/api/me`端点会使用`@jwt_required()`来验证这个Token。
5.  **数据显示**：如果Token有效且后端成功返回数据，`authStore`会更新`currentUser`状态，`ProfileView.vue`的计算属性`userProfile`随之更新，从而在界面上显示用户信息。



#### 8.8 Token 刷新流程 (全栈)

Access Token 通常具有较短的生命周期以提高安全性。当它过期时，用户不应该被立即强制登出并重新输入凭证，而是应该通过一个长效的 Refresh Token 来“静默地”获取新的 Access Token，从而提供无缝的用户体验。

##### 8.8.1 后端 `/api/auth/refresh` API (Flask)

首先，确保 Flask 后端 (`backend/app.py`) 有一个用于刷新 Access Token 的端点。此端点需要有效的 Refresh Token 才能访问。

```python
@app.route("/api/auth/refresh", methods=["POST"])
@jwt_required(refresh=True)  # 关键：表明此断点需要的是Refresh Token
def refresh_access_token_api() -> tuple[jsonify, int]:
    """
        使用有效的 Refresh Token 获取一个新的 Access Token。
    """
    # --- Token 知识点：Refresh Token 的验证与使用 ---
    # 1. 客户端在请求头 `Authorization: Bearer <refresh_token>` 中发送 Refresh Token。
    # 2. `@jwt_required(refresh=True)` 装饰器会专门验证传入的是否为 Refresh Token，
    #    并检查其签名、有效期等。
    # 3. 如果 Refresh Token 有效，`get_jwt_identity()` 仍然可以提取出用户的身份信息。
    # 4. 服务器基于此身份信息签发一个新的 Access Token。
    #    通常，通过刷新获得的 Access Token 不再标记为 "fresh" (`fresh=False`)。
    # 5. 一般情况下，刷新操作不会同时签发新的 Refresh Token (除非实现了 Refresh Token 轮换策略)。
    current_user_identity: str = get_jwt_identity()

    # 创建新的 Access Token
    new_access_token: str = create_access_token(identity=current_user_identity, fresh=False)
    
    logger.info(f"用户 '{current_user_identity}' 刷新了 Access Token。")
    return jsonify({
        "messages": f"新的 Access Token 已生成",
        "status": 200,
        "access_token": new_access_token
    }), 200
    
```

**后端代码要点：**

  * `@jwt_required(refresh=True)`: 强制此端点只能用 Refresh Token 访问。
  * `create_access_token(identity=..., fresh=False)`: 生成新的 Access Token，明确其非“新鲜”。

##### 8.8.2 前端 `authService.js` 中修改/添加 `refreshToken` 方法

确保 `frontend/src/apis/authService.js` 文件中有调用后端刷新接口的方法。

```javascript
    // 刷新 Token (将在 8.8 节实现)
    refreshToken() {
        const currentRefreshToken = localStorage.getItem('refresh_token');
        if (!currentRefreshToken) {
            return Promise.reject(new Error("没有可用的刷新令牌"));
        }

        // 创建一个新的axios实例，避免使用apiClient导致的循环引用，这一步很重要
        return axios({
            method: 'post',
            url: 'http://127.0.0.1:5000/api/auth/refresh',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentRefreshToken}`
            },
            data: {}
        });
    }
```

##### 8.8.3 Token 知识点：完善 `apiClient.js` 的响应拦截器以实现自动刷新

现在，我们将升级 `frontend/src/utils/http.js` (即`apiClient.js`) 中的响应拦截器，使其在捕获到 `401 Unauthorized` 错误（通常意味着 Access Token 过期）时，自动尝试使用 Refresh Token 获取新的 Access Token，并用新 Token 重试原始失败的请求。

```javascript
// frontend/src/utils/http.js
import axios from 'axios';
import authApiService from '../apis/authService';
// 导入提示框
import { ElMessage } from 'element-plus';
import router from '../router';
const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Token 知识点: Axios 请求拦截器 - 自动添加 Authorization 头部
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// 标记是否正在刷新Token
let isRefreshing = false;
// 存储等待刷新Token的请求队列
let failedQueue = [];

// 执行队列中的请求
const processQueue = (error, token = null) => {
    failedQueue.forEach(prom => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token);
        }
    });
    
    failedQueue = [];
};

// Token 知识点: Axios 响应拦截器 - 处理 Token 过期和刷新
apiClient.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error) => {
        const originalRequest = error.config;
        
        // 检查是否为401错误且不是刷新Token的请求
        if (error.response && error.response.status === 401 && 
            !originalRequest._retry && 
            !originalRequest.url.includes('/auth/refresh')) {
            
            // 如果已经在刷新Token，则将请求加入队列
            if (isRefreshing) {
                return new Promise((resolve, reject) => {
                    failedQueue.push({resolve, reject});
                }).then(token => {
                    originalRequest.headers['Authorization'] = `Bearer ${token}`;
                    return apiClient(originalRequest);
                }).catch(err => {
                    return Promise.reject(err);
                });
            }
            
            originalRequest._retry = true;
            isRefreshing = true;
            console.log('Token 过期或无效，尝试刷新...');
            
            try {
                // 尝试使用refreshToken获取新的accessToken
                const response = await authApiService.refreshToken();
                const { access_token } = response.data;
                
                // 更新localStorage和axios默认头部
                localStorage.setItem('access_token', access_token);
                apiClient.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
                
                // 使用新token更新原始请求的Authorization头部
                originalRequest.headers['Authorization'] = `Bearer ${access_token}`;
                
                // 处理队列中的请求
                processQueue(null, access_token);
                isRefreshing = false;
                
                // 重试原始请求
                return apiClient(originalRequest);
            } catch (refreshError) {
                console.error('刷新Token失败:', refreshError);
                // 刷新失败，清除token并重定向到登录页
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                
                // 处理队列中的请求
                processQueue(refreshError, null);
                isRefreshing = false;
                ElMessage.error('登录已过期，请重新登录');
                
                router.push('/login');

                return Promise.reject(refreshError);
            }
        }
        return Promise.reject(error);
    }
);

export default apiClient;
```

**测试Token刷新**：

  * 在Flask后端的 `app.config["JWT_ACCESS_TOKEN_EXPIRES"]` 设置一个很短的时间（例如 `timedelta(seconds=10)`）进行测试。
  * 登录前端应用。
  * 等待超过10秒。
  * 尝试访问受保护的路由（如`/profile`）或执行需要认证的操作。
  * 观察浏览器开发者工具的网络(Network)标签页：
      * 应该能看到原始请求返回401。
      * 紧接着应该有一个对 `/api/auth/refresh` 的POST请求。
      * 如果刷新成功，会看到原始请求被使用新的Access Token自动重试并成功。
      * 用户应该无感知地继续操作。

#### 8.9 用户登出 (全栈实现Token吊销)

实现用户登出功能时，仅仅在客户端删除Token是不够的，因为该Token在有效期内仍然可以被截获并使用。一个更安全的做法是实现服务器端的Token吊销机制，通常采用黑名单(Blocklist)策略。

##### 8.9.1 Token知识点：JWT的“登出”与服务器端吊销

  * **JWT的无状态性**：JWT的核心优势之一是无状态，服务器不需要存储已签发的Token。Token本身包含所有验证所需信息（通过签名保证完整性，通过声明如`exp`保证时效性）。
  * **“登出”的挑战**：由于无状态，服务器无法知道某个特定的Token是否“应该”被登出。只要Token签名有效且未过期，它就是合法的。
  * **解决方案：Token黑名单 (Blocklist)**
      * 当用户登出或需要使某个Token失效时，将其一个唯一标识符（通常是JWT的`jti`声明，即JWT ID）添加到一个服务器端的黑名单中。
      * `Flask-JWT-Extended`在每次验证Token时，除了检查签名和有效期外，还会调用一个开发者提供的回调函数（`@jwt.token_in_blocklist_loader`），查询此`jti`是否存在于黑名单中。如果存在，则该Token被视为已吊销，即使它在其他方面都有效。
      * 黑名单需要持久化存储（如Redis、数据库），因为内存中的黑名单在服务器重启后会丢失。在本章的无数据库示例中，我们仍将使用内存中的`set`作为黑名单。

##### 8.9.2 后端实现Token Blocklisting API (Flask)

我们在 `backend/app.py` 中确保以下配置和API端点已实现：

1.  **Flask应用配置 (确认)**:

    ```python
    # backend/app.py
    # ...
    app.config["JWT_BLACKLIST_ENABLED"] = True
    app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access", "refresh"] # 登出时同时检查access和refresh token
    # ...
    TOKEN_BLOCKLIST: set[str] = set() # 内存黑名单
    ```

2.  **`@jwt.token_in_blocklist_loader` 回调 (确认)**:

    ```python
    # backend/app.py
    # ... (jwt = JWTManager(app) 之后)
    # 这个回调函数用于检查JWT令牌是否在黑名单中
    # 当用户登出或管理员吊销令牌时，我们会将令牌的唯一标识符(jti)添加到黑名单中
    # Flask-JWT-Extended会在每次请求时调用此回调，检查令牌是否被吊销
    # 如果返回True，表示令牌在黑名单中，请求将被拒绝并返回401错误
    # 这是实现安全登出和令牌吊销功能的关键机制
    @jwt.token_in_blocklist_loader
    def check_if_jti_in_blocklist(jwt_header: dict, jwt_payload: dict) -> bool:
        """
        回调函数，检查给定的JWT的jti是否已被加入黑名单。
        Flask-JWT-Extended会在验证每个受保护请求的Token时调用此函数。
        """
        jti = jwt_payload["jti"] # 'jti'是JWT的唯一标识符声明
        is_revoked = jti in TOKEN_BLOCKLIST
        if is_revoked:
            logger.info(f"Token JTI '{jti}' 在黑名单中。")
        return is_revoked
    
    ```

3.  **登出API端点 (`/api/auth/logout` 和 `/api/auth/logout_refresh`)**:
    这些端点接收有效的Token，提取其`jti`，并将`jti`添加到`TOKEN_BLOCKLIST`中。

    ```python
    # backend/app.py
    # ... (确保导入了 get_jwt)
    from flask_jwt_extended import get_jwt
    # ...

    @app.route('/api/auth/logout', methods=['DELETE']) # 使用DELETE语义表示资源状态改变
    @jwt_required() # 需要有效的Access Token来将其jti加入黑名单
    def logout_access_api() -> tuple[jsonify, int]:
        """
        吊销当前传入的Access Token。
        """
        jti = get_jwt()["jti"] # 获取当前Access Token的JWT ID
        TOKEN_BLOCKLIST.add(jti)
        logger.info(f"Access Token JTI '{jti}' added to blocklist. User logged out.")
        return jsonify(message="Access Token已成功吊销，用户已登出。"), 200

    ```

##### 8.9.3 前端实现登出逻辑 (调用后端API并清理状态)

前端的登出逻辑现在需要调用后端的登出API，并在Pinia store (`authStore.js`) 的 `logout` action 中实现。

1.  **`frontend/src/apis/authService.js` 中确认 `logout` 方法**

```js
    // 登出接口 (如果后端实现了 Token 吊销)
    logout() {
        // 假设后端有一个 /auth/logout 接口来吊销 Token
        // 注意: 即使调用失败，前端也应该清理本地 Token
        return apiClient.delete('/auth/logout');
    },
```



1.  **更新 `frontend/src/stores/authStore.js` 中的 `logout` action**
    确保它调用 `authApiService.logout()`。

    ```javascript
            // 登出操作 (参数 callApiBackend 用于控制是否调用后端登出API)
            async logout(callApiBackend = true) {
                if (callApiBackend && this.accessToken) {
                    try {
                        await authApiService.logout(); // 调用后端吧token加入黑名单
    
                    } catch (error) {
                        // 即便后端登出失败（例如网络问题或Token已过期），前端也必须完成登出流程
                        console.log('后台服务出错', error.response?.data || error.message);
                    }
                }
                // 清理认证相关的状态和localStorage
                this.clearAuthData();
                // 登出后通常导航到登录页
                router.push({ name: 'Login' });
            }
    ```

    

**测试登出与Token吊销**：

1.  登录应用。
2.  复制当前的Access Token。
3.  点击登出按钮。
4.  尝试使用之前复制的Access Token访问受保护的API（如`/api/me`，可以使用Postman或curl）。
5.  如果黑名单机制工作正常，后端应该返回401或422错误（具体取决于`Flask-JWT-Extended`的错误处理，因为Token的`jti`在黑名单中）。`@jwt.revoked_token_loader` 可以用来定制这个响应。

附上项目完整代码仓库：



-----