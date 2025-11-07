<template>
  <div class="flex items-center w-full max-w-md mb-6 px-4">
    <button
      @click="$emit('back')"
      class="p-2 bg-white rounded-full shadow hover:bg-gray-50"
    >
      <ArrowLeft class="w-5 h-5 text-gray-600" />
    </button>
    <h2 class="mx-auto text-lg font-semibold text-gray-700">{{ title }}</h2>
  </div>
</template>

<script setup lang="ts">
defineProps({
  title: {
    type: String,
    required: true
  }
})
</script>
