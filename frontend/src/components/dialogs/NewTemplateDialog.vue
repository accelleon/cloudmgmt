<template>
  <q-dialog ref="dialogRef" @hide="onHide">
    <div class="row window-width">
      <q-card class="q-dialog-plugin">
        <q-card-section>
          <div class="text-h5">Add Template</div>
        </q-card-section>

        <q-separator />

        <q-card-section>
          <q-form ref="tempForm" @keyup.enter="onSubmit">
            <q-input
              class="full-width q-py-md"
              square
              filled
              v-model="template.name"
              label="Template Name"
              autofocus
              lazy-rules
              :rules="[(val: string) => (val && val.length) || 'Name is required']"
            />
            <q-input
              class="full-width q-py-md"
              square
              filled
              v-model="template.description"
              label="Description"
              lazy-rules
              :rules="[(val: string) => (val && val.length) || 'Description is required']"
            />
          </q-form>
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
import { defineComponent, ref } from 'vue';
import { TemplateService } from 'src/services/TemplateService';
import { CreateTemplate } from 'src/models/CreateTemplate';

export default defineComponent({
  emits: [...useDialogPluginComponent.emits],

  setup() {
    const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } =
      useDialogPluginComponent();

    const $q = useQuasar();
    const template = ref<CreateTemplate>({
      name: '',
      description: '',
      order: [],
    });

    const tempForm = ref();

    return {
      dialogRef,
      onDialogHide,
      onDialogOK,
      onDialogCancel,
      template,
      tempForm,

      onSubmit() {
        if (tempForm.value.validate()) {
          TemplateService.createTemplate(template.value)
            .then((resp) => {
              onDialogOK(resp);
            })
            .catch((err) => {
              $q.notify({
                color: 'negative',
                message: err.body?.detail || err.message,
              });
            });
        }
      },

      onHide() {
        onDialogHide();
      },

      onCancel() {
        onDialogCancel();
      },
    };
  },
});
</script>
