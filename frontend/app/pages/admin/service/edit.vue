<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">Edit Service</h1>

    <div v-if="service" class="space-y-4">
      <label class="block">
        <span class="text-gray-700">Service Name</span>
        <input
          v-model="service.name"
          type="text"
          class="mt-1 block w-full border rounded-lg px-3 py-2"
        />
      </label>

      <label class="block">
        <span class="text-gray-700">Service Code</span>
        <input
          v-model="service.code"
          type="text"
          class="mt-1 block w-full border rounded-lg px-3 py-2"
        />
      </label>

      <label class="block">
        <span class="text-gray-700">Logo URL</span>
        <input
          v-model="service.logo_url"
          type="text"
          class="mt-1 block w-full border rounded-lg px-3 py-2"
        />
      </label>

      <button
        class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        @click="updateService"
      >
        Save Changes
      </button>
    </div>

    <div v-else>
      <p>Loading service details...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const route = useRoute()
const router = useRouter()
const service = ref<any>(null)

onMounted(async () => {
  try {
    service.value = await $fetch(`/admin/services/${route.query.id}`)
  } catch (error) {
    console.error('Failed to load service:', error)
  }
})

const updateService = async () => {
  if (!service.value) return
  try {
    await $fetch(`/admin/services/${route.query.id}`, {
      method: 'PUT',
      body: service.value
    })
    alert('Service updated successfully!')
    router.push('/admin/services')
  } catch (error) {
    console.error('Failed to update service:', error)
  }
}
</script>
