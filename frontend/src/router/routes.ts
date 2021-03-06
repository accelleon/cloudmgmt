import { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'main',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '/users',
        component: () => import('pages/UsersPage.vue'),
        meta: { isAdmin: true },
      },
      {
        path: '/accounts',
        component: () => import('pages/AccountsPage.vue'),
        meta: { isAdmin: true },
      },
      {
        path: '/billing',
        component: () => import('pages/BillingPage.vue'),
        meta: { requiresAuth: true },
        alias: '/',
      },
      {
        path: '/metrics',
        component: () => import('pages/MetricsPage.vue'),
        meta: { requiresAuth: true },
      },
    ],
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('layouts/LoginLayout.vue'),
    children: [{ path: '', component: () => import('pages/LoginPage.vue') }],
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;
