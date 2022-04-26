<template>
  <div class="col">
    <div class="row">
      <q-select
        class="q-pb-md q-px-md"
        style="width: 12.5vw"
        v-model="template"
        label="Template"
        dense
        flat
        :options="templates"
        map-options
        option-label="name"
        @update:model-value="showTemplate()"
      >
        <template v-slot:option="scope">
          <q-item v-bind="scope.itemProps">
            <q-item-section>
              <q-item-label>{{ scope.opt.name }}</q-item-label>
              <q-item-label caption>{{ scope.opt.description }}</q-item-label>
            </q-item-section>
          </q-item>
        </template>
      </q-select>
      <q-btn
        icon="save"
        label="Save"
        @click="saveTemplate()"
        :disabled="!template"
        flat
        dense
      />
      <q-btn
        icon="delete"
        label="Delete"
        @click="deleteTemplate()"
        :disabled="!template"
        flat
        dense
      />
      <q-btn icon="add" label="Add" @click="addTemplate()" flat dense />
    </div>
    <div class="row full-width">
      <div class="col q-px-sm">
        <q-table
          class="template-table"
          row-key="id"
          binary-state-sort
          virtual-scroll
          :virtual-scroll-sticky-size-start="48"
          :rows="included_accounts"
          :columns="columns"
          :loading="loading"
          title="Included"
          v-model:pagination="pagination"
          :rows-per-page-options="[0]"
        >
          <template #body-cell-drag-handle="props">
            <q-td :props="props">
              <q-btn icon="arrow_upward" flat dense @click="moveUp(props.row)">
                <q-tooltip> Move Up </q-tooltip>
              </q-btn>
              <q-btn
                icon="arrow_downward"
                flat
                dense
                @click="moveDown(props.row)"
              >
                <q-tooltip> Move Down </q-tooltip>
              </q-btn>
              <q-btn icon="close" flat dense @click="exclude(props.row)">
                <q-tooltip> Exclude </q-tooltip>
              </q-btn>
            </q-td>
          </template>

          <template v-slot:body-cell-iaas="props">
            <q-td :props="props">
              {{
                props.row.data.endpoint
                  ? props.row.iaas.name.concat(
                      ' (',
                      props.row.data.endpoint,
                      ')'
                    )
                  : props.row.iaas.name
              }}
            </q-td>
          </template>
        </q-table>
      </div>
      <div class="col q-px-sm">
        <q-table
          class="template-table"
          row-key="id"
          binary-state-sort
          virtual-scroll
          :virtual-scroll-sticky-size-start="48"
          :rows="excluded_accounts"
          :columns="columns"
          :loading="loading"
          title="Excluded"
          v-model:pagination="pagination"
          :rows-per-page-options="[0]"
        >
          <template #body-cell-drag-handle="props">
            <q-td :props="props">
              <q-btn icon="add" flat dense @click="include(props.row)">
                <q-tooltip> Include </q-tooltip>
              </q-btn>
            </q-td>
          </template>

          <template v-slot:body-cell-iaas="props">
            <q-td :props="props">
              {{
                props.row.data.endpoint
                  ? props.row.iaas.name.concat(
                      ' (',
                      props.row.data.endpoint,
                      ')'
                    )
                  : props.row.iaas.name
              }}
            </q-td>
          </template>
        </q-table>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.template-table {
  height: calc(100vh - 240px);

  .q-table__top,
  .q-table__bottom,
  thead tr:first-child th {
    background-color: #f5f5f5;
  }

  thead tr th {
    position: sticky;
    z-index: 1;
  }

  thead tr:last-child th {
    top: 48px;
  }
  thead tr:first-child th {
    top: 0;
  }
}
</style>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';

import { useQuasar } from 'quasar';
import { AccountService } from 'src/services/AccountService';
import { Account } from 'src/models/Account';
import { Template } from 'src/models/Template';
import { TemplateService } from 'src/services/TemplateService';
import NewTemplateDialog from './dialogs/NewTemplateDialog.vue';

