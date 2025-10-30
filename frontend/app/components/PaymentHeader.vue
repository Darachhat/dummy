<template>
  <div class="flex items-center w-full max-w-md mb-6">
    <button
      @click="navigateTo(backPath)"
      class="p-2 bg-white rounded-full shadow hover:bg-gray-50"
    >
      <ArrowLeft class="w-5 h-5 text-gray-600" />
    </button>

    <div class="flex mx-3 items-center space-x-3 ">
      <img
        v-if="service?.logo_url"
        :src="getLogoUrl(service.logo_url)"
        alt="Service Logo"
        class="w-10 h-10 rounded-full object-contain"
      />
      <h2 class="text-lg font-semibold text-gray-700">
        Bill to {{ service?.name || 'Service' }}
      </h2>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  service: {
    type: Object,
    required: false
  },
  backPath: {
    type: String,
    default: '/payment/start'
  }
})

const config = useRuntimeConfig()
const BACKEND_URL = config.public.apiBase

const getLogoUrl = (path: string) => {
  if (!path) return `${BACKEND_URL}/static/logos/default.png`
  if (path.startsWith('http')) return path
  return `${BACKEND_URL}${path}`
}
</script>
