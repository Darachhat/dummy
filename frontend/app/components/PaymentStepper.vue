<template>
  <div class="w-full max-w-lg mx-auto">
    <nav aria-label="Payment steps" class="flex items-center justify-between">
      <div
        v-for="(s, i) in steps"
        :key="s.key"
        class="flex-1 px-1 first:pl-0 last:pr-0"
      >
        <div class="flex items-center">
          <div
            :class="[
              'flex items-center justify-center rounded-full w-8 h-8 shrink-0',
              i+1 < step ? 'bg-green-600 text-white' : i+1 === step ? 'bg-gray-900 text-white' : 'bg-white text-gray-400 border border-gray-200'
            ]"
            aria-hidden="true"
          >
            <span v-if="i+1 < step">✓</span>
            <span v-else>{{ i+1 }}</span>
          </div>

          <div class="ml-3 text-left">
            <div :class="[ i+1 <= step ? 'text-gray-900 font-semibold' : 'text-gray-400 text-sm' ]">
              {{ s.title }}
            </div>
            <div v-if="s.subtitle" class="text-xs text-gray-400 -mt-0.5">
              {{ s.subtitle }}
            </div>
          </div>
        </div>

        <!-- connector -->
        <div
          v-if="i < steps.length - 1"
          :class="[
            'h-0.5 mt-3 w-full block',
            (i+1) < step ? 'bg-green-600' : 'bg-gray-200'
          ]"
        ></div>
      </div>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue'

const props = defineProps<{
  step?: number // 1..4
  compact?: boolean
}>()

const step = props.step ?? 1

const steps = [
  { key: 'start', title: 'Select Service', subtitle: '' },
  { key: 'invoice', title: 'Invoice', subtitle: 'Enter ref & amount' },
  { key: 'confirm', title: 'Confirm', subtitle: 'Enter PIN' },
  { key: 'success', title: 'Success', subtitle: 'Receipt' },
]
</script>

<style scoped>
/* small helper to visually space connectors in small widths */
nav > div > .h-0.5 {
  margin-left: 2.5rem;
  margin-right: 0.25rem;
}
@media (min-width: 768px) {
  nav > div > .h-0.5 { margin-left: 3.5rem; }
}
</style>
