<template>
  <q-dialog ref="dialogRef" @hide="onDialogHide">
    <q-card class="q-dialog-plugin">
      <q-card-section>
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
      </q-card-section>
      <q-card-actions align="right">
        <q-btn color="primary" label="Ok" @click="onOKClick" />
        <q-btn color="primary" label="Cancel" @click="onCancelClick" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script lang="ts">
import { useDialogPluginComponent } from 'quasar'

export default {
  props: {},

  emits: [
    ...useDialogPluginComponent.emits
  ],

  setup() {
    const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } = useDialogPluginComponent();

    return {
        dialogRef,
        onDialogHide,

        onOKClick() {
            onDialogOK()
        },

        onCancelClick: onDialogCancel
    }
  }
}

</script>