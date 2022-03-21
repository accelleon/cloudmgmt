<template>
  <q-page class="window-height windows-width row justify-center items-center">
    <div class="column">
      <div class="row">
        <login-card v-if="!twofa" @submit="login" />
        <two-fa-card v-else @submit="login" @cancel="cancel" />
      </div>
    </div>
  </q-page>
</template>

<script>
import { useQuasar } from 'quasar';
import { ref, onBeforeUnmount, defineComponent } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from 'src/stores/auth-store';
import LoginCard from 'components/LoginCard.vue';
import TwoFaCard from 'components/TwoFaCard.vue';

export default defineComponent({
    name: 'LoginPage',
    setup() {
        const $q = useQuasar();
        const router = useRouter();
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
                data.username = e.username;
                data.password = e.password;
              } else {
                data.twofa_code = e.twofa_code;
              }
              
              try {
                await store.login(data);
              } catch (e) {
                console.log(e)
              }
              if (err) {
                if (err.response.status == 403) {
                  // Requires twofa
                  twofa.value = true;
                  $q.loading.hide();
                } else {
                  $q.notify(err.response.data.message);
                }
                router.push('main');
              }
            },

            cancel() {
              twofa.value = false;
              data.twofa_code = null;
            }
        };
    },
    components: { LoginCard, TwoFaCard }
});
</script>