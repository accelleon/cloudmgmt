<template>
  <q-page>
    <q-tabs class="q-pa-sm" v-model="tab">
      <q-tab name="billing" label="Billing" />
      <q-tab name="templates" label="Templates" />
    </q-tabs>
    <q-tab-panels v-model="tab" animated swipeable>
      <q-tab-panel name="billing">
        <billing-table />
      </q-tab-panel>
      <q-tab-panel name="templates">
        <template-table />
      </q-tab-panel>
    </q-tab-panels>
  </q-page>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import BillingTable from 'src/components/BillingTable.vue';
import TemplateTable from 'src/components/TemplateTable.vue';

export default defineComponent({
  name: 'BillingPage',
  components: { BillingTable, TemplateTable },

  setup() {
    return {
      tab: ref('billing'),
    };
  },
});
</script>
