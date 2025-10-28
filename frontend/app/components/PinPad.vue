<template>
  <div class="grid grid-cols-3 gap-3 w-56 mx-auto">
    <div
      v-for="d in digits"
      :key="d"
      class="border rounded p-4 text-center cursor-pointer select-none text-xl font-medium"
      @click="press(d)"
    >
      {{ d }}
    </div>
  </div>
</template>

<script setup lang="ts">
const model = defineModel<string>({ default: '' })
const emit = defineEmits(['submit'])
const digits = ['1','2','3','4','5','6','7','8','9','←','0','✓']

const press = (d: string) => {
  if (d === '←') model.value = model.value.slice(0, -1)
  else if (d === '✓') emit('submit')
  else if (model.value.length < 4) model.value += d
}
</script>
