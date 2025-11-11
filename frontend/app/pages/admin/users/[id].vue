<template>
  <div class="min-h-screen flex bg-gray-50 relative">
    <!-- Overlay for mobile -->
    <div
      v-if="sidebarOpen && !isDesktop"
      class="fixed inset-0 bg-black bg-opacity-40 z-30"
      @click="sidebarOpen = false"
    ></div>

    <!-- Sidebar -->
    <aside
      :class="[
        'bg-white shadow-sm z-40 transform transition-transform duration-300 ease-in-out fixed md:static md:translate-x-0',
        'h-screen md:h-auto w-64 flex flex-col justify-between p-6 md:min-h-screen',
        'rounded-none md:rounded-xl',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full',
      ]"
    >
      <div class="flex-1 flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-8">
            <h1 class="text-2xl font-bold text-gray-800">Admin</h1>
            <button
              v-if="!isDesktop"
              @click="sidebarOpen = false"
              class="text-gray-500 hover:text-gray-800 md:hidden"
            >
              <X class="w-5 h-5" />
            </button>
          </div>

          <!-- ADMIN NAV -->
          <nav class="space-y-3 flex-1">
            <SidebarItem label="Home" icon="Home" to="/admin" :collapsed="!isDesktop" />
            <SidebarItem label="User Management" icon="User" to="/admin/users" :collapsed="!isDesktop" />
            <SidebarItem label="Payments" icon="CreditCard" to="/admin/payments" :collapsed="!isDesktop" />
            <SidebarItem label="Transactions" icon="List" to="/admin/transactions" :collapsed="!isDesktop" />
            <SidebarItem label="Service Management" icon="List" to="/admin/services" :collapsed="!isDesktop" />
          </nav>
        </div>

        <button
          @click="logout"
          class="flex items-center gap-2 text-gray-500 hover:text-red-600 transition mt-8"
        >
          <LogOut class="w-5 h-5" />
          <span>Logout</span>
        </button>
      </div>
    </aside>

    <!-- Main content -->
    <main class="flex-1 flex flex-col p-4 md:p-8 w-full relative">
      <!-- Mobile Navbar -->
      <div class="flex items-center md:hidden mb-6 sticky top-0 bg-gray-50 z-20 px-2">
        <button @click="sidebarOpen = true" class="text-gray-700 hover:text-gray-900">
          <Menu class="w-6 h-6" />
        </button>
        <h2 class="ml-3 text-lg font-semibold">User #{{ id }}</h2>
      </div>

      <!-- Page header -->
      <div class="hidden md:flex justify-between items-center mb-8">
        <h2 class="text-2xl font-bold text-gray-800 capitalize">User #{{ id }}</h2>
        <div class="flex gap-2">
          <NuxtLink to="/admin/users" class="px-3 py-1 border rounded-xl">Back</NuxtLink>
          <button class="px-3 py-1 border rounded-xl" @click="toggleEdit">
            {{ isEditing ? 'Done' : 'Edit' }}
          </button>
        </div>
      </div>

      <!-- User Info -->
      <section class="rounded-2xl border bg-white mb-6">
        <div class="px-4 py-3 border-b font-medium">User Info</div>
        <div class="p-4 grid md:grid-cols-2 gap-4 text-sm">
          <FormRow label="Name">
            <template #default>
              <span v-if="!isEditing">{{ user?.name }}</span>
              <input v-else v-model="form.name" class="border rounded-xl px-3 py-2 w-full" />
            </template>
          </FormRow>
          <FormRow label="Phone">
            <template #default>
              <span v-if="!isEditing">{{ user?.phone }}</span>
              <input v-else v-model="form.phone" class="border rounded-xl px-3 py-2 w-full" />
            </template>
          </FormRow>
          <FormRow label="Role">
            <template #default>
              <span v-if="!isEditing"><RoleBadge :role="user?.role || 'user'" /></span>
              <select v-else v-model="form.role" class="border rounded-xl px-3 py-2 w-full">
                <option value="user">user</option>
                <option value="admin">admin</option>
              </select>
            </template>
          </FormRow>
          <FormRow label="Created At">{{ formatDate(user?.created_at) }}</FormRow>
        </div>
        <div v-if="isEditing" class="p-4 border-t flex justify-end gap-2">
          <button class="px-3 py-1 border rounded-xl" @click="cancelEdit">Cancel</button>
          <button class="px-3 py-1 border rounded-xl" :disabled="saving" @click="save">
            {{ saving ? 'Saving…' : 'Save' }}
          </button>
        </div>
      </section>

      <!-- Accounts -->
      <section class="rounded-2xl border bg-white mb-6">
        <div class="px-4 py-3 border-b font-medium">Accounts</div>
        <div class="overflow-x-auto p-4">
          <table class="min-w-full text-sm">
            <thead class="bg-gray-50">
              <tr>
                <th class="text-left p-3">Account Number</th>
                <th class="text-left p-3">Balance</th>
                <th class="text-left p-3">Currency</th>
                <th class="text-left p-3">Status</th>
                <th class="text-right p-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="a in accounts" :key="a.id || a.account_number" class="border-t">
                <td class="p-3">{{ a.account_number }}</td>
                <td class="p-3">{{ formatMoney(a.balance) }}</td>
                <td class="p-3">{{ a.currency }}</td>
                <td class="p-3">{{ a.status || 'active' }}</td>
                <td class="p-3 text-right">
                  <button
                    class="px-3 py-1 border rounded-xl"
                    @click="openBalanceDialog(a)"
                    :disabled="!a.id || editingBalance"
                    title="Edit Balance"
                  >
                    Edit Balance
                  </button>
                </td>
              </tr>
              <tr v-if="accounts.length===0">
                <td colspan="5" class="p-6 text-center text-gray-500">No accounts</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Transactions -->
      <section class="rounded-2xl border bg-white mb-6">
        <div class="px-4 py-3 border-b font-medium">Recent Transactions</div>
        <div class="overflow-x-auto p-4">
          <table class="min-w-full text-sm">
            <thead class="bg-gray-50">
              <tr>
                <th class="text-left p-3">ID</th>
                <th class="text-left p-3">Type</th>
                <th class="text-left p-3">Amount</th>
                <th class="text-left p-3">Currency</th>
                <th class="text-left p-3">Created</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="t in transactions" :key="t.id" class="border-t">
                <td class="p-3">{{ t.id }}</td>
                <td class="p-3">{{ t.type }}</td>
                <td class="p-3">{{ formatMoney(t.amount) }}</td>
                <td class="p-3">{{ t.currency }}</td>
                <td class="p-3">{{ formatDate(t.created_at) }}</td>
              </tr>
              <tr v-if="transactions.length===0">
                <td colspan="5" class="p-6 text-center text-gray-500">No transactions</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Payments -->
      <section class="rounded-2xl border bg-white">
        <div class="px-4 py-3 border-b font-medium">Payments</div>
        <div class="overflow-x-auto p-4">
          <table class="min-w-full text-sm">
            <thead class="bg-gray-50">
              <tr>
                <th class="text-left p-3">Payment ID</th>
                <th class="text-left p-3">Method</th>
                <th class="text-left p-3">Amount</th>
                <th class="text-left p-3">Currency</th>
                <th class="text-left p-3">Created</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in payments" :key="p.id" class="border-t">
                <td class="p-3">{{ p.id }}</td>
                <td class="p-3">{{ p.method || '—' }}</td>
                <td class="p-3">{{ formatMoney(p.amount) }}</td>
                <td class="p-3">{{ p.currency }}</td>
                <td class="p-3">{{ formatDate(p.created_at) }}</td>
              </tr>
              <tr v-if="payments.length===0">
                <td colspan="5" class="p-6 text-center text-gray-500">No payments</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </main>

    <!-- Edit Balance Dialog -->
    <dialog ref="balanceDlg" class="rounded-2xl p-0 w-[420px]">
      <form method="dialog" class="p-6 space-y-4">
        <h3 class="text-lg font-semibold">Edit Balance</h3>
        <div class="text-sm text-gray-600">
          Account: <b>{{ targetAccount?.account_number || '—' }}</b>
        </div>
        <div class="space-y-1">
          <label class="text-xs text-gray-500">New Balance</label>
          <input
            v-model="newBalance"
            type="number"
            step="0.01"
            class="border rounded-xl px-3 py-2 w-full"
            placeholder="0.00"
          />
        </div>
        <div class="flex justify-end gap-2">
          <button class="px-3 py-1 border rounded-xl">Cancel</button>
          <button
            class="px-3 py-1 border rounded-xl"
            @click.prevent="saveBalance"
            :disabled="editingBalance || !targetAccount?.id"
          >
            {{ editingBalance ? 'Saving…' : 'Save' }}
          </button>
        </div>
      </form>
    </dialog>
  </div>
