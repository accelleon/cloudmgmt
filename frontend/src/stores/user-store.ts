import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { useAuthStore } from './auth-store';
import { UpdateUser, UpdateUserResp, User } from 'src/model/users';

export const useUserStore = defineStore('user', {
  state: () => {
    return {
      user: {} as User,
    }
  },

  getters: {
    fullname: (state) => `${state.user.first_name} ${state.user.last_name}`,
  },

  actions: {
    async getUser() {
      const auth = useAuthStore();
      if (!auth.isAuthenticated) {
        return Promise.reject('User not authenticated');
      }
      await api.get('users/me').then((resp) => {
        this.user = resp.data as User;
        return Promise.resolve();
      }).catch((err) => {
        this.user = {} as User;
        return Promise.reject(err);
      })
    },

    async enableTwoFa(passcode?: string) {
      await this.getUser();
      if (!this.user.id) {
        return Promise.reject('User not authenticated');
      }

      // If we don't have a passcode, we need to get the
      // URI from the API and open the TwoFa Dialog
      if (!passcode) {
        const data: UpdateUser = {
          twofa_enabled: true,
        }
        return api.post('users/me', data).then((resp) => {
          const user = resp.data as UpdateUserResp;
          if (!user.twofa_uri) {
            return Promise.reject('This shouldn\'t happen...')
          }
          // This gets returned as a reference so copy the string
          return Promise.resolve(`${user.twofa_uri}`);
        }).catch((err) => {
          return Promise.reject(err);
        });
      } else {
        const data: UpdateUser = {
          twofa_enabled: true,
          twofa_code: passcode,
        }
        await api.post('users/me', data).then(async (resp) => {
          const user = resp.data as UpdateUserResp;
          if (!user.twofa_enabled) {
            return Promise.reject('Successful response but failed to enable 2FA')
          }
          // Store our new state
          this.user = user;
          return Promise.resolve();
        }).catch((err) => {
          if (err.response) {
            return Promise.reject(err.response);
          } else {
            return Promise.reject(err);
          }
        });
      }
    },

    async disableTwoFa() {
      const data: UpdateUser = {
        twofa_enabled: false,
      }
      api.post('users/me', data).then((resp) => {
        const user = resp.data as UpdateUserResp;
        if(user.twofa_enabled) {
          return Promise.reject('Successful response but failed to disable 2FA');
        }
      }).catch((err) => {
        if (err.response) {
          return Promise.reject(err.response);
        } else {
          return Promise.reject(err);
        }
      });
    }
  }
});