<template>
  <q-page>
    <div class="q-pa-xl">
      <q-table
        class="user-table"
        row-key="id"
        binary-state-sort
        virtual-scroll
        :virtual-scroll-sticky-size-start="48"
        v-model:pagination="pagination"
        :rows="users"
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
            <q-btn-dropdown
              dropdown-icon="filter_list"
              flat
              auto-close
              @hide="onSearch"
            >
              <q-list>
                <q-item>
                  <q-item-section avatar>
                    <q-toggle
                      v-model="filterBy.is_admin"
                      flat
                      dense
                      @update:model-value="onSearch"
                    />
                  </q-item-section>
                  <q-item-section>Administrator</q-item-section>
                  <q-item-section side>
                    <q-checkbox
                      v-model="filter.is_admin"
                      flat
                      dense
                      @update:model-value="onSearch"
                    />
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section avatar>
                    <q-toggle
                      v-model="filterBy.twofa_enabled"
                      flat
                      dense
                      @update:model-value="onSearch"
                    />
                  </q-item-section>
                  <q-item-section>2FA</q-item-section>
                  <q-item-section side>
                    <q-checkbox
                      v-model="filter.twofa_enabled"
                      flat
                      dense
                      @update:model-value="onSearch"
                    />
                  </q-item-section>
                </q-item>
              </q-list>
            </q-btn-dropdown>
          </div>
        </template>

        <template v-slot:top-right>
          <q-btn icon="add" @click="onAdd">
            <q-tooltip> Add User </q-tooltip>
          </q-btn>
        </template>

        <template v-slot:body-cell-is_admin="props">
          <q-td :props="props">
            <q-icon
              size="md"
              :name="props.row.is_admin ? 'check_circle' : 'cancel'"
              :color="props.row.is_admin ? 'green' : 'red'"
            />
          </q-td>
        </template>

        <template v-slot:body-cell-twofa_enabled="props">
          <q-td :props="props">
            <q-icon
              size="md"
              :name="props.row.twofa_enabled ? 'check_circle' : 'cancel'"
              :color="props.row.twofa_enabled ? 'green' : 'red'"
            />
          </q-td>
        </template>

        <template v-slot:body-cell-action="props">
          <q-td :props="props">
            <q-btn-dropdown dropdown-icon="more_vert" flat auto-close>
              <q-list>
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

<style lang="scss">
.user-table {
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
import { defineComponent, ref } from 'vue';
import { onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { UserService } from '..';
import UpdateUserDialog from 'src/components/dialogs/UpdateUserDialog.vue';
import NewUserDialog from 'src/components/dialogs/NewUserDialog.vue';
import { SearchOrder } from 'src/models/SearchOrder';
import { User } from 'src/models/User';

const columns = [
  {
    name: 'username',
    required: true,
    label: 'Username',
    align: 'left',
    field: 'username',
    sortable: true,
  },
  {
    name: 'first_name',
    required: true,
    label: 'First Name',
    align: 'left',
    field: 'first_name',
    sortable: true,
  },
  {
    name: 'last_name',
    required: true,
    label: 'Last Name',
    align: 'left',
    field: 'last_name',
    sortable: true,
  },
  {
    name: 'is_admin',
    label: 'Admin',
    align: 'center',
    field: 'is_admin',
    sortable: true,
  },
  {
    name: 'twofa_enabled',
    label: 'Two-Factor Auth',
    align: 'center',
    field: 'twofa_enabled',
    sortable: true,
  },
  {
    name: 'action',
    align: 'center',
    field: 'action',
    sortable: false,
  },
];

interface Filter {
  name?: string;
  is_admin: boolean;
  twofa_enabled: boolean;
}

export default defineComponent({
  name: 'UsersPage',

  setup() {
    const $q = useQuasar();

    const users = ref<User[]>();
    const filter = ref({
      name: '',
      is_admin: false,
      twofa_enabled: false,
    } as Filter);
    const filterBy = ref({
      is_admin: false,
      twofa_enabled: false,
    });
    const loading = ref(false);
    const pagination = ref({
      sortBy: 'username',
      descending: false,
      page: 1,
      rowsPerPage: 20,
      rowsNumber: 20,
    });

    const onRequest = (props: any) => {
      const { page, rowsPerPage, sortBy, descending } = props.pagination;

      loading.value = true;
      UserService.getUsers(
        filter.value.name,
        undefined,
        undefined,
        filterBy.value.is_admin ? filter.value.is_admin : undefined,
        filterBy.value.twofa_enabled ? filter.value.twofa_enabled : undefined,
        page - 1,
        rowsPerPage,
        sortBy,
        descending ? SearchOrder.DESC : SearchOrder.ASC
      )
        .then(({ results, total }) => {
          pagination.value.rowsNumber = total;
          pagination.value.page = page;
          pagination.value.rowsPerPage = rowsPerPage;
          pagination.value.sortBy = sortBy;
          pagination.value.descending = descending;
          loading.value = false;
          users.value = results;
          return Promise.resolve();
        })
        .catch((err) => {
          loading.value = false;
          $q.notify({
            color: 'negative',
            message: err.message?.body || err.message,
          });
          return Promise.reject(err);
        });
    };

    onMounted(() => {
      onRequest({
        pagination: pagination.value,
      });
    });

    const onDelete = async (props: any) => {
      const { id, username } = props;
      $q.dialog({
        title: 'Delete User',
        message: `Are you sure you want to delete user ${username}?`,
        color: 'negative',
      }).onOk(() => {
        loading.value = true;
        UserService.deleteUser(id)
          .then(() => {
            $q.notify({
              color: 'positive',
              message: `User ${username} deleted`,
            });
            onRequest({
              pagination: pagination.value,
            });
          })
          .catch((err) => {
            $q.notify({
              color: 'negative',
              message: err.message?.body || err.message,
            });
          });
      });
    };

    const onEdit = async (props: any) => {
      const user = { ...props };
      $q.dialog({
        title: 'Update User',
        component: UpdateUserDialog,
        componentProps: {
          user,
        },
      }).onOk(async (user) => {
        onRequest({
          pagination: pagination.value,
        });
      });
    };

    const onAdd = async () => {
      $q.dialog({
        component: NewUserDialog,
      }).onOk(() => {
        onRequest({
          pagination: pagination.value,
        });
      });
    };

    const onSearch = (value: any) => {
      if (value === 'string' || value === 'null') filter.value.name = value;
      onRequest({
        pagination: pagination.value,
      });
    };

    return {
      users,
      columns,
      loading,
      pagination,
      filter,
      filterBy,
      onRequest,
      onDelete,
      onEdit,
      onAdd,
      onSearch,
    };
  },
});
</script>
