<template>
  <el-container class="pet-layout">
    <!-- ================= 顶部栏 ================= -->
    <el-header class="layout-header" height="64px">
      <!-- 左：Logo -->
      <div class="header-left">
        <el-button
          class="mobile-menu-btn"
          text
          :icon="MenuIcon"
          aria-label="打开导航菜单"
        />
        <router-link to="/manager/home" class="brand" aria-label="暖爪首页">
          <div class="brand-logo" aria-hidden="true">🐾</div>
          <div class="brand-text">
            <strong>暖爪</strong>
            <small>智能宠物领养平台</small>
          </div>
        </router-link>
      </div>

      <!-- 中：搜索框 -->
      <div class="header-search" role="search">
        <el-input
          placeholder="搜索品种、城市或关键词…"
          clearable
          aria-label="搜索宠物"
          class="custom-search-input"
        >
          <template #prefix>
            <el-icon class="search-icon">
              <Search />
            </el-icon>
          </template>
        </el-input>
      </div>

      <!-- 右：操作区 -->
      <div class="header-actions">
        <el-badge :is-dot="true" class="msg-badge">
          <el-button
            circle
            text
            :icon="Bell"
            size="large"
            aria-label="消息通知"
          />
        </el-badge>

        <el-dropdown trigger="click">
          <el-avatar
            :size="38"
            src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"
            class="user-avatar"
            aria-label="当前用户：小暖"
          >
            小
          </el-avatar>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item>个人资料</el-dropdown-item>
              <el-dropdown-item>我的申请</el-dropdown-item>
              <el-dropdown-item divided @click="outLogin">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <!-- ================= 主体 ================= -->
    <el-container class="layout-body">
      <!-- 移动端遮罩 (默认隐藏) -->
      <div class="aside-mask" aria-hidden="true" style="display: none;" />

      <!-- 侧边栏：动态绑定宽度 -->
      <el-aside class="layout-aside" :width="isCollapse ? '64px' : '236px'">
        <!-- 绑定 :collapse="isCollapse" -->
        <el-menu
          router
          default-active="/home"
          :collapse="isCollapse"
          :collapse-transition="false"
          class="el-menu-vertical"
        >
          <!-- 领养中心分组 -->
          <!-- 折叠时隐藏文字标题 -->
          <div class="menu-title" v-show="!isCollapse">领养中心</div>

          <el-menu-item index="/manager/home">
            <el-icon><HomeFilled /></el-icon>
            <template #title><span class="menu-label">首页</span></template>
          </el-menu-item>

          <el-menu-item index="/manager/pets">
            <el-icon><List /></el-icon>
            <template #title>
              <span class="menu-item-inner">
                <span class="menu-label">宠物列表</span>
<!--                <el-badge :value="128" type="danger" class="menu-badge" />-->
              </span>
            </template>
          </el-menu-item>

          <el-menu-item index="/manager/match">
            <el-icon><Star /></el-icon>
            <template #title><span class="menu-label">智能匹配</span></template>
          </el-menu-item>

          <el-menu-item index="/manager/guide">
            <el-icon><Document /></el-icon>
            <template #title><span class="menu-label">领养指南</span></template>
          </el-menu-item>

          <!-- 个人中心分组 -->
          <div class="menu-title" v-show="!isCollapse">个人中心</div>

          <el-menu-item index="/manager/apply">
            <el-icon><Tickets /></el-icon>
            <template #title><span class="menu-label">我的申请</span></template>
          </el-menu-item>

          <el-menu-item index="/manager/favorite">
            <el-icon><StarFilled /></el-icon>
            <template #title><span class="menu-label">我的收藏</span></template>
          </el-menu-item>

          <el-menu-item index="/manager/user">
            <el-icon><Setting /></el-icon>
            <template #title><span class="menu-label">账号设置</span></template>
          </el-menu-item>
        </el-menu>

        <!-- 底部折叠按钮 -->
        <div class="sidebar-footer">
          <el-button text class="collapse-btn" aria-label="切换菜单状态" @click="toggleCollapse">
            <!-- 根据状态切换图标 -->
            <el-icon>
              <Expand v-if="isCollapse" />
              <Fold v-else />
            </el-icon>
            <!-- 折叠时隐藏文字 -->
            <span class="collapse-text" v-show="!isCollapse">收起菜单</span>
          </el-button>
        </div>
      </el-aside>

      <!-- 主内容区：子路由渲染入口 -->
      <el-main>
          <router-view />
      </el-main>

    </el-container>

    <!-- ================= 页脚 ================= -->
    <el-footer height="44px" class="layout-footer">
      <span>© 2025 暖爪 · 智能宠物领养平台</span>
      <el-divider direction="vertical" />
      <router-link class="footer-link" to="/manager/guide">领养指南</router-link>
    </el-footer>
  </el-container>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ref } from 'vue'