</template>

<script setup lang="ts">
import SidebarItem from '~/components/SidebarItem.vue'
import { LogOut, Menu, X } from 'lucide-vue-next'
import { h, defineComponent } from 'vue'

type Role = 'user' | 'admin'
interface User { id: number; name?: string; phone: string; role: Role; created_at?: string }

const route = useRoute()
const id = computed(() => String(route.params.id))
const { $api } = useNuxtApp()
const { logout } = useAuth()

const isDesktop = ref(false)
const sidebarOpen = ref(false)

onMounted(() => {
  const updateScreen = () => { isDesktop.value = window.innerWidth >= 768 }
  updateScreen()
  window.addEventListener('resize', updateScreen)
})
onBeforeUnmount(() => window.removeEventListener('resize', () => {}))

const isEditing = ref(route.query.edit === '1')
function toggleEdit(){ isEditing.value = !isEditing.value }

const user = ref<User | null>(null)
const accounts = ref<any[]>([])
const transactions = ref<any[]>([])
const payments = ref<any[]>([])

async function loadAll() {
  try { user.value = await $api(`/admin/users/${id.value}`) } catch (e) { console.error(e) }
  try { accounts.value = await $api(`/admin/users/${id.value}/accounts`) } catch { accounts.value = [] }
  try { transactions.value = await $api(`/admin/users/${id.value}/transactions?limit=20`) } catch { transactions.value = [] }
  try { payments.value = await $api(`/admin/users/${id.value}/payments?limit=20`) } catch { payments.value = [] }
}
onMounted(loadAll)

