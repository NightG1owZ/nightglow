import { createRouter, createWebHistory } from 'vue-router'
import DefaultLayout from '@/layouts/DefaultLayout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: DefaultLayout,
      children: [
        {
          path: '',
          name: 'Home',
          component: () => import('@/views/Home.vue'),
          meta: { title: '首页' },
        },
        {
          path: 'article/:id',
          name: 'ArticleDetail',
          component: () => import('@/views/ArticleDetail.vue'),
          meta: { title: '文章详情' },
        },
        {
          path: 'categories',
          name: 'Categories',
          component: () => import('@/views/Categories.vue'),
          meta: { title: '分类' },
        },
        {
          path: 'tags',
          name: 'Tags',
          component: () => import('@/views/Tags.vue'),
          meta: { title: '标签' },
        },
        {
          path: 'about',
          name: 'About',
          component: () => import('@/views/About.vue'),
          meta: { title: '关于' },
        },
      ],
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: { title: '登录', plain: true },
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/Register.vue'),
      meta: { title: '注册', plain: true },
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('@/views/NotFound.vue'),
      meta: { title: '页面不存在', plain: true },
    },
  ],
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) return savedPosition
    return { top: 0 }
  },
})

router.afterEach((to) => {
  const title = to.meta?.title as string | undefined
  if (title) {
    document.title = `${title} · NightGlow Blog`
  } else {
    document.title = 'NightGlow Blog'
  }
})

export default router