import {
  Bell,
  Document,
  Expand,
  Fold,
  HomeFilled,
  List,
  Menu as MenuIcon,
  Search,
  Setting,
  Star,
  StarFilled,
  Tickets,
} from '@element-plus/icons-vue'
import {logout} from "@/utils/auth.js";

const router = useRouter()
// 1. 从本地存储读取初始状态（如果有的话）
const cachedState = localStorage.getItem('menu-collapsed')
const isCollapse = ref(cachedState === 'true')

// 2. 切换折叠状态的方法
const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
  // 保存到本地存储
  localStorage.setItem('menu-collapsed', isCollapse.value)
}

const outLogin = () => {
  router.push('/login')
  logout()
}
</script>

<style scoped>
/* =========================================================
 * 设计令牌
 * =======================================================*/
.pet-layout {
  --brand: #ff7a59;
  --brand-light: #ff9a6c;
  --brand-dark: #ef5b3a;
  --brand-weak: #fff1ec;
  --bg-page: #f6f7fb;
  --bg-card: #ffffff;
  --bg-muted: #f4f6fa;
  --border: #eaedf3;
  --text-main: #1f2937;
  --text-body: #4b5563;
  --text-sub: #8892a0;
  --text-muted: #b3bbc8;

  --radius-sm: 8px;
  --radius-md: 10px;
  --radius-lg: 12px;
  --radius-pill: 999px;

  --header-h: 64px;
  --footer-h: 44px;
  --aside-w: 236px;
  --aside-w-collapsed: 64px;

  --shadow-brand: 0 6px 14px rgba(255, 107, 74, 0.35);

  --el-color-primary: var(--brand);
  --el-color-primary-light-3: var(--brand-light);
  --el-color-primary-light-5: #ffbba3;
  --el-color-primary-light-7: #ffd8cc;
  --el-color-primary-light-9: var(--brand-weak);

  height: 100vh;
  height: 100dvh;
  background-color: var(--bg-page);
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC',
    'Microsoft YaHei', sans-serif;
}

.pet-layout,
.pet-layout * {
  box-sizing: border-box;
}

/* =========================================================
 * 顶部栏
 * =======================================================*/
.layout-header {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
  align-items: center;
  gap: 16px;
  padding: 0 20px;
  background-color: var(--bg-card);
  border-bottom: 1px solid var(--border);
  position: relative;
  z-index: 20;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 4px;
  min-width: 0;
}

.mobile-menu-btn {
  display: none;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
  text-decoration: none;
  color: inherit;
}

.brand-logo {
  flex: none;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-lg);
  display: grid;
  place-items: center;
  font-size: 20px;
  color: #fff;
  background: linear-gradient(135deg, #ff9a6c, #ff6b4a);
  box-shadow: var(--shadow-brand);
}

.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.25;
  min-width: 0;
}

.brand-text strong {
  font-size: 16px;
  letter-spacing: 0.5px;
  color: var(--text-main);
  white-space: nowrap;
}

