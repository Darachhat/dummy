<template>
  <div class="min-h-screen bg-gray-100 flex flex-col items-center py-8">
    <!-- Header -->
    <div class="flex gap-6 items-center w-full max-w-md mb-6">
      <button @click="navigateTo('/')" class="p-2 bg-white rounded-full shadow">
        <ArrowLeft class="w-5 h-5 text-gray-600" />
      </button>
      <h2 class="text-lg font-semibold mx-3 px-24 text-gray-700">Bill Payment</h2>
    
    </div>

    <div
      v-if="services.length"
      class="bg-white rounded-2xl shadow w-full max-w-md divide-y divide-gray-200"
    >
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
          />
          <span class="font-medium text-gray-700">{{ s.name }}</span>
        </div>
        <ChevronRight class="w-5 h-5 text-gray-400" />
      </button>
    </div>

    <!-- Empty State -->
    <div v-else class="text-gray-500 mt-10">Loading services...</div>
  </div>
</template>

<script setup lang="ts">
const { $api } = useNuxtApp()
const services = ref<any[]>([])
const config = useRuntimeConfig()
const BACKEND_URL = config.public.apiBase


// Helper to ensure images load from backend, not frontend
const getLogoUrl = (path: string) => {
  if (!path) return '/logos/default.png'
  if (path.startsWith('http')) return path
  return `${BACKEND_URL}${path}`
}

// Fetch services from backend
onMounted(async () => {
  try {
    const res = await $api('/services')
    services.value = res
  } catch (err) {
    console.error('Failed to load services', err)
  }
})

// Store selected service for next page
const selectService = (s: any) => {
  const paymentSelection = useState('paymentSelection')
  paymentSelection.value = { service: s, service_id: s.id }
  navigateTo('/payment/invoice')
}

</script>
