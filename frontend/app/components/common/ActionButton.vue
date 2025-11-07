<template>
  <div class="flex flex-col items-center">
    <button
      :class="[
        'w-14 h-14 rounded-full flex items-center justify-center text-white shadow-md hover:opacity-90 active:scale-95 transition',
        color === 'blue'
          ? 'bg-blue-600'
          : color === 'indigo'
          ? 'bg-indigo-600'
          : 'bg-gray-600',
      ]"
      @click="$emit('click')"
    >
      <component :is="iconComponent" class="w-6 h-6" />
    </button>
    <span class="text-sm text-gray-700 mt-1 font-medium">{{ label }}</span>
  </div>
</template>

<script setup lang="ts">
import { ArrowUpRight, List, User } from 'lucide-vue-next'

const props = defineProps({
  icon: { type: String, required: true },
  label: { type: String, required: true },
  color: { type: String, required: true },
})

defineEmits(['click'])

const icons = { ArrowUpRight, List, User }
const iconComponent = computed(() => icons[props.icon as keyof typeof icons])
</script>
