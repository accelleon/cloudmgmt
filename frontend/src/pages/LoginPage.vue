<template>
  <q-page class="window-height windows-width row justify-center items-center">
    <div class="column">
      <div class="row" style="max-width: 400px">
        <login-card v-if="!twofa" @submit="login" />
        <two-fa-card v-else @submit="login" @cancel="cancel" />
      </div>
    </div>
  </q-page>
</template>

<script>
import { useQuasar } from 'quasar';
import { ref, onBeforeUnmount, defineComponent } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from 'src/stores/auth-store';
import LoginCard from 'components/LoginCard.vue';
import TwoFaCard from 'components/TwoFaCard.vue';

export default defineComponent({
  name: 'LoginPage',

  setup() {
    const $q = useQuasar();
    const router = useRouter();
    const route = useRoute();
    const twofa = ref(false);

    var data = {
      username: null,
      password: null,
      twofa_code: null,
    };

    onBeforeUnmount(() => {
      $q.loading.hide();
    });

    return {
      twofa,

      async login(e) {
        const store = useAuthStore();
        $q.loading.show();
        if (!twofa.value) {
          data = e;
        } else {
          data.twofa_code = e.twofa_code;
        }

        await store
          .login(data)
          .then(() => {
            router.push(route.query.next || '/');
          })
          .catch((err) => {
            if (err.status == 403 && err.body.twofa_required) {
              // Required 2fa
              twofa.value = true;
              $q.loading.hide();
            } else {
              // Some other error
              $q.loading.hide();
              $q.notify({
                type: 'negative',
                message: err.body?.detail || err.message,
              });
            }
          });
      },

      cancel() {
        twofa.value = false;
        data.twofa_code = null;
      },
    };
  },
  components: { LoginCard, TwoFaCard },
});
</script>
