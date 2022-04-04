import { defineStore } from 'pinia';
import { useAuthStore } from './auth-store';
import { User, UserService } from '..';

export const useUserStore = defineStore('user', {
  state: () => {
    return {
      user: {} as User,
    };
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
      await UserService.getSelfApiV1UsersMeGet()
        .then((resp) => {
          this.user = resp;
          return Promise.resolve();
        })
        .catch((err) => {
          this.user = {} as User;
          return Promise.reject(err.body?.message || err.message);
        });
    },

    async enableTwoFa(passcode?: string) {
      await this.getUser();
      if (!this.user.id) {
        return Promise.reject('User not authenticated');
      }

      // If we don't have a passcode, we need to get the
      // URI from the API and open the TwoFa Dialog
      if (!passcode) {
        return await UserService.updateSelfApiV1UsersMePost({
          twofa_enabled: true,
        })
          .then((user) => {
            if (!user.twofa_uri) {
              return Promise.reject("This shouldn't happen...");
            }
            // This gets returned as a reference so copy the string
            return Promise.resolve(`${user.twofa_uri}`);
          })
          .catch((err) => {
            return Promise.reject(err.body?.message || err.message);
          });
      } else {
        await UserService.updateSelfApiV1UsersMePost({
          twofa_enabled: true,
          twofa_code: passcode,
        })
          .then((user) => {
            if (!user.twofa_enabled) {
              return Promise.reject(
                'Successful response but failed to enable 2FA'
              );
            }
            // Store our new state
            this.user = user;
            return Promise.resolve();
          })
          .catch((err) => {
            return Promise.reject(err.body?.message || err.message);
          });
      }
    },

    async disableTwoFa() {
      await UserService.updateSelfApiV1UsersMePost({
        twofa_enabled: false,
      })
        .then((user) => {
          if (user.twofa_enabled) {
            return Promise.reject(
              'Successful response but failed to disable 2FA'
            );
          }
        })
        .catch((err) => {
          return Promise.reject(err.body?.message || err.message);
        });
    },
  },
});
