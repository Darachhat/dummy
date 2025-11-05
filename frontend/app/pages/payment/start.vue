<template>
  <div class="min-h-screen bg-gray-100 flex flex-col items-center py-8">
    <div class="flex items-center w-full max-w-md mb-6 px-4">
      <button @click="navigateTo('/')" class="p-2 bg-white rounded-full shadow hover:bg-gray-50">
        <ArrowLeft class="w-5 h-5 text-gray-600" />
      </button>
      <h2 class="mx-auto text-lg font-semibold text-gray-700">Bill Payment</h2>
    </div>

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
import { useToast } from '~/composables/useToast'
const { show } = useToast()

const getLogoUrl = (path: string) => {
  if (!path) return `${BACKEND_URL}/static/logos/default.svg`
  return path.startsWith('http') ? path : `${BACKEND_URL}${path}`
}

onMounted(async () => {
  try {
    services.value = await $api('/services')
  } catch (err) {
    show('Failed to load services', 'error')
  } finally {
    loading.value = false
  }
})

const selectService = (s: any) => {
  const paymentSelection = useState('paymentSelection')
  paymentSelection.value = { service: s, service_id: s.id }
  navigateTo('/payment/invoice')
}
</script>
