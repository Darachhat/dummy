<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">User Details</h1>

    <div v-if="loading">Loading user data...</div>
    <div v-else-if="user">
      <h2 class="text-lg font-semibold mb-2">User Info</h2>
      <p><strong>Name:</strong> {{ user.name }}</p>
      <p><strong>Phone:</strong> {{ user.phone }}</p>
      <p><strong>Role:</strong> {{ user.role }}</p>

      <!-- Accounts -->
      <h2 class="text-lg font-semibold mt-6 mb-2">Accounts</h2>
      <table class="w-full border text-sm mb-6">
        <thead class="bg-gray-100">
          <tr>
            <th class="p-2 text-left">ID</th>
            <th class="p-2 text-left">Name</th>
            <th class="p-2 text-left">Number</th>
            <th class="p-2 text-left">Balance</th>
            <th class="p-2 text-left">Currency</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="a in accounts" :key="a.id" class="border-t">
            <td class="p-2">{{ a.id }}</td>
            <td class="p-2">{{ a.name }}</td>
            <td class="p-2">{{ a.number }}</td>
            <td class="p-2">{{ a.balance }}</td>
            <td class="p-2">{{ a.currency }}</td>
          </tr>
        </tbody>
      </table>

      <!-- Transactions -->
      <h2 class="text-lg font-semibold mb-2">Transactions</h2>
      <table class="w-full border text-sm mb-6">
        <thead class="bg-gray-100">
          <tr>
            <th class="p-2 text-left">ID</th>
            <th class="p-2 text-left">Type</th>
            <th class="p-2 text-left">Amount</th>
            <th class="p-2 text-left">Status</th>
            <th class="p-2 text-left">Date</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in transactions" :key="t.id" class="border-t">
            <td class="p-2">{{ t.id }}</td>
            <td class="p-2">{{ t.type }}</td>
            <td class="p-2">{{ t.amount }}</td>
            <td class="p-2">{{ t.status }}</td>
            <td class="p-2">{{ formatDate(t.created_at) }}</td>
          </tr>
        </tbody>
      </table>

      <!-- Payments -->
      <h2 class="text-lg font-semibold mb-2">Payments</h2>
      <table class="w-full border text-sm">
        <thead class="bg-gray-100">
          <tr>
            <th class="p-2 text-left">ID</th>
            <th class="p-2 text-left">Amount</th>
            <th class="p-2 text-left">Currency</th>
            <th class="p-2 text-left">Status</th>
            <th class="p-2 text-left">Date</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in payments" :key="p.id" class="border-t">
            <td class="p-2">{{ p.id }}</td>
            <td class="p-2">{{ p.amount }}</td>
            <td class="p-2">{{ p.currency }}</td>
            <td class="p-2">{{ p.status }}</td>
            <td class="p-2">{{ formatDate(p.created_at) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else>
      <p>No user found.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const route = useRoute()
const config = useRuntimeConfig()

const user = ref(null)
const accounts = ref([])
const transactions = ref([])
const payments = ref([])
const loading = ref(true)

const formatDate = (date: string) => new Date(date).toLocaleString()

onMounted(async () => {
  const id = route.params.id
  try {
    user.value = await $fetch(`${config.public.apiBase}/admin/users/${id}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    })
    accounts.value = await $fetch(`${config.public.apiBase}/admin/users/${id}/accounts`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    transactions.value = await $fetch(`${config.public.apiBase}/admin/users/${id}/transactions`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    payments.value = await $fetch(`${config.public.apiBase}/admin/users/${id}/payments`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
  } catch (err) {
    console.error('Failed to fetch user details:', err)
  } finally {
    loading.value = false
  }
})
</script>
