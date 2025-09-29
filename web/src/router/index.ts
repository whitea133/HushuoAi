import { createRouter, createWebHashHistory } from 'vue-router'
// import HomeView from '../views/HomeView.vue'

const router = createRouter({
  // history: createWebHistory(import.meta.env.BASE_URL),
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: () => import("../views/index.vue"),
    },
    {
      path: '/textTool',
      // name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/textTool.vue'),
    },
    {
       path: '/videoTool',
       component: () => import('../views/videoTool.vue'),
    },
        {
       path: '/voiceTool',
       component: () => import('../views/voiceTool.vue'),
    }
  ],
})

export default router
