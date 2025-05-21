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
                        <input type="password" id="password" placeholder="请输入密码" minlength="6" maxlength="12" v-model="form.password"
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