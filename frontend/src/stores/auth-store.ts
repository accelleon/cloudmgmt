import { defineStore, MutationType } from 'pinia';
import { useQuasar, LocalStorage } from 'quasar';
import { api } from 'boot/axios';

interface authState {
  token: string | null;
  authenticated: boolean;
}

export const useAuthStore = defineStore('auth', {
  state: () => {
    const token = LocalStorage.getItem('auth_token') as string || null;

    return {
      token: token,
      authenticated: token ? true : false,
    } as authState;
  },

  getters: {
    isAuthenticated: (state) => state.authenticated,
  },

  actions: {
    async login(data: any) {
      const $q = useQuasar();
      const resp = await api.post('/login', {
        username: data.username,
        password: data.password,
        twofa_code: data.passcode,
      });
      if (resp.status == 200) {
        const token = resp.data.access_token;
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        this.authenticated = true;
      } else {
        return Promise.reject(resp);
      }
    },

    logout() {
      this.authenticated = false;
      this.token = null;
    }
  }
});

useAuthStore().$subscribe((mutation, state) => {
  mutation.type
  mutation.storeId
  
  LocalStorage.set('auth_token', state.token);
});