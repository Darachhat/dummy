<!-- frontend/app/components/ui/LoadingSpinner.vue -->
<template>
  <div role="status" aria-live="polite" class="flex items-center justify-center">
    <svg
      class="animate-spin h-6 w-6"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
    </svg>
    <span class="sr-only">Loading</span>
  </div>
</template>

<script setup lang="ts">
// No props — keep tiny and accessible.
</script>

<style scoped>
/* rely on tailwind for sizing/animation; keep the svg color inheritable */
</style>
