<template>
  <q-card square bordered class="q-pa-lg shadow-1">
    <q-card-section>
      <div class="text-h5">Cloud Management</div>
    </q-card-section>

    <q-separator />
    <q-card-section class="q-pa-none">
      <q-form @submit="onSubmit" class="q-px-sm q-pt-md">
        <q-input
          class="q-my-md full-width"
          ref="nameRef"
          square
          filled
          v-model="name"
          type="text"
          label="Username"
          autofocus
          lazy-rules
          :rules="[
            (val) => (val && val.length > 0) || 'Username cannot be empty',
          ]"
        />
        <q-input
          class="q-my-md full-width"
          ref="passRef"
          square
          filled
          v-model="pass"
          label="Password"
          lazy-rules
          :rules="[
            (val) => (val && val.length > 0) || 'Password cannot be empty',
          ]"
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
    <q-card-actions class="q-pb-md">
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
</template>

<style lang="scss">
.q-card {
  width: 400px;
  margin: auto;
}
</style>

<script>
import { defineComponent, ref } from 'vue';

export default defineComponent({
  emits: ['submit'],

  setup(props, { emit }) {
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
        nameRef.value.validate();
        passRef.value.validate();
        if (!nameRef.value.hasError && !passRef.value.hasError) {
          emit('submit', {
            username: name.value,
            password: pass.value,
          });
        }
      },
    };
  },
});
</script>
