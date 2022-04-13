<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-toolbar-title> Cloud Management </q-toolbar-title>

        <div>Quasar v{{ $q.version }}</div>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-card square class="absolute-top full-width row" style="height: 150px">
        <div class="col-10 q-pa-lg text-h6">{{ user.fullname }}</div>
        <div class="col-2" align="right">
          <div class="q-pa-sm">
            <q-btn flat rounded padding="none" @click="pinned = !pinned">
              <q-icon
                :name="pinned ? 'push_pin' : 'o_push_pin'"
                :class="pinned ? '' : 'rotate-90'"
              />
              <q-tooltip
                anchor="center right"
                self="center left"
                :offset="[10, 10]"
              >
                Pin/Unpin the navigation drawer.
              </q-tooltip>
            </q-btn>
          </div>
          <div class="q-pa-sm absolute-bottom">
            <q-btn-dropdown
              flat
              rounded
              padding="none"
              dropdown-icon="manage_accounts"
              no-icon-animation
              auto-close
            >
              <template v-slot:label>
                <q-tooltip
                  anchor="center right"
                  self="center left"
                  :offset="[10, 10]"
                >
                  Manage profile.
                </q-tooltip>
              </template>

              <q-list>
                <q-item clickable @click="changePassword">
                  <q-item-section avatar>
                    <q-icon name="lock" size="md" />
                  </q-item-section>
                  <q-item-section>Change Password</q-item-section>
                </q-item>
                <q-item>
                  <q-item-section avatar>
                    <q-icon name="pin" size="md" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>2FA</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-toggle
                      v-model="twofa"
                      checked-icon="check"
                      unchecked-icon="clear"
                      color="green"
                      @update:model-value="onTwofaChange"
                    />
                  </q-item-section>
                </q-item>
                <q-item clickable @click="logout">
                  <q-item-section avatar>
                    <q-icon name="exit_to_app" size="md" />
                  </q-item-section>
                  <q-item-section>Logout</q-item-section>
                </q-item>
              </q-list>
            </q-btn-dropdown>
          </div>
        </div>
        <q-separator />
      </q-card>

      <q-scroll-area
        style="
          height: calc(100% - 220px);
          margin-top: 150px;
          margin-bottom: 70px;
        "
      >
        <q-tabs vertical inline-label stretch>
          <q-route-tab icon="receipt_long" label="Billing" to="#" />
          <q-route-tab icon="delete_sweep" label="Purge" to="#" />
          <q-route-tab icon="manage_accounts" label="Users" to="/users" />
          <q-route-tab icon="groups" label="Groups" to="#" />
          <q-route-tab icon="cloud" label="Accounts" to="/accounts" />
          <q-route-tab icon="settings" label="Settings" to="#" />
        </q-tabs>
      </q-scroll-area>

      <div class="absolute-bottom justify-center row" style="height: 70px">
        <div class="column q-pa-lg">
          <q-btn square label="Log out" icon="logout" />
        </div>
      </div>
    </q-drawer>

    <q-page-container class="container-fluid">
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { useUserStore } from 'src/stores/user-store';
import TwoFaDialog from 'src/components/dialogs/TwoFaDialog.vue';
import ChangePasswordDialog from 'src/components/dialogs/ChangePasswordDialog.vue';
import { useAuthStore } from 'src/stores/auth-store';
import { useRouter } from 'vue-router';

export default defineComponent({
  name: 'MainLayout',

  setup() {
    const leftDrawerOpen = ref(false);
    const pinned = ref(true);
    const link = ref('');
    const $q = useQuasar();
    const $router = useRouter();
    const user = useUserStore();

    const twofa = ref(false);

    onMounted(async () => {
      await user.getUser();
      twofa.value = user.user.twofa_enabled!;
    });

    async function enableTwofa() {
      $q.dialog({
        title: 'Enable Two-Factor Authentication',
        component: TwoFaDialog,
      }).onOk(() => {
        twofa.value = true;
      });
    }

    async function disableTwofa() {
      // Confirm disabling two-factor authentication.
      $q.dialog({
        title: 'Disable Two-Factor Authentication',
        message: 'Are you sure you want to disable two-factor authentication?',
        color: 'negative',
      }).onOk(async () => {
        user
          .disableTwoFa()
          .then(() => {
            $q.notify({
              message: 'Two-Factor Authentication disabled.',
              color: 'positive',
              icon: 'check',
            });
            twofa.value = false;
          })
          .catch(() => {
            $q.notify({
              message: 'Two-Factor Authentication could not be disabled.',
              color: 'negative',
              icon: 'error',
            });
          });
      });
    }

    return {
      pinned,
      link,
      user,
      twofa,
      leftDrawerOpen,

      changePassword: () => {
        $q.dialog({
          component: ChangePasswordDialog,
          title: 'Change Password',
        });
      },

      logout: () => {
        useAuthStore().logout();
        $router.push('/login');
      },

      onTwofaChange: (value: any, _evt: any) => {
        if (value) {
          enableTwofa();
        } else {
          disableTwofa();
        }
        twofa.value = user.user.twofa_enabled!;
      },
    };
  },
});
</script>
