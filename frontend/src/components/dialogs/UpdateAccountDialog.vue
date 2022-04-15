<template>
  <q-dialog ref="dialogRef" @hide="onHide">
    <div class="row window-width">
      <q-card class="q-dialog-plugin">
        <q-card-section>
          <div class="text-h5">Edit Account</div>
        </q-card-section>

        <q-separator />

        <q-card-section>
          <q-tabs v-model="tab">
            <q-tab name="1" label="General" />
            <q-tab name="2" label="Security" />
          </q-tabs>

          <q-tab-panels
            class="q-py-md"
            v-model="tab"
            animated
            swipeable
            keep-alive
          >
            <q-tab-panel name="1">
              <q-form ref="gen">
                <q-select
                  class="full-width"
                  square
                  filled
                  readonly
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
                />
              </q-form>
            </q-tab-panel>
            <q-tab-panel name="2">
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
                      :readonly="param.readonly"
                    />
                    <q-select
                      v-if="param.type === 'choice'"
                      v-model="account.data[param.key]"
                      class="full-width q-py-md"
                      filled
                      square
                      :label="param.label"
                      :options="param.choices"
                      :readonly="param.readonly"
                    />
                  </div>
                </div>
              </q-form>
            </q-tab-panel>
          </q-tab-panels>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn color="primary" label="Cancel" @click="onHide" />
          <q-btn color="primary" label="Submit" @click="onSubmit" />
        </q-card-actions>
      </q-card>
    </div>
  </q-dialog>
</template>

<script lang="ts">
import { useDialogPluginComponent, useQuasar } from 'quasar';
import { defineComponent, ref, onMounted, computed, PropType } from 'vue';
import _ from 'lodash';
import { Account } from 'src/models/Account';
import { AccountService } from 'src/services/AccountService';
import { ProviderService } from 'src/services/ProviderService';
import { UpdateAccount } from 'src/models/UpdateAccount';
import { Iaas } from 'src/models/Iaas';

export default defineComponent({
  emits: [...useDialogPluginComponent.emits],

  props: {
    old: {
      type: Object as PropType<Account>,
      required: true,
    },
  },

  setup(props) {
    const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } =
      useDialogPluginComponent();

    const $q = useQuasar();
    const account = ref<UpdateAccount>();
    const iaas = ref();
    const tab = ref('1');
    const gen = ref();
    const sec = ref();

    onMounted(() => {
      iaas.value = props.old.iaas;
      account.value = {
        name: props.old.name,
        data: { ...props.old.data },
      };
    });

    return {
      dialogRef,
      account,
      gen,
      sec,
      iaas,
      tab,

      onHide() {
        onDialogHide();
      },

      async onSubmit() {
        if (
          _.isEqual(account.value, {
            name: props.old.name,
            data: props.old.data,
          })
        ) {
          $q.notify({
            message: 'No changes made',
            color: 'positive',
          });
          onDialogCancel();
          return;
        }
        if (await gen.value.validate()) {
          if (sec.value) {
            if (!(await sec.value.validate())) {
              return;
            }
          }
          AccountService.updateAccount(props.old.id!, { ...account.value })
            .then(() => {
              $q.notify({
                message: 'Account updated successfully',
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
      },

      onCancel() {
        onDialogCancel();
      },
    };
  },
});
</script>
