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
