<template>
  <div class="min-h-screen bg-gray-50 flex flex-col items-center py-10 px-4">
   <!-- Header -->
<div class="relative flex items-center justify-center w-full max-w-lg mb-8">
  <button
    @click="navigateTo('/')"
    class="absolute left-4 p-2 bg-white rounded-full shadow hover:bg-gray-100 transition"
  >
    <ArrowLeft class="w-5 h-5 text-gray-700" />
  </button>
  <h2 class="text-xl font-semibold text-gray-800 text-center">Bill Payment</h2>
</div>


    <!-- Title -->
    <div class="w-full max-w-lg mb-6 text-center">
      <h3 class="text-lg font-medium text-gray-700">Choose a Service to Pay</h3>
      <p class="text-sm text-gray-500 mt-1">Select a service provider to continue</p>
    </div>

    <!-- Services -->
    <div
      v-if="services.length"
      class="grid grid-cols-1 gap-3 w-full max-w-lg"
    >
      <button
        v-for="s in services"
        :key="s.id"
        @click="selectService(s)"
        class="flex items-center justify-between bg-white p-4 rounded-xl shadow hover:shadow-md transition group border border-gray-100"
      >
        <div class="flex items-center gap-3">
          <img
            :src="getLogoUrl(s.logo_url)"
            alt="Service Logo"
            class="w-10 h-10 rounded-full border object-contain"
          />
          <div class="text-left">
            <p class="font-medium text-gray-800 group-hover:text-gray-900">
              {{ s.name }}
            </p>
            <p class="text-xs text-gray-500">Tap to pay your bill</p>
          </div>
        </div>
        <ChevronRight class="w-5 h-5 text-gray-400 group-hover:text-gray-600" />
      </button>
    </div>

    <!-- Empty -->
    <div v-else class="text-gray-500 text-center mt-10">
      <p v-if="loading">Loading services...</p>
      <p v-else>No services available</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ArrowLeft, ChevronRight } from 'lucide-vue-next'

const { $api } = useNuxtApp()
const services = ref<any[]>([])
const loading = ref(true)
const BACKEND_URL = useRuntimeConfig().public.apiBase

const getLogoUrl = (path: string) =>
  !path
    ? `${BACKEND_URL}/static/logos/default.svg`
    : path.startsWith('http')
    ? path
    : `${BACKEND_URL}${path}`

onMounted(async () => {
  try {
    services.value = await $api('/services')
  } catch (err) {
    console.error('Failed to load services:', err)
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
