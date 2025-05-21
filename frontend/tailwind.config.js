// tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('daisyui'), // 添加 DaisyUI 插件
  ],
  // (可选) DaisyUI 主题等配置
  daisyui: {
    themes: ["light", "dark", "cupcake"], // 启用的主题列表，可按需选择
    // styled: true,         // DaisyUI组件类是否默认应用 (默认为true)
    // base: true,           // 是否应用DaisyUI基础样式 (默认为true)
    // utils: true,          // 是否应用DaisyUI工具类 (默认为true)
    // logs: true,           // 是否在控制台显示DaisyUI日志 (默认为true)
  },
}