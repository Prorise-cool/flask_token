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
import router from '@/router';

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

@media (max-width: 1200px) {
    .waterfall-wrapper {
        column-count: 3;
    }
}

@media (max-width: 768px) {
    .waterfall-wrapper {
        column-count: 2;
    }
}

@media (max-width: 480px) {
    .waterfall-wrapper {
        column-count: 1;
    }
}

.waterfall-item {
    break-inside: avoid; /* 防止内容被折断 */
    margin-bottom: 16px;
    position: relative;
}
</style>