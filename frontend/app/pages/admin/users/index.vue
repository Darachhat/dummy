<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">User Management</h1>

    <div v-if="loading">Loading users...</div>
    <div v-else>
      <table class="w-full border text-sm">
        <thead class="bg-gray-100">
          <tr>
            <th class="p-2 text-left">ID</th>
            <th class="p-2 text-left">Name</th>
            <th class="p-2 text-left">Phone</th>
            <th class="p-2 text-left">Role</th>
            <th class="p-2 text-left">Created At</th>
            <th class="p-2 text-center">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id" class="border-t hover:bg-gray-50">
            <td class="p-2">{{ user.id }}</td>
            <td class="p-2">{{ user.name }}</td>
            <td class="p-2">{{ user.phone }}</td>
            <td class="p-2">{{ user.role }}</td>
            <td class="p-2">{{ formatDate(user.created_at) }}</td>
            <td class="p-2 text-center">
              <NuxtLink
                :to="`/admin/users/${user.id}`"
                class="text-blue-600 hover:underline"
              >
                View / Edit
              </NuxtLink>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
const users = ref<any[]>([])
const loading = ref(true)

const config = useRuntimeConfig()

const formatDate = (date: string) => new Date(date).toLocaleString()

onMounted(async () => {
  try {
    users.value = await $fetch(`${config.public.apiBase}/admin/users`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    })
  } catch (err) {
    console.error('Failed to fetch users:', err)
  } finally {
    loading.value = false
  }
})
</script>
