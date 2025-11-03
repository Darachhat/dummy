<template>
  <div class="min-h-screen bg-gray-100 flex flex-col items-center py-8">
    <!-- Header -->
    <div class="flex gap-4 items-center w-full max-w-md mb-6 px-4">
      <button @click="navigateTo('/')" class="p-2 bg-white rounded-full shadow hover:bg-gray-50">
        <ArrowLeft class="w-5 h-5 text-gray-600" />
      </button>
      <h2 class="text-lg font-semibold text-gray-700">Bill Payment</h2>
    </div>

    <!-- Service List -->
    <div v-if="services.length" class="bg-white rounded-2xl shadow w-full max-w-md divide-y divide-gray-100">
      <button
        v-for="s in services"
        :key="s.id"
        class="flex items-center justify-between w-full px-4 py-4 hover:bg-gray-50 transition"
        @click="selectService(s)"
      >
        <div class="flex items-center space-x-3">
          <img
            :src="getLogoUrl(s.logo_url)"
            alt="Service Logo"
            class="w-8 h-8 rounded-full object-contain"
            loading="lazy"
          />
          <span class="font-medium text-gray-700">{{ s.name }}</span>
        </div>
        <ChevronRight class="w-5 h-5 text-gray-400" />
      </button>
    </div>

    <!-- Loading & Empty State -->
    <div v-else class="text-gray-500 mt-10">
      <p v-if="loading">Loading services...</p>
      <p v-else>No services available</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const { $api } = useNuxtApp()
const services = ref<any[]>([])
const loading = ref(true)
const BACKEND_URL = useRuntimeConfig().public.apiBase

// Helper to resolve backend image paths
const getLogoUrl = (path: string) => {
  if (!path) return `${BACKEND_URL}/static/logos/default.png`
  return path.startsWith('http') ? path : `${BACKEND_URL}${path}`
}

// Fetch services
onMounted(async () => {
  try {
    services.value = await $api('/services')
  } catch (err) {
    console.error('Failed to load services:', err)
  } finally {
    loading.value = false
  }
})

// Select and go next
const selectService = (s: any) => {
  const paymentSelection = useState('paymentSelection')
  paymentSelection.value = { service: s, service_id: s.id }
  navigateTo('/payment/invoice')
}
</script>