.brand-text small {
  font-size: 11px;
  color: var(--text-sub);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.header-search {
  width: min(420px, 42vw);
  justify-self: center;
}

.search-icon {
  cursor: pointer;
  transition: color 0.2s;
}

.search-icon:hover {
  color: var(--brand);
}

:deep(.custom-search-input .el-input__wrapper) {
  border-radius: var(--radius-pill);
  background-color: var(--bg-muted);
  box-shadow: none;
  border: 1px solid transparent;
  transition: background-color 0.2s, border-color 0.2s, box-shadow 0.2s;
}

:deep(.custom-search-input .el-input__wrapper:hover) {
  background-color: #eef1f7;
}

:deep(.custom-search-input .el-input__wrapper.is-focus) {
  background-color: var(--bg-card);
  border-color: var(--brand);
  box-shadow: 0 0 0 3px rgba(255, 122, 89, 0.12);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  justify-self: end;
}

.msg-badge {
  display: flex;
  align-items: center;
}

.user-avatar {
  cursor: pointer;
  outline: none;
  flex: none;
  font-weight: 600;
}

.user-avatar:focus-visible {
  box-shadow: 0 0 0 3px rgba(255, 122, 89, 0.25);
}

/* =========================================================
 * 主体
 * =======================================================*/
.layout-body {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.layout-aside {
  flex: none;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-card);
  border-right: 1px solid var(--border);
  overflow: hidden;
  transition: width 0.25s ease, transform 0.25s ease;
}

.el-menu-vertical {
  border-right: none;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 12px 8px;
}

/* 核心：收起时去除菜单内边距 */
.el-menu-vertical.el-menu--collapse {
  padding: 12px 0;
  width: 64px;
}

.el-menu-vertical::-webkit-scrollbar {
  width: 6px;
}

.el-menu-vertical::-webkit-scrollbar-thumb {
  background-color: #d8dee9;
  border-radius: var(--radius-pill);
}

.menu-title {
  padding: 12px 16px 8px;
  font-size: 11px;
  letter-spacing: 1px;
  color: var(--text-muted);
  user-select: none;
  white-space: nowrap;
}

:deep(.el-menu-item) {
  height: 42px;
  line-height: 42px;
  border-radius: var(--radius-md);
  margin-bottom: 4px;
  color: var(--text-body);
}

:deep(.el-menu-item:hover) {
  background-color: var(--bg-muted);
}

:deep(.el-menu-item.is-active) {
  background-color: var(--brand-weak);
  color: var(--brand-dark);
  font-weight: 600;
}

/* 核心：收起时菜单项内容居中 */
:deep(.el-menu--collapse .el-menu-item) {
  justify-content: center;
  padding: 0 !important;
}

.menu-item-inner {
  display: flex;
  align-items: center;
  width: 100%;
  min-width: 0;
}

.menu-label {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 修改点：修复 Badge 垂直对齐问题 */
.menu-badge {
  margin-left: auto;
  display: flex;
  align-items: center; /* 让徽标和文字中心对齐 */
  /* 去掉了原来的 transform: translateY(-2px); */
}

/* 让 Element Plus 默认的 sup 标签居中 */
:deep(.menu-badge .el-badge__content) {
  margin-top: 0;
}

:deep(.el-menu-item.is-active .menu-badge .el-badge__content) {
  background-color: var(--brand);
  border: none;
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid var(--border);
}

.collapse-btn {
  width: 100%;
  justify-content: center;
  color: var(--text-sub);
  border: 1px dashed var(--border);
  border-radius: var(--radius-md);
  background: #fafbfd;
}

.collapse-btn:hover {
  color: var(--brand);
  border-color: #ffcfc2;
  background: var(--brand-weak);
}

.collapse-text {
  margin-left: 8px;
}

.layout-main {
  padding: 24px;
  overflow-y: auto;
  scrollbar-gutter: stable;
  background-color: var(--bg-page);
}

/* =========================================================
 * 页脚
 * =======================================================*/
.layout-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: 12px;
  color: var(--text-sub);
  background-color: var(--bg-card);
  border-top: 1px solid var(--border);
}

.footer-link {
  color: var(--text-sub);
  text-decoration: none;
  transition: color 0.2s;
}

.footer-link:hover {
  color: var(--brand);
}

/* =========================================================
 * 过渡动画
 * =======================================================*/
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* =========================================================
 * 响应式
 * =======================================================*/
@media (max-width: 992px) {
  .header-search {
    display: none;
  }

  .brand-text small {
    display: none;
  }

  .layout-main {
    padding: 16px;
  }
}

@media (max-width: 768px) {
  .mobile-menu-btn {
    display: inline-flex;
  }

  /* 移动端侧边栏直接变成抽屉，不需要折叠，宽度固定 */
  .layout-aside {
    position: fixed;
    top: var(--header-h);
    bottom: 0;
    left: 0;
    z-index: 100;
    width: var(--aside-w) !important;
    transform: translateX(-100%);
    border-right: 1px solid var(--border);
    box-shadow: 4px 0 16px rgba(15, 23, 42, 0.08);
  }

  /* 移动端隐藏折叠按钮，因为不需要 */
  .sidebar-footer {
    display: none;
  }
}

@media (max-width: 560px) {
  .layout-header {
    padding: 0 12px;
    gap: 8px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .layout-aside,
  .fade-enter-active,
  .fade-leave-active,
  .footer-link {
    transition: none !important;
  }
}
</style>