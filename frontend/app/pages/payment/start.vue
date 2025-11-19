<!-- src/pages/payment/start.vue -->
<template>
  <AppPage title="Bill Payment" back-to="/">
    <!-- Title -->
    <div class="w-full mb-6 text-center">
      <h3 class="text-lg font-medium text-gray-700">Choose a Service to Pay</h3>
      <p class="text-sm text-gray-500 mt-1">
        Select a service provider to continue
      </p>
    </div>

    <!-- Services -->
    <div v-if="services.length" class="grid grid-cols-1 gap-3 w-full">
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
  </AppPage>
</template>

<script setup lang="ts">
import PaymentStepper from '~/components/PaymentStepper.vue'
import { ChevronRight } from 'lucide-vue-next'
import AppPage from '~/components/AppPage.vue'
import { useLogoUrl } from '~/composables/useLogoUrl'

const { $api } = useNuxtApp()
const services = ref<any[]>([])
const loading = ref(true)

const { getLogoUrl } = useLogoUrl()

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
