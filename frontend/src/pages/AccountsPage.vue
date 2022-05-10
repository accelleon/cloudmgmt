<template>
  <q-page>
    <div class="q-pa-xl">
      <q-table
        class="acct-table"
        row-key="id"
        binary-state-sort
        virtual-scroll
        :virtual-scroll-sticky-size-start="48"
        v-model:pagination="pagination"
        :rows="accts"
        :columns="columns"
        :loading="loading"
        @request="onRequest"
      >
        <template v-slot:top-left>
          <div class="row">
            <q-input
              style="width: 25vw"
              v-model="filter.name"
              clearable
              dense
              flat
              hide-underline
              placeholder="Search"
              debounce="500"
              type="search"
              @update:model-value="onSearch"
            >
              <template v-slot:prepend>
                <q-icon name="search" />
              </template>
            </q-input>
            <q-btn-dropdown dropdown-icon="filter_list" flat>
              <q-list>
                <q-item>
                  <q-item-section avatar>
                    <q-toggle
                      v-model="filterBy.iaas"
                      flat
                      dense
                      @update:model-value="onSearch"
                    />
                  </q-item-section>
                  <q-item-section>Provider</q-item-section>
                  <q-item-section side>
                    <q-select
                      style="min-width: 100px"
                      v-model="filter.iaas"
                      flat
                      dense
                      :options="iaas"
                      @update:model-value="onSearch(null)"
                    />
                  </q-item-section>
                </q-item>
              </q-list>
            </q-btn-dropdown>
          </div>
        </template>

        <template v-slot:body-cell-iaas="props">
          <q-td :props="props">
            {{
              props.row.data.endpoint
                ? props.row.iaas.name.concat(' (', props.row.data.endpoint, ')')
                : props.row.iaas.name
            }}
          </q-td>
        </template>

        <template v-slot:body-cell-validated="props">
          <q-td :props="props">
            <q-icon
              size="md"
              :name="props.row.validated ? 'check_circle' : 'cancel'"
              :color="props.row.validated ? 'green' : 'red'"
            >
              <q-tooltip v-if="!props.row.validated">
                {{
                  props.row.last_error ? props.row.last_error : 'Not validated'
                }}
              </q-tooltip>
            </q-icon>
          </q-td>
        </template>

        <template v-slot:top-right>
          <q-btn icon="add" @click="onAdd">
            <q-tooltip> Add Account </q-tooltip>
          </q-btn>
        </template>

        <template v-slot:body-cell-action="props">
          <q-td :props="props">
            <q-btn-dropdown dropdown-icon="more_vert" flat auto-close>
              <q-list>
                <q-item clickable @click="onValidate(props.row)">
                  <q-item-section>Validate</q-item-section>
                </q-item>
                <q-item clickable @click="onEdit(props.row)">
                  <q-item-section avatar>
                    <q-icon name="edit" size="xs" />
                  </q-item-section>
                  <q-item-section>Edit</q-item-section>
                </q-item>
                <q-item clickable @click="onDelete(props.row)">
                  <q-item-section avatar>
                    <q-icon name="delete" size="xs" />
                  </q-item-section>
                  <q-item-section>Delete</q-item-section>
                </q-item>
              </q-list>
            </q-btn-dropdown>
          </q-td>
        </template>
      </q-table>
    </div>
  </q-page>
</template>