const columns = [
  {
    name: 'drag-handle',
    align: 'left',
  },
  {
    name: 'iaas',
    required: true,
    label: 'Provider',
    align: 'left',
    sortable: false,
    field: (row: any) => row.iaas.name,
  },
  {
    name: 'name',
    required: true,
    label: 'Name',
    align: 'left',
    sortable: false,
    field: 'name',
  },
];

export default defineComponent({
  name: 'TemplateTable',

  setup() {
    const $q = useQuasar();

    const templates = ref<Template[]>([]);
    const loading = ref(false);
    const template = ref<Template>();
    var accounts = Array<Account>();
    const included_accounts = ref<Account[]>([]);
    const excluded_accounts = ref<Account[]>([]);

    const showTemplate = () => {
      if (template.value) {
        // Map shown templates to accounts
        included_accounts.value = template.value.order.map((id) => {
          return accounts.find((account) => account.id === id)!;
        });
        excluded_accounts.value = accounts.filter(
          (account) => account.id && !template.value?.order.includes(account.id)
        );
      }
    };

    const loadTemplates = async (toShow?: Template) => {
      loading.value = true;
      AccountService.getAccounts().then((resp) => {
        accounts = resp.results;
        TemplateService.getTemplates(true).then((resp) => {
          templates.value = resp;
          if (templates.value.length > 0) {
            template.value = toShow || templates.value[0];
            showTemplate();
          }
          loading.value = false;
          return Promise.resolve();
        });
      });
    };

    onMounted(() => {
      loadTemplates();
    });

    return {
      columns,
      templates,
      loading,
      template,
      included_accounts,
      excluded_accounts,

      pagination: ref({
        rowsPerPage: 0,
      }),

      showTemplate,

      moveUp(account: Account) {
        const index = included_accounts.value.indexOf(account);
        if (index > 0) {
          included_accounts.value.splice(index, 1);
          included_accounts.value.splice(index - 1, 0, account);
        }
      },

      moveDown(account: Account) {
        const index = included_accounts.value.indexOf(account);
        if (index < included_accounts.value.length - 1) {
          included_accounts.value.splice(index, 1);
          included_accounts.value.splice(index + 1, 0, account);
        }
      },

      include(account: Account) {
        included_accounts.value.push(account);
        excluded_accounts.value = excluded_accounts.value.filter(
          (val) => val.id != account.id
        );
      },

      exclude(account: Account) {
        excluded_accounts.value.push(account);
        included_accounts.value = included_accounts.value.filter(
          (val) => val.id != account.id
        );
      },

      saveTemplate() {
        if (!template.value) {
          return;
        }
        const order = included_accounts.value.map((account) => account.id!);
        TemplateService.updateTemplate(template.value.id, {
          order,
        })
          .then((resp) => {
            $q.notify({
              message: 'Template saved',
              color: 'positive',
            });
            loadTemplates(resp);
          })
          .catch((err: any) => {
            $q.notify({
              message: err.body?.detail || err.message,
              color: 'negative',
            });
          });
      },

      deleteTemplate() {
        if (!template.value) {
          return;
        }
        const { id, name } = template.value;
        $q.dialog({
          title: 'Delete Template',
          message: `Are you sure you want to delete ${name}?`,
          color: 'negative',
        }).onOk(() => {
          TemplateService.deleteTemplate(id)
            .then(() => {
              loadTemplates();
              $q.notify({
                message: 'Template Deleted',
                color: 'positive',
              });
            })
            .catch((err: any) => {
              $q.notify({
                message: err.body?.detail || err.message,
                color: 'negative',
              });
            });
        });
      },

      addTemplate() {
        $q.dialog({
          title: 'New Template',
          component: NewTemplateDialog,
        }).onOk((resp: Template) => {
          loadTemplates(resp);
        });
      },
    };
  },
});
</script>
