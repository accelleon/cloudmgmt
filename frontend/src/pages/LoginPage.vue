<template>
  <q-page class="window-height windows-width row justify-center items-center">
    <div class="column">
      <div class="row">
        <q-card square bordered class="q-pa-lg shadow-1">
          <q-card-section>
            <div class="text-h5">Cloud Management</div>
          </q-card-section>

          <q-separator />

          <q-card-section>
            <q-form class="q-gutter-md" @submit="onSubmit">
              <q-input
                ref="nameRef"
                square
                filled
                v-model="name"
                type="text"
                label="Username"
                autofocus
                lazy-rules
                :rules="[ val => val && val.length > 0 || 'Username cannot be empty']"
              />
              <q-input
                ref="passRef"
                square
                filled
                v-model="pass"
                label="Password"
                lazy-rules
                :rules="[ val => val && val.length > 0 || 'Password cannot be empty']"
                :type="isPwd ? 'password' : 'text'"
              >
                <template v-slot:append>
                  <q-icon
                    :name="isPwd ? 'visibility_off' : 'visibility'"
                    class="cursor-pointer"
                    @click="isPwd = !isPwd"
                  />
                </template>
              </q-input>
            </q-form>
          </q-card-section>
          <q-card-actions vertical>
            <q-btn
              unelevated
              color="light-green-7"
              size="lg"
              class="full-width"
              label="Login"
              @click="onSubmit"
            />
          </q-card-actions>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<style scoped>
.q-card {
  max-width: 360px;
}
</style>

<script>
import { useQuasar, SessionStorage } from 'quasar';
import { ref, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import { api } from 'boot/axios';

export default {
  name: 'LoginPage',
  setup() {
    const $q = useQuasar();
    const router = useRouter();

    const isPwd = ref(true);

    const name = ref(null);
    const nameRef = ref(null);

    const pass = ref(null);
    const passRef = ref(null);

    onBeforeUnmount(() => {
        $q.loading.hide();
      })

    return {
      isPwd,
      name,
      nameRef,
      pass,
      passRef,

      onSubmit() {
        nameRef.value.validate()
        passRef.value.validate()
        
        if (!nameRef.value.hasError && !passRef.value.hasError) {
          $q.loading.show()

          api.post('/login', {
              username: name.value,
              password: pass.value,
            }).then((resp) => {
              SessionStorage.set('token', resp.data.access_token)
              router.push({ name: 'main' })
            }).catch((err) => {
              if (err.response.status === 403) {
                // Server is requesting 2fa
                console.log('Requested 2fa code')
              } else if (err.response.status === 401) {
                // Denied access
                $q.notify({
                  type: 'negative',
                  message: 'Incorrect username/password'
                })
                $q.loading.hide()
              }
            })
        }
      },
    };
  },
};
</script>