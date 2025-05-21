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
    { name: '测试', href: '/test', current: false },
]
</script>