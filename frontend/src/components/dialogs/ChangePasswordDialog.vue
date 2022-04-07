<template>
  <q-dialog ref="dialogRef" @hide="onHide">
    <div class="row">
      <q-card class="q-dialog-plugin">
        <q-card-section>
          <div class="text-h5">Change Password</div>
        </q-card-section>

        <q-separator />

        <q-card-section>
          <q-form class="q-px-sm" @submit="onSubmit">
            <q-input
              class="q-my-md full-width"
              ref="oldPasswordRef"
              square
              filled
              v-model="oldPassword"
              label="Old Password"
              autofocus
              lazy-rules
              :type="isPwd1 ? 'password' : 'text'"
              :rules="[
                (val) => (val && val.length) || 'Old Password is required',
              ]"
            >
              <template v-slot:append>
                <q-icon
                  :name="isPwd1 ? 'visibility_off' : 'visibility'"
                  class="cursor-pointer"
                  @click="isPwd1 = !isPwd1"
                />
              </template>
            </q-input>
            <q-input
              class="q-my-md full-width"
              ref="newPasswordRef"
              square
              filled
              v-model="newPassword"
              label="New Password"
              lazy-rules
              :type="isPwd2 ? 'password' : 'text'"
              :rules="pwd_rules"
            >
              <template v-slot:append>
                <q-icon
                  :name="isPwd2 ? 'visibility_off' : 'visibility'"
                  class="cursor-pointer"
                  @click="isPwd2 = !isPwd2"
                />
              </template>
            </q-input>
            <q-input
              class="q-my-md full-width"
              ref="confirmPasswordRef"
              square
              filled
              v-model="confirmPassword"
              label="Confirm Password"
              lazy-rules
              :type="isPwd3 ? 'password' : 'text'"
              :rules="confirm_rules"
            >
              <template v-slot:append>
                <q-icon
                  :name="isPwd3 ? 'visibility_off' : 'visibility'"
                  class="cursor-pointer"
                  @click="isPwd3 = !isPwd3"
                />
              </template>
            </q-input>
          </q-form>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn color="primary" label="Cancel" @click="onCancel" />
          <q-btn color="primary" label="Submit" @click="onSubmit" />
        </q-card-actions>
      </q-card>
    </div>
  </q-dialog>
</template>

<script lang="ts">
import { useDialogPluginComponent, useQuasar } from 'quasar';
import { defineComponent, ref, computed } from 'vue';
import { password_rules } from 'src/core/validation';
import { useUserStore } from 'src/stores/user-store';

export default defineComponent({
  emits: [...useDialogPluginComponent.emits],

  setup() {
    const $q = useQuasar();
    const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } =
      useDialogPluginComponent();

    const oldPassword = ref<string>('');
    const oldPasswordRef = ref();
    const newPassword = ref<string>('');
    const newPasswordRef = ref();
    const confirmPassword = ref<string>('');
    const confirmPasswordRef = ref();
    const isPwd1 = ref(true);
    const isPwd2 = ref(true);
    const isPwd3 = ref(true);

    const pwd_rules = computed(() => [
      ...password_rules,
      (val: string) =>
        val != oldPassword.value ||
        'New password cannot be the same as old password',
    ]);

    const confirm_rules = computed(() => [
      (val: string) => (val && val.length) || 'Confirm password is required',
      (val: string) =>
        (val && val === newPassword.value) || 'Passwords do not match',
    ]);

    return {
      dialogRef,
      onDialogHide,

      pwd_rules,
      confirm_rules,

      isPwd1,
      isPwd2,
      isPwd3,

      oldPassword,
      oldPasswordRef,
      newPassword,
      newPasswordRef,
      confirmPassword,
      confirmPasswordRef,

      async onSubmit() {
        oldPasswordRef.value.validate();
        newPasswordRef.value.validate();
        confirmPasswordRef.value.validate();

        if (
          !oldPasswordRef.value.error &&
          !newPasswordRef.value.error &&
          !confirmPasswordRef.value.error
        ) {
          await useUserStore()
            .changePassword(oldPassword.value, newPassword.value)
            .then(() => {
              $q.notify({
                message: 'Password changed successfully',
                color: 'positive',
              });
              onDialogOK();
            })
            .catch((err) => {
              $q.notify({
                color: 'negative',
                message: err.body?.detail || err.message,
              });
            });
        }
      },

      onHide(_evt: any) {
        onDialogHide();
      },

      onCancel: onDialogCancel,
    };
  },
});
</script>
