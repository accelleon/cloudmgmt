import { defineStore } from 'pinia';
import { LocalStorage } from 'quasar';
import { AuthRequest, LoginService } from '..';
import jwt_decode from 'jwt-decode';

interface authState {
  token: string | null;
}

interface Token {
  sub: number;
  exp: number;
  iat: number;
}

export const useAuthStore = defineStore('auth', {
  state: () => {
    return {
      token: LocalStorage.getItem('auth_token') || null,
    } as authState;
  },

  getters: {
    isAuthenticated: (state) => {
      if (!state.token) {
        return false;
      }
      const token: Token = jwt_decode(state.token);

      if (token.exp * 1000 < Date.now()) {
        return false;
      }
      return true;
    },
  },

  actions: {
    async login(data: AuthRequest) {
      await LoginService.login(data)
        .then((resp) => {
          const token = resp.access_token;
          this.token = token;
          LocalStorage.set('auth_token', token);
          return Promise.resolve();
        })
        .catch((err) => {
          return Promise.reject(err);
        });
    },

    logout() {
      this.token = null;
      LocalStorage.remove('auth_token');
      window.location.reload();
    },
  },
});
