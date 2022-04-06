<template>
  <q-dialog ref="dialogRef" @hide="onHide" @show="onShow">
    <div class="row window-width">
      <q-card class="q-dialog-plugin">
        <q-card-section>
          <div class="text-h5">Edit User</div>
        </q-card-section>

        <q-separator />

        <q-card-section>
          <q-tabs v-model="tab">
            <q-tab name="general" icon="person" label="General" />
            <q-tab name="security" icon="key" label="Security" />
            <q-tab name="permissions" icon="lock" label="Permissions" />
          </q-tabs>

          <q-tab-panels
            class="q-py-md"
            v-model="tab"
            animated
            swipeable
            keep-alive
          >
            <q-tab-panel name="general">
              <q-form class="q-gutter-md" @submit="onSubmit">
                <q-input
                  class="full-width"
                  ref="usernameRef"
                  square
                  filled
                  v-model="username"
                  label="Username"
                  autofocus
                  lazy-rules
                  :rules="uname_rules"
                />
                <q-input
                  class="full-width"
                  ref="firstNameRef"
                  square
                  filled
                  v-model="firstName"
                  label="First Name"
                  lazy-rules
                  :rules="(val: string) => val != props.user.first_name ? [(val: string) => val || 'First Name is required'] : []"
                />
                <q-input
                  class="full-width"
                  ref="lastNameRef"
                  square
                  filled
                  v-model="lastName"
                  label="Last Name"
                  lazy-rules
                  :rules="(val: string) => val != props.user.last_name ? [(val: string) => val || 'Last Name is required'] : []"
                />
              </q-form>
            </q-tab-panel>
            <q-tab-panel name="security">
              <q-form class="q-gutter-md" @submit="onSubmit">
                <q-input
                  class="full-width"
                  ref="passwordRef"
                  square
                  filled
                  v-model="password"
                  type="password"
                  label="New Password"
                  lazy-rules
                  :rules="pwd_rules"
                >
                  <template v-slot:append>
                    <q-icon
                      :name="isPwd ? 'visibility_off' : 'visibility'"
                      class="cursor-pointer"
                      @click="isPwd = !isPwd"
                    />
                  </template>
                </q-input>
                <q-input
                  class="full-width"
                  ref="confirmRef"
                  square
                  filled
                  v-model="confirmPassword"
                  label="Confirm Password"
                  lazy-rules
                  :type="isPwd1 ? 'text' : 'password'"
                  :rules="confirm_rules"
                >
                  <template v-slot:append>
                    <q-icon
                      :name="isPwd1 ? 'visibility_off' : 'visibility'"
                      class="cursor-pointer"
                      @click="isPwd1 = !isPwd1"
                    />
                  </template>
                </q-input>
                <q-checkbox
                  ref="twofaEnabledRef"
                  square
                  filled
                  v-model="twofaEnabled"
                  label="Two-Factor Authentication Enabled"
                  :disable="!$props.user.twofa_enabled"
                />
              </q-form>
            </q-tab-panel>
            <q-tab-panel name="permissions">
              <q-form class="q-gutter-md" @submit="onSubmit">
                <q-checkbox
                  ref="isAdminRef"
                  v-model="isAdmin"
                  type="checkbox"
                  label="Administrator"
                />
              </q-form>
            </q-tab-panel>
          </q-tab-panels>
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
import { defineComponent, ref, PropType, computed } from 'vue';
import { password_rules, name_rules } from 'src/core/validation';
import { User } from 'src/models/User';
import { UserService } from 'src/services/UserService';
import { UpdateUser } from 'src/models/UpdateUser';

export default defineComponent({
  emits: [...useDialogPluginComponent.emits],

  props: {
    user: {
      type: Object as PropType<User>,
      required: true,
    },
  },

  setup(props) {
    const $q = useQuasar();
    const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } =
      useDialogPluginComponent();

    const username = ref();
    const usernameRef = ref();
    const password = ref();
    const passwordRef = ref();
    const confirmPassword = ref();
    const confirmRef = ref();
    const firstName = ref();
    const lastName = ref();
    const isAdmin = ref();
    const twofaEnabled = ref();
    const isPwd = ref(false);
    const isPwd1 = ref(false);
    const tab = ref('general');

    const uname_rules = computed(() => {
      if (props.user.username === username.value) {
        return [(val: string) => true];
      } else {
        return [...name_rules];
      }
    });

    const confirm_rules = computed(() => [
      (val: string) =>
        (password.value && val && val.length) || 'Password is required',
      (val: string) => val === password.value || 'Passwords do not match',
    ]);

    const pwd_rules = computed(() => {
      if (password.value) {
        return [...password_rules];
      } else {
        return [(val: string) => true];
      }
    });

    return {
      dialogRef,
      isPwd,
      isPwd1,

      async onSubmit() {
        usernameRef.value.validate();
        if (passwordRef.value) {
          passwordRef.value.validate();
          confirmRef.value.validate();
        }

        if (
          usernameRef.value.hasError ||
          (passwordRef.value && passwordRef.value.hasError) ||
          (confirmRef.value && confirmRef.value.hasError)
        ) {
          return;
        }

        // Return if nothing changed
        if (
          username.value == props.user.username &&
          firstName.value == props.user.first_name &&
          lastName.value == props.user.last_name &&
          isAdmin.value == props.user.is_admin &&
          twofaEnabled.value == props.user.twofa_enabled &&
          !password.value
        ) {
          $q.notify({
            color: 'positive',
            message: 'No changes made.',
          });
          onDialogCancel();
          return;
        }

        const user: UpdateUser = {
          username:
            username.value != props.user.username ? username.value : undefined,
          password: password.value ? password.value : undefined,
          first_name: firstName.value,
          last_name: lastName.value,
          is_admin: isAdmin.value,
          twofa_enabled: twofaEnabled.value,
        };

        await UserService.updateUser(props.user.id!, user)
          .then(() => {
            onDialogOK();
          })
          .catch(() => {
            $q.notify({
              color: 'negative',
              message: 'Failed to update user',
            });
          });
      },

      async onShow(_evt: any) {
        username.value = props.user.username;
        firstName.value = props.user.first_name;
        lastName.value = props.user.last_name;
        isAdmin.value = props.user.is_admin;
        twofaEnabled.value = props.user.twofa_enabled;
      },

      async onHide(_evt: any) {
        onDialogHide();
      },

      async onCancel(_evt: any) {
        onDialogCancel();
      },

      pwd_rules,
      confirm_rules,
      uname_rules,
      props,

      username,
      usernameRef,
      password,
      passwordRef,
      firstName,
      lastName,
      isAdmin,
      twofaEnabled,
      tab,
    };
  },
});
</script>
