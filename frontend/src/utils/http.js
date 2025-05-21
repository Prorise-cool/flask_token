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
                console.log('刷新Token响应:', response);
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