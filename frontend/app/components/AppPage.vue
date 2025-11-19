<!-- components/AppPage.vue -->
<template>
  <div class="min-h-screen bg-gray-50 flex flex-col items-center py-10 px-4">
    <!-- Header -->
    <div class="relative flex items-center justify-center w-full max-w-lg mb-8">
      <button
        v-if="backTo"
        @click="navigateTo(backTo)"
        class="absolute left-4 p-2 bg-white rounded-full shadow hover:bg-gray-100 transition"
      >
        <ArrowLeft class="w-5 h-5 text-gray-700" />
      </button>

      <!-- Default header title, can be overridden via slot -->
      <slot name="header-center">
        <h2 class="text-xl font-semibold text-gray-800 text-center">
          {{ title }}
        </h2>
      </slot>
    </div>

    <!-- NEW SLOT: Stepper or anything between header and content -->
    <slot name="header-after"></slot>

    <!-- Page body -->
    <div class="w-full max-w-lg">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ArrowLeft } from 'lucide-vue-next'

defineProps<{
  title?: string
  backTo?: string | null
}>()
</script>
