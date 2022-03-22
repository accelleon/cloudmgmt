import { defineStore } from 'pinia';
import { LocalStorage } from 'quasar';
import { api } from 'boot/axios';

export interface authPost {
  username: string;
  password: string;
  twofa_code?: string;
}

interface authState {
  token: string | null;
  authenticated: boolean;
}

export const useAuthStore = defineStore('auth', {
  state: () => {
    return {
      token: (LocalStorage.getItem('auth_token')  || null),
      authenticated: (LocalStorage.getItem('auth_token') ? true : false),
    } as authState;
  },

  getters: {
    isAuthenticated: (state) => state.authenticated,
  },

  actions: {
    async login(data: authPost) {
      await api.post('/login', data).then((resp) => {
        const token = resp.data.access_token;
        this.authenticated = true;
        this.token = token;
        LocalStorage.set('auth_token', token);
        return Promise.resolve();
      }).catch((err) => {
        return Promise.reject(err.response);
      });
    },

    logout() {
      this.authenticated = false;
      this.token = null;
      LocalStorage.remove('auth_token');
    }
  }
});