<template>
  <q-table
    class="billing-table"
    row-key="id"
    binary-state-sort
    virtual-scroll
    :virtual-scroll-sticky-size-start="48"
    v-model:pagination="pagination"
    :rows="bills"
    :columns="columns"
    :loading="loading"
    @request="onRequest"
  >
    <template v-slot:top-left>
      <div class="row">
        <q-select
          style="width: 12.5vw"
          v-model="period"
          label="Billing Period"
          dense
          flat
          :options="periods"
          @update:model-value="onSearch()"
        />
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
                  @update:model-value="onSearch()"
                />
              </q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>
      </div>
    </template>

    <template v-slot:top-right>
      <q-btn icon="file_download" @click="downloadSheet">
        <q-tooltip> Export to Excel </q-tooltip>
      </q-btn>
    </template>

    <template v-slot:body-cell-start_date="props">
      <q-td :props="props">
        {{ utc_to_local(props.row.start_date) }}
      </q-td>
    </template>

    <template v-slot:body-cell-end_date="props">
      <q-td :props="props">
        {{ utc_to_local(props.row.end_date) }}
      </q-td>
    </template>

    <template v-slot:body-cell-total="props">
      <q-td :props="props">
        {{
          props.row.total != null
            ? num_to_cur(props.row.total, props.row.account.currency)
            : '-'
        }}
      </q-td>
    </template>

    <template v-slot:body-cell-balance="props">
      <q-td :props="props">
        {{
          props.row.balance != null
            ? num_to_cur(props.row.balance, props.row.account.currency)
            : '-'
        }}
      </q-td>
    </template>

    <template v-slot:body-cell-iaas="props">
      <q-td :props="props">
        {{
          props.row.account.data.endpoint
            ? props.row.account.iaas.name.concat(
                ' (',
                props.row.account.data.endpoint,
                ')'
              )
            : props.row.account.iaas.name
        }}
      </q-td>
    </template>
  </q-table>
</template>

<style lang="scss" scoped>
.billing-table {
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
import { defineComponent, ref, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { BillingService } from 'src/services/BillingService';
import { BillingPeriod } from 'src/models/BillingPeriod';
import { SearchOrder } from 'src/models/SearchOrder';
import { Account } from 'src/models/Account';
import axios from 'axios';
import { useAuthStore } from 'src/stores/auth-store';
import SelectTemplateDialogVue from './dialogs/SelectTemplateDialog.vue';

const columns = [
  {
    name: 'iaas',
    required: true,
    label: 'Provider',
    align: 'left',
    sortable: true,
    field: (row: any) => row.account.iaas.name,
  },
  {
    name: 'account',
    required: true,
    label: 'Account',
    align: 'left',
    sortable: true,
    field: (row: any) => row.account.name,
  },
  {
    name: 'start_date',
    required: true,
    label: 'Start Date',
    align: 'left',
    sortable: true,
    field: 'start_date',
  },
  {
    name: 'end_date',
    required: true,
    label: 'End Date',
    align: 'left',
    sortable: true,
    field: 'end_date',
  },
  {
    name: 'total',
    required: true,
    label: 'Total',
    align: 'right',
    sortable: true,
    field: 'total',
  },
  {
    name: 'balance',
    required: false,
    label: 'Balance',
    align: 'right',
    sortable: true,
    field: 'balance',
  },
];

interface Filter {
  acct?: string;
  iaas?: string;
}

function utc_to_local(utc_datetime: string) {
  // remove milliseconds
  utc_datetime = utc_datetime.replace(/\.\d+Z/, 'Z');

  // convert to date
  const datetime = new Date(utc_datetime);

  // convert to local datetime
  const local_datetime = new Date(
    datetime.getTime() + datetime.getTimezoneOffset() * 60000
  );

  // format local datetime
  return local_datetime.toISOString().slice(0, 10);
}

function num_to_cur(num: number, currency: string) {
  return num.toLocaleString('en-US', {
    style: 'currency',
    currency,
  });
}

export default defineComponent({
  name: 'BillingTable',

  setup() {
    const $q = useQuasar();

    const bills = ref<BillingPeriod[]>();
    const iaas = ref<string[]>();
    const acct = ref<Account[]>();
    const periods = ref<string[]>();
    const period = ref<string>();
    const filter = ref({
      acct: '',
      iaas: '',
    } as Filter);
    const filterBy = ref({
      acct: false,
      iaas: false,
    });
    const loading = ref(false);
    const pagination = ref({
      sortBy: 'name',
      descending: false,
      page: 1,
      rowsPerPage: 0,
      rowsNumber: 10,
    });

    const onRequest = (props: any) => {
      const { page, rowsPerPage, sortBy, descending } = props.pagination;

      if (!period.value) {
        return;
      }

      loading.value = true;
      return BillingService.getBilling(
        period.value,
        filterBy.value.iaas ? filter.value.iaas : undefined,
        filterBy.value.acct ? filter.value.acct : undefined,
        page - 1,
        rowsPerPage,
        sortBy,
        descending ? SearchOrder.DESC : SearchOrder.ASC
      )
        .then(({ results, total }) => {
          acct.value = [...new Set(results.map((b) => b.account))];
          iaas.value = [...new Set(results.map((a) => a.account.iaas.name))];
          pagination.value.rowsNumber = total;
          pagination.value.page = page;
          pagination.value.rowsPerPage = rowsPerPage;
          pagination.value.sortBy = sortBy;
          pagination.value.descending = descending;
          bills.value = results;
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
      BillingService.getPeriods().then((result) => {
        periods.value = result;
        if (periods.value.length > 0) {
          period.value = periods.value[0];
          onRequest({ pagination: pagination.value });
        }
      });
    });

    const onSearch = () => {
      onRequest({ pagination: pagination.value });
    };

    const downloadSheet = () => {
      $q.dialog({
        title: 'Select Template',
        component: SelectTemplateDialogVue,
      }).onOk((template) => {
        const notif = $q.notify({
          group: false, // Required to update later
          timeout: 0,
          spinner: true,
          message: 'Downloading...',
        });
        // TODO: modify BillingService to use blob
        axios({
          method: 'GET',
          url: '/api/v1/billing/export',
          responseType: 'blob',
          headers: {
            Authorization: `Bearer ${useAuthStore().token}`,
          },
          params: {
            template: template.name,
            period: period.value,
          },
        })
          .then((resp) => {
            const blob = new Blob([resp.data], {
              type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.setAttribute('download', 'billing.xlsx');
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            notif({
              icon: 'done',
              spinner: false,
              color: 'positive',
              message: 'Downloaded',
              timeout: 1000,
            });
          })
          .catch((resp) => {
            notif({
              icon: 'error',
              spinner: false,
              timeout: 2000,
              color: 'negative',
              message: resp.body?.detail || resp.message,
            });
          });
      });
    };

    return {
      columns,
      bills,
      iaas,
      acct,
      period,
      periods,
      filter,
      filterBy,
      loading,
      pagination,
      onRequest,
      onSearch,
      downloadSheet,
      utc_to_local,
      num_to_cur,
    };
  },
});
</script>
