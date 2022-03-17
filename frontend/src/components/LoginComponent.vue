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
            <q-form class="q-gutter-md">
              <q-input
                ref="nameRef"
                square
                filled
                v-model="name"
                type="text"
                label="username"
                lazy-rules
                :rules="[ val => val && val.length > 0 || 'Username cannot be empty']"
              />
              <q-input
                ref="passRef"
                square
                filled
                v-model="pass"
                label="password"
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
              type="submit"
              @click="onSubmit()"
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
import { useQuasar } from 'quasar';
import { ref } from 'vue';
import { api } from 'boot/axios';

export default {
  name: 'LoginComponent',
  setup() {
    const $q = useQuasar();
    const isPwd = ref(true);
    const name = ref(null);
    const nameRef = ref(null);
    const pass = ref(null);
    const passRef = ref(null);

    return {
      isPwd,
      name,
      nameRef,
      pass,
      passRef,

      onSubmit() {
        nameRef.value.validate()
        passRef.value.validate()

        if(nameRef.value.hasError || passRef.value.hasError) {

        }
        else {
          $q.loading.show()

          api.post('/login', {
              username: name.value,
              password: pass.value,
            });

          $q.notify({
            color: 'green-4',
            textColor: 'white',
            message: 'Submitted',
          });
        }
      },
    };
  },
};
</script>