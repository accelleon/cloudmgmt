import { defineStore } from 'pinia';
import { useQuasar, LocalStorage } from 'quasar';
import { api } from 'boot/axios';

import TwoFaDialog from 'dialogs/TwoFaDialog.vue'

export const useAuthStore = defineStore('auth', {
  state: () => {
    return {
      token: null,
      authenticated: false,
    }
  },

  getters: {
    isAuthenticated: (state) => state.authenticated,
  },

  actions: {
    login(user: string, pass: string) {
      const $q = useQuasar();
      api.post('/login', {
        username: user,
        password: pass,
      }).then((resp) => {
        this.token = resp.data.access_token;
        this.authenticated = true;
      }).catch((err) => {
        $q.dialog({
          component: TwoFaDialog,
        }).onOk(() => {
          console.log('OK')
        }).onCancel(() => {
          console.log('Cancel')
        }).onDismiss(() => {
          console.log('One of the two')
        })
        return err
      })
    },
  }
});