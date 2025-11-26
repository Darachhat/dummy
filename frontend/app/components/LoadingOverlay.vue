<template>
  <Teleport to="body">
    <div
      v-if="globalLoading"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm"
      aria-hidden="true"
    >
      <div class="bg-white/90 dark:bg-gray-900/80 rounded-xl p-6 flex flex-col items-center gap-3 shadow-lg">
        <!-- spinner -->
        <svg class="w-10 h-10 animate-spin" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" class="text-gray-200"></circle>
          <path d="M22 12a10 10 0 00-10-10" stroke="currentColor" stroke-width="4" class="text-gray-800"></path>
        </svg>
        <div class="text-sm text-gray-700">Loading…</div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
const globalLoading = useState<boolean>('globalLoading')
</script>

<style scoped>
/* nothing special; Tailwind classes used */
</style>
