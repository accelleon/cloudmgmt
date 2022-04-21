<template>
  <q-page>
    <div class="q-pa-xl">
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
            {{ num_to_cur(props.row.total, props.row.account.currency) }}
          </q-td>
        </template>

        <template v-slot:body-cell-balance="props">
          <q-td :props="props">
            {{ num_to_cur(props.row.balance, props.row.account.currency) }}
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
    </div>
  </q-page>
</template>

<style lang="scss">
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
  name: 'BillingPage',

  setup() {
    const $q = useQuasar();

    const bills = ref<BillingPeriod[]>();
    const iaas = ref<string[]>();
    const acct = ref<Account[]>();
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

      loading.value = true;

      return BillingService.getBilling(
        filterBy.value.iaas ? filter.value.iaas : undefined,
        filterBy.value.acct ? filter.value.acct : undefined,
        undefined,
        undefined,
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
      onRequest({ pagination: pagination.value });
    });

    const onSearch = () => {
      onRequest({ pagination: pagination.value });
    };

    const downloadSheet = () => {
      // TODO: modify BillingService to use blob
      axios({
        method: 'GET',
        url: 'http://172.50.1.69:8000/api/v1/billing/export',
        responseType: 'blob',
        headers: {
          Authorization: `Bearer ${useAuthStore().token}`,
        },
      }).then((resp) => {
        const blob = new Blob([resp.data], {
          type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.setAttribute('download', 'billing.xlsx');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      });
    };

    return {
      columns,
      bills,
      iaas,
      acct,
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
