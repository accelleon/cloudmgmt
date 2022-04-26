<template>
  <q-dialog ref="dialogRef" @hide="onHide">
    <div class="row window-width">
      <q-card class="q-dialog-plugin">
        <q-card-section>
          <div class="text-h5">Select Template</div>
        </q-card-section>

        <q-separator />

        <q-card-section>
          <q-select
            class="full-width q-py-md"
            ref="templateRef"
            square
            filled
            v-model="template"
            label="Template"
            option-label="name"
            map-options
            :options="templateOptions"
            lazy-rules
            :rules="[(val: any) => (val) || 'Template is required']"
          />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn color="primary" label="Cancel" @click="onHide" />
          <q-btn color="primary" label="Export" @click="onSubmit" />
        </q-card-actions>
      </q-card>
    </div>
  </q-dialog>
</template>

<script lang="ts">
import { useDialogPluginComponent, useQuasar } from 'quasar';
import { defineComponent, ref, onMounted } from 'vue';
import { TemplateService } from 'src/services/TemplateService';
import { Template } from 'src/models/Template';

export default defineComponent({
  emits: [...useDialogPluginComponent.emits],

  setup() {
    const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } =
      useDialogPluginComponent();

    const $q = useQuasar();

    const template = ref<Template>();
    const templateOptions = ref<Template[]>();
    const templateRef = ref();

    onMounted(() => {
      TemplateService.getTemplates()
        .then((templates) => {
          templateOptions.value = templates;
          template.value = templates.find((t) => t.name === 'default');
        })
        .catch((err) => {
          $q.notify({
            message: err.body?.detail || err.message,
            color: 'negative',
          });
          onDialogCancel();
        });
    });

    return {
      template,
      templateOptions,
      templateRef,
      dialogRef,

      onHide() {
        onDialogHide();
      },

      onSubmit() {
        if (templateRef.value.validate()) {
          onDialogOK(template.value);
        }
      },

      onCancel() {
        onDialogCancel();
      },
    };
  },
});
</script>
