<template>
  <q-dialog ref="dialogRef" @hide="onHide">
    <div class="row window-width">
      <q-card class="q-dialog-plugin">
        <q-card-section>
          <div class="text-h5">Add Account</div>
        </q-card-section>

        <q-separator />

        <q-card-section>
          <q-tabs v-model="tab">
            <q-tab name="1" label="General" />
            <q-tab name="2" label="Security" :disable="iaas == null" />
          </q-tabs>
          <q-tab-panels
            class="q-py-md"
            v-model="tab"
            animated
            swipeable
            keep-alive
          >
            <q-tab-panel name="1">
              <q-form ref="gen" @keyup.enter="onSubmit">
                <q-select
                  class="full-width"
                  ref="iaasRef"
                  square
                  filled
                  v-model="iaas"
                  label="Provider"
                  option-label="name"
                  map-options
                  :options="iaasOptions"
                  lazy-rules
                  :rules="[(val: any) => (val) || 'Provider is required']"
                />
                <q-input
                  class="full-width"
                  ref="accountName"
                  name="accountName"
                  square
                  filled
                  v-model="account.name"
                  label="Account Name"
                  autofocus
                  lazy-rules
                  :rules="[(val: string) => (val && val.length) || 'Name is required']"
                />
              </q-form>
            </q-tab-panel>
            <q-tab-panel name="2" :disable="iaas == null">
              <q-form ref="sec">
                <div v-if="iaas" class="q-px-none">
                  <div v-for="param in iaas.params" :key="param.key">
                    <q-input
                      v-if="param.type === 'string' || param.type === 'secret'"
                      v-model="account.data[param.key]"
                      class="full-width q-py-md"
                      filled
                      square
                      :label="param.label"
                      lazy-rules
                      :rules="[(val: string) => (val && val.length) || 'Value is required']"
                    />
                    <q-select
                      v-if="param.type === 'choice'"
                      v-model="account.data[param.key]"
                      class="full-width q-py-md"
                      filled
                      square
                      :label="param.label"
                      :options="param.choices"
                      lazy-rules
                      :rules="[(val: any) => (val != null) || 'Value is required']"
                    />
                  </div>
                </div>
              </q-form>
            </q-tab-panel>
          </q-tab-panels>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn color="primary" label="Cancel" @click="onHide" />
          <q-btn
            v-if="tab > 1"
            color="primary"
            label="Back"
            @click="tab = '1'"
          />
          <q-btn
            color="primary"
            :label="tab == 2 ? 'Submit' : 'Next'"
            @click="onSubmit"
          />
        </q-card-actions>
      </q-card>
    </div>
  </q-dialog>
</template>

<script lang="ts">
import { useDialogPluginComponent, useQuasar } from 'quasar';
import { defineComponent, ref, onMounted } from 'vue';
import { AccountService } from 'src/services/AccountService';
import { ProviderService } from 'src/services/ProviderService';
import { CreateAccount } from 'src/models/CreateAccount';
import { Iaas } from 'src/models/Iaas';

export default defineComponent({
  emits: [...useDialogPluginComponent.emits],

  setup() {
    const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } =
      useDialogPluginComponent();

    const $q = useQuasar();
    const account = ref<CreateAccount>({
      name: '',
      iaas: '',
      data: <Record<string, string>>{},
    });
    const iaasOptions = ref<Iaas[]>();
    const iaas = ref();
    const tab = ref('1');
    const pwd = ref<[boolean]>();
    const gen = ref();
    const sec = ref();

    onMounted(() => {
      ProviderService.getProviders()
        .then(({ results }) => {
          iaasOptions.value = results;
        })
        .catch((err) => {
          $q.notify({
            color: 'negative',
            message: err.body?.detail || err.message,
          });
        });
    });

    return {
      dialogRef,
      account,
      iaasOptions,
      pwd,
      gen,
      sec,
      iaas,
      tab,

      onHide() {
        onDialogHide();
      },

      async onSubmit() {
        if (!(await gen.value.validate())) {
          tab.value = '1';
        } else if (tab.value == '2' && !(await sec.value.validate())) {
          tab.value = '2';
        } else {
          if (tab.value == '1') {
            tab.value = '2';
          } else {
            account.value.iaas = iaas.value.name;
            AccountService.createAccount({ ...account.value })
              .then(() => {
                $q.notify({
                  message: 'Account created successfully',
                  color: 'positive',
                });
                onDialogOK();
              })
              .catch((err: any) => {
                $q.notify({
                  message: err.body?.detail || err.message,
                  color: 'negative',
                });
              });
          }
        }
      },

      onCancel() {
        onDialogCancel();
      },
    };
  },
});
</script>
