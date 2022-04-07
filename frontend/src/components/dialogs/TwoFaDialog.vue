<template>
  <q-dialog ref="dialogRef" @before-show="onShow" @hide="onHide">
    <div class="row window-width">
      <q-card class="q-dialog-plugin">
        <q-card-section>
          <div class="text-h5">Enable 2FA</div>
        </q-card-section>

        <q-separator />

        <q-card-section horizontal>
          <q-card-section>
            <canvas id="qr-code"></canvas>
          </q-card-section>

          <div class="row items-center">
            <q-card-section>
              <div class="q-pa-md">
                Scan the QR code to the right with you're prefered Google
                compatible Authenticator app
              </div>
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
                  :rules="[
                    (val) =>
                      (val && val.length == 6) || 'Code must be 6 digits',
                  ]"
                />
              </q-form>
            </q-card-section>
          </div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn color="primary" label="Cancel" @click="onCancel" />
          <q-btn color="primary" label="Submit" @click="onSubmit" />
        </q-card-actions>
      </q-card>
    </div>
  </q-dialog>
</template>

<style>
.q-card {
  width: 1500px;
}
.q-input {
  width: 200px;
}
</style>

<script>
import { useDialogPluginComponent, useQuasar } from 'quasar';
import { ref, defineComponent } from 'vue';
import QRious from 'qrious';
import { useUserStore } from 'src/stores/user-store';

export default defineComponent({
  emits: [...useDialogPluginComponent.emits],

  setup() {
    const $q = useQuasar();
    const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } =
      useDialogPluginComponent();
    const store = useUserStore();

    const codeRef = ref(null);
    const code = ref(null);

    return {
      dialogRef,
      onDialogHide,
      codeRef,
      code,

      onShow(_evt) {
        // Our first call gives us our URI
        store
          .enableTwoFa()
          .then((twofa_uri) => {
            if (!twofa_uri) {
              return Promise.reject("Didn't get a URI");
            }
            new QRious({
              level: 'H',
              padding: 25,
              size: 280,
              element: document.getElementById('qr-code'),
              value: twofa_uri,
            });
          })
          .catch((err) => {
            $q.notify({
              type: 'negative',
              message: err.body?.detail || err,
            });
            onDialogCancel();
          });
      },

      onSubmit() {
        codeRef.value.validate();

        if (!codeRef.value.hasError) {
          store
            .enableTwoFa(code.value)
            .then(() => {
              $q.notify({
                type: 'positive',
                message: '2FA enabled',
              });
              onDialogOK();
            })
            .catch((err) => {
              // Some error
              $q.notify({
                type: 'negative',
                message: err.data?.detail || err,
              });
            });
        }
      },

      async onHide(_evt) {
        // If we didn't finish enabling 2fa send a disable
        // to clear temp secret
        if (!store.user.twofa_enabled) {
          store.disableTwoFa();
        }
        onDialogHide();
      },

      // Disabling incomplete 2fa can be done in onHide
      onCancel: onDialogCancel,
    };
  },
});
</script>
