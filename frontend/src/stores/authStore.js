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
                    console.log('后台服务出错', error.response?.data || error.message);
                }
            }
            // 清理认证相关的状态和localStorage
            this.clearAuthData();
            // 登出后通常导航到登录页
            router.push({ name: 'Login' });
        }

    }
})