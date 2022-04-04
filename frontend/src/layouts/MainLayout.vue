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
            <q-btn rounded padding="none" @click="pinned = !pinned">
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
        </div>
        <q-separator />
        <q-card-actions>
          <q-btn square label="Profile" icon="manage_accounts" />
        </q-card-actions>
      </q-card>

      <q-scroll-area
        style="
          height: calc(100% - 220px);
          margin-top: 150px;
          margin-bottom: 70px;
          border-right: 1px solid #ddd;
        "
      >
        <q-list padding>
          <q-item
            clickable
            v-ripple
            :active="link === 'billing'"
            @click="link = 'billing'"
            active-class="my-menu-link"
          >
            <q-item-section avatar>
              <q-icon name="receipt_long" />
            </q-item-section>
            <q-item-section>Billing</q-item-section>
          </q-item>

          <q-item
            clickable
            v-ripple
            :active="link === 'purge'"
            @click="link = 'purge'"
            active-class="my-menu-link"
          >
            <q-item-section avatar>
              <q-icon name="delete_sweep" />
            </q-item-section>
            <q-item-section>Purge</q-item-section>
          </q-item>

          <q-item
            clickable
            v-ripple
            :active="link === 'users'"
            @click="link = 'users'"
            active-class="my-menu-link"
          >
            <q-item-section avatar>
              <q-icon name="manage_accounts" />
            </q-item-section>
            <q-item-section>Users</q-item-section>
          </q-item>

          <q-item
            clickable
            v-ripple
            :active="link === 'groups'"
            @click="link = 'groups'"
            active-class="my-menu-link"
          >
            <q-item-section avatar>
              <q-icon name="groups" />
            </q-item-section>
            <q-item-section>Groups</q-item-section>
          </q-item>

          <q-item
            clickable
            v-ripple
            :active="link === 'accounts'"
            @click="link = 'accounts'"
            active-class="my-menu-link"
          >
            <q-item-section avatar>
              <q-icon name="cloud" />
            </q-item-section>
            <q-item-section>Accounts</q-item-section>
          </q-item>

          <q-item
            clickable
            v-ripple
            :active="link === 'settings'"
            @click="link = 'settings'"
            active-class="my-menu-link"
          >
            <q-item-section avatar>
              <q-icon name="settings" />
            </q-item-section>
            <q-item-section>Settings</q-item-section>
          </q-item>
        </q-list>
      </q-scroll-area>

      <div class="absolute-bottom justify-center row" style="height: 70px">
        <div class="column q-pa-lg">
          <q-btn square label="Log out" icon="logout" />
        </div>
      </div>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<style lang="scss">
.my-menu-link {
  color: black;
  background: #fde08e;
}
</style>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { useQuasar } from 'quasar';
import TwoFaDialog from 'src/components/TwoFaDialog.vue';
import { useUserStore } from 'src/stores/user-store';

export default defineComponent({
  name: 'MainLayout',

  setup() {
    const leftDrawerOpen = ref(false);
    const pinned = ref(true);
    const link = ref('');
    const $q = useQuasar();
    const user = useUserStore();

    user.getUser();

    return {
      pinned,
      link,
      user,
      leftDrawerOpen,
      toggleLeftDrawer() {
        leftDrawerOpen.value = !leftDrawerOpen.value;
      },

      enableTwoFa() {
        $q.dialog({
          component: TwoFaDialog,
        });
      },

      async disableTwoFa() {
        await user.disableTwoFa();
      },
    };
  },
});
</script>