<style lang="scss" scoped>
.acct-table {
  height: calc(100vh - 160px);

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
import { defineComponent, ref, onMounted, PropType } from 'vue';
import { useQuasar } from 'quasar';
import { AccountService } from '..';
import { ProviderService } from '..';
import { Account } from '../models/Account';
import { Iaas } from '../models/Iaas';
import { SearchOrder } from '../models/SearchOrder';
import NewAccountDialog from 'src/components/dialogs/NewAccountDialog.vue';
import UpdateAccountDialog from 'src/components/dialogs/UpdateAccountDialog.vue';
import { IaasType } from 'src/models/IaasType';

const columns = [
  {
    name: 'iaas',
    required: true,
    label: 'Provider',
    align: 'left',
    sortable: true,
    field: (row: any) => row.iaas.name,
  },
  {
    name: 'name',
    required: true,
    label: 'Name',
    align: 'left',
    sortable: true,
    field: 'name',
  },
  {
    name: 'validated',
    required: true,
    label: 'Validated',
    align: 'center',
    sortable: true,
    field: (row: any) => row.data.validated,
  },
  {
    name: 'action',
    label: '',
    align: 'right',
    sortable: false,
    field: 'action',
  },
];

interface Filter {
  name?: string;
  iaas?: string;
  type?: IaasType;
}

export default defineComponent({
  name: 'AccountsPage',

  setup() {
    const $q = useQuasar();

    const accts = ref<Account[]>();
    const iaas = ref<string[]>();
    const filter = ref({
      name: '',
      iaas: '',
      type: undefined,
    } as Filter);
    const filterBy = ref({
      iaas: false,
      type: false,
    });
    const loading = ref(false);
    const pagination = ref({
      sortBy: 'name',
      descending: false,
      page: 1,
      rowsPerPage: 20,
      rowsNumber: 20,
    });

    const onRequest = (props: any) => {
      const { page, rowsPerPage, sortBy, descending } = props.pagination;

      loading.value = true;

      return AccountService.getAccounts(
        filter.value.name,
        filterBy.value.iaas ? filter.value.iaas : undefined,
        filterBy.value.type ? filter.value.type : undefined,
        page - 1,
        rowsPerPage,
        sortBy,
        descending ? SearchOrder.DESC : SearchOrder.ASC
      )
        .then(({ results, total }) => {
          iaas.value = [...new Set(results.map((a) => a.iaas.name))];
          pagination.value.rowsNumber = total;
          pagination.value.page = page;
          pagination.value.rowsPerPage = rowsPerPage;
          pagination.value.sortBy = sortBy;
          pagination.value.descending = descending;
          accts.value = results;
        })
        .catch((err) => {
          $q.notify({
            color: 'negative',
            textColor: 'white',
            message: err.body?.detail || err.message,
          });
        })
        .finally(() => {
          loading.value = false;
        });
    };

    onMounted(() => {
      onRequest({ pagination: pagination.value });
    });

    const onDelete = (props: any) => {
      const { id, name } = props;
      $q.dialog({
        title: 'Delete Account',
        message: `Are you sure you want to delete ${name}?`,
        color: 'negative',
      }).onOk(() => {
        loading.value = true;
        AccountService.deleteAccount(id)
          .then(() => {
            loading.value = false;
            $q.notify({
              color: 'positive',
              textColor: 'white',
              message: `${name} deleted`,
            });
            onRequest({ pagination: pagination.value });
          })
          .catch((err) => {
            loading.value = false;
            $q.notify({
              color: 'negative',
              textColor: 'white',
              message: err.body?.detail || err.message,
            });
          });
      });
    };

    const onValidate = (props: any) => {
      const { id, name } = props;
      loading.value = true;
      AccountService.validateAccount(id).then((account) => {
        onRequest({ pagination: pagination.value });
        loading.value = false;
        if (account.validated) {
          $q.notify({
            color: 'positive',
            textColor: 'white',
            message: `${name} validated`,
          });
        } else {
          $q.notify({
            color: 'negative',
            textColor: 'white',
            message: `${name} not validated`,
          });
        }
      });
    };

    const onEdit = (props: any) => {
      $q.dialog({
        title: 'Edit Account',
        component: UpdateAccountDialog,
        componentProps: {
          old: { ...props },
        },
      }).onOk(() => {
        onRequest({
          pagination: pagination.value,
        });
      });
    };

    const onAdd = () => {
      $q.dialog({
        title: 'New Account',
        component: NewAccountDialog,
      }).onOk((acct: Account) => {
        onRequest({ pagination: pagination.value });
      });
    };

    const onSearch = (value: any) => {
      if (value === 'string' || value === 'null') filter.value.name = value;
      onRequest({ pagination: pagination.value });
    };

    return {
      accts,
      columns,
      filter,
      filterBy,
      loading,
      iaas,
      pagination,
      onRequest,
      onDelete,
      onEdit,
      onAdd,
      onSearch,
      onValidate,
    };
  },
});
</script>
