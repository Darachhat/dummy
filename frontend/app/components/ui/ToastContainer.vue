<template>
  <div class="fixed top-4 right-4 z-50 space-y-2">
    <transition-group name="fade" tag="div">
      <div
        v-for="t in toasts"
        :key="t.id"
        class="px-4 py-3 rounded-lg shadow text-white flex items-center gap-2 w-72"
        :class="{
          'bg-green-600': t.type === 'success',
          'bg-red-600': t.type === 'error',
          'bg-blue-600': t.type === 'info',
        }"
      >
        <span>{{ t.message }}</span>
      </div>
    </transition-group>
  </div>
</template>

<script setup lang="ts">
import { useToast } from '~/composables/useToast'
const { toasts } = useToast()
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: all 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
