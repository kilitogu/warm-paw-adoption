import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '@/utils/auth'

export const constantRouters = [
    { path: '/login', component: () => import("@/views/Login.vue") },
    { path: '/register', component: () => import("@/views/Register.vue") },
    // 根路径直接重定向到首页
    { path: '/', redirect: '/manager/home' },
    {
      path: '/manager',
      name: 'Layout',
      component: () => import('@/views/layout/index.vue'),
      children: [
        {path: 'home', name: 'Home', component: () => import('@/views/Home.vue'), meta: { title: '首页' }},
        {path: 'pets', name: 'Pets', component: () => import('@/views/Pet.vue'), meta: { title: '宠物列表' }},
        {path: 'pet/detail/:id', name: 'PetDetail', component: () => import('@/views/PetDetail.vue'), meta: { title: '宠物详情' }},
        {path: 'apply', name: 'MyApplications', component: () => import('@/views/My.vue'), meta: { title: '我的申请', tab: 'apply' }},
        {path: 'favorite', name: 'MyFavorites', component: () => import('@/views/My.vue'), meta: { title: '我的收藏', tab: 'favorite' }},
        {path: 'user', name: 'User', component: () => import('@/views/User.vue'), meta: { title: '账号信息' }},
        {path: 'guide', name: 'Guide', component: () => import('@/views/Guide.vue'), meta: { title: '领养指南' }},
        {path: 'match', name: 'Match', component: () => import('@/views/Match.vue'), meta: { title: '智能匹配' }},
      ]
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes: constantRouters,
    scrollBehavior(to, from, savedPosition) {
        if (savedPosition) return savedPosition
        return { top: 0 }
    }
})

// 路由守卫：验证token
router.beforeEach((to, from) => {
  const token = getToken()

  if (to.path === '/login' || to.path === '/register') {
    return true
  } else {
    return token ? true : '/login'
  }
})

export default router