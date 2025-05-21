// frontend/src/apis/authService.js
import apiClient from "../utils/http"
import axios from 'axios';

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
        return apiClient.get('/me');
    },

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
};