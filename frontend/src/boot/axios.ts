import { boot } from 'quasar/wrappers';
import axios, { AxiosInstance } from 'axios';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';

import { useAuthStore } from 'stores/auth-store';

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $axios: AxiosInstance;
  }
}

// Be careful when using SSR for cross-request state pollution
// due to creating a Singleton instance here;
// If any client changes this (global) instance, it might be a
// good idea to move this instance creation inside of the
// "export default () => {}" function below (which runs individually
// for each client)
const api = axios.create({
  baseURL: process.env.NODE_ENV !== 'prod' ? 'http://172.31.7.183:8000/api/v1' : 'http://potato.net'
});
api.defaults.headers.post['Content-Type'] = 'application/json';

api.interceptors.request.use(
  config => {
    // If we're authenticated, pull our token
    const store = useAuthStore();
    if (store.isAuthenticated) {
      config.headers.Authorization = `Bearer ${store.token}`;
    }

    return config;
  },
  error => Promise.reject(error)
);

api.interceptors.response.use(
  resp => resp,
  error => {
    // If we get a 401 invalidate our session
    if (error.response.status == 401) {
      const store = useAuthStore();
      if (store.isAuthenticated) {
        const router = useRouter();
        const $q = useQuasar();
        store.logout();
        $q.notify({
          type: 'negative',
          message: 'Your session has expired.',
        });
        router.push('/login');
      }
    }
    return Promise.reject(error);
  }
)

export default boot(({ app }) => {
  // for use inside Vue files (Options API) through this.$axios and this.$api

  app.config.globalProperties.$axios = axios;
  // ^ ^ ^ this will allow you to use this.$axios (for Vue Options API form)
  //       so you won't necessarily have to import axios in each vue file

  app.config.globalProperties.$api = api;
  // ^ ^ ^ this will allow you to use this.$api (for Vue Options API form)
  //       so you can easily perform requests against your app's API
});

export { api };
