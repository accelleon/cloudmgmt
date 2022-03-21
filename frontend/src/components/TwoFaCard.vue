<template>
  <q-card square bordered class="q-pa-lg shadow-1">
    <q-card-section>
      <div class="text-h5">Authenticator Code</div>
    </q-card-section>

    <q-separator/>

    <q-card-section>
      <q-form class="q-gutter-md" @submit="onSubmit">
        <q-input
          ref="codeRef"
          square
          filled
          v-model="code"
          type="text"
          label="Authenticator Code"
          autofocus
          mask="######"
          lazy-rules
          :rules="[ val => val && val.length !== 6 || 'Code must be 6 digits']"
        />
      </q-form>
    </q-card-section>
    
    <q-card-actions align="right">
      <q-btn color="primary" label="Submit" @click="onSubmit" />
      <q-btn color="primary" label="Cancel" @click="$emit('cancel')" />
    </q-card-actions>
  </q-card>
</template>

<script>
import { useQuasar } from "quasar";
import { ref, defineComponent } from "vue";

export default defineComponent({
  emits: ['submit', 'cancel'],

  setup(props, { emit }) {
    const $q = useQuasar();

    const code = ref(null);
    const codeRef = ref(null);

    return {
      code,
      codeRef,

      onSubmit() {
        codeRef.value.validate();

        if (!codeRef.value.hasError) {
          emit('submit', {
            twofa_code: code.value,
          });
        }
      }
    }
  }
})
</script>