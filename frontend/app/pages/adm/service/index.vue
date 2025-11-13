<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">Service Management</h1>
    <div class="flex justify-end mb-4">
      <button
        class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        @click="addService"
      >Add Service</button>
    </div>

    <table class="min-w-full bg-white border rounded-xl">
      <thead class="bg-gray-100">
        <tr>
          <th class="py-2 px-4 text-left">ID</th>
          <th class="py-2 px-4 text-left">Name</th>
          <th class="py-2 px-4 text-left">Code</th>
          <th class="py-2 px-4 text-left">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="svc in services" :key="svc.id" class="border-t hover:bg-gray-50">
          <td class="py-2 px-4">{{ svc.id }}</td>
          <td class="py-2 px-4">{{ svc.name }}</td>
          <td class="py-2 px-4">{{ svc.code }}</td>
          <td class="py-2 px-4">
            <button class="text-blue-500 mr-2" @click="editService(svc.id)">Edit</button>
            <button class="text-red-500" @click="deleteService(svc.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
const services = ref([])

onMounted(async () => {
  services.value = await $fetch('/adm/services')
})

const addService = async () => {
  const name = prompt('Service name:')
  const code = prompt('Service code:')
  if (name && code) {
    await $fetch('/adm/services', {
      method: 'POST',
      body: { name, code, logo_url: '/static/logos/default.png' }
    })
    services.value = await $fetch('/adm/services')
  }
}

const editService = async (id: number) => {
  const name = prompt('New name:')
  if (name) {
    await $fetch(`/adm/services/${id}`, {
      method: 'PUT',
      body: { name }
    })
    services.value = await $fetch('/adm/services')
  }
}

const deleteService = async (id: number) => {
  if (confirm('Delete this service?')) {
    await $fetch(`/adm/services/${id}`, { method: 'DELETE' })
    services.value = services.value.filter(s => s.id !== id)
  }
}
</script>