const form = reactive({ name: '', phone: '', role: 'user' })
watchEffect(() => {
  if (user.value) {
    form.name = user.value.name || ''
    form.phone = user.value.phone || ''
    form.role = (user.value.role as string) || 'user'
  }
})

const saving = ref(false)
async function save(){
  saving.value = true
  try {
    await $api(`/admin/users/${id.value}`, {
      method: 'PUT',
      body: { name: form.name, phone: form.phone, role: form.role }
    })
    await loadAll()
    isEditing.value = false
  } catch (e){
    console.error(e)
    alert('Save failed')
  } finally { saving.value = false }
}
function cancelEdit(){
  isEditing.value = false
  if (user.value){
    form.name = user.value.name || ''
    form.phone = user.value.phone || ''
    form.role = (user.value.role as string) || 'user'
  }
}

function formatDate(s?: string){ return s ? new Date(s).toLocaleString() : '-' }
function formatMoney(n?: number){ return (n ?? 0).toLocaleString(undefined, { maximumFractionDigits: 2 }) }

/* Edit Balance modal logic */
const balanceDlg = ref<HTMLDialogElement | null>(null)
const targetAccount = ref<any | null>(null)
const newBalance = ref<string>('')
const editingBalance = ref(false)

function openBalanceDialog(a: any) {
  if (!a?.id) {
    alert('This account is missing an ID; cannot edit balance. Ensure /admin/users/{id}/accounts returns { id, ... }.')
    return
  }
  targetAccount.value = a
  newBalance.value = String(a.balance ?? '')
  balanceDlg.value?.showModal()
}

async function saveBalance() {
  if (!targetAccount.value?.id) return
  editingBalance.value = true
  try {
    const payload = { balance: Number(newBalance.value) }
    await $api(`/admin/users/${id.value}/accounts/${targetAccount.value.id}`, {
      method: 'PUT',
      body: payload
    })
    balanceDlg.value?.close()
    targetAccount.value = null
    await loadAll() // refresh account list after saving
  } catch (e) {
    console.error(e)
    alert('Failed to update balance')
  } finally {
    editingBalance.value = false
  }
}

/* Inline child components without JSX */
const FormRow = defineComponent({
  name: 'FormRow',
  props: { label: { type: String, required: true } },
  setup(props, { slots }) {
    return () =>
      h('div', null, [
        h('div', { class: 'text-gray-500 text-xs mb-1' }, props.label),
        h('div', { class: 'font-medium' }, slots.default ? slots.default() : null),
      ])
  }
})

const RoleBadge = defineComponent({
  name: 'RoleBadge',
  props: { role: { type: String, default: 'user' } },
  setup(props) {
    return () =>
      h('span', { class: 'inline-block rounded-full px-2 py-0.5 text-xs border' }, props.role || 'user')
  }
})
</script>
