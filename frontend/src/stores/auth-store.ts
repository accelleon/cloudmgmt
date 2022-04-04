import { defineStore } from 'pinia';
import { LocalStorage } from 'quasar';
import { AuthRequest, LoginService, OpenAPI } from '..';

interface authState {
  token: string | null;
  authenticated: boolean;
}

export const useAuthStore = defineStore('auth', {
  state: () => {
    return {
      token: LocalStorage.getItem('auth_token') || null,
      authenticated: LocalStorage.getItem('auth_token') ? true : false,
    } as authState;
  },

  getters: {
    isAuthenticated: (state) => state.authenticated,
  },

  actions: {
    async login(data: AuthRequest) {
      await LoginService.loginApiV1LoginPost(data)
        .then((resp) => {
          const token = resp.access_token;
          this.authenticated = true;
          this.token = token;
          OpenAPI.TOKEN = token;
          LocalStorage.set('auth_token', token);
          return Promise.resolve();
        })
        .catch((err) => {
          return Promise.reject(err);
        });
    },

    logout() {
      this.authenticated = false;
      this.token = null;
      LocalStorage.remove('auth_token');
    },
  },
});
