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