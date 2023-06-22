import { createRouter, createWebHistory } from 'vue-router'
import EditCaseDetails from '../components/EditCaseDetails.vue'
import ViewCaseDetails from '../components/ViewCaseDetails.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
  },
  {
    path: '/editCase/:id',
    name: 'editCaseDetails',
    component: EditCaseDetails,
    props: true
  },
  {
    path: '/viewCase/:id',
    name: 'viewCaseDetails',
    component: ViewCaseDetails,
    props: true
  },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
})

export default router
