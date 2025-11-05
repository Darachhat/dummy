<template>
  <div class="bg-white rounded-2xl shadow w-full max-w-md p-6 text-center">
    <p class="text-sm text-gray-600 mb-4">Enter your 4-digit PIN</p>

    <div class="flex justify-center space-x-3 mb-6">
      <input
        v-for="i in 4"
        :key="i"
        ref="pinInputs"
        type="password"
        maxlength="1"
        inputmode="numeric"
        class="w-12 h-12 text-center border border-gray-300 rounded-lg text-lg font-semibold focus:ring-2 focus:ring-blue-500 focus:outline-none"
        @input="handleInput(i - 1, $event)"
        @keydown.backspace="handleBackspace(i - 1, $event)"
      />
    </div>

    <button
      :disabled="pin.join('').length < 4 || isLoading"
      @click="submit"
      class="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
    >
      <span v-if="!isLoading">CONFIRM PAYMENT</span>
      <span v-else>Processing...</span>
    </button>

    <p v-if="error" class="text-red-600 text-sm mt-3">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  paymentId: Number
})
const emit = defineEmits(['confirmed'])

const { $api } = useNuxtApp()
const pin = ref(['', '', '', ''])
const pinInputs = ref<HTMLInputElement[]>([])
const error = ref('')
const isLoading = ref(false)

const handleInput = (index: number, e: Event) => {
  const target = e.target as HTMLInputElement
  pin.value[index] = target.value
  if (target.value && index < 3) pinInputs.value[index + 1]?.focus()
}

const handleBackspace = (index: number, e: KeyboardEvent) => {
  const target = e.target as HTMLInputElement
  if (!target.value && index > 0) pinInputs.value[index - 1]?.focus()
}

const submit = async () => {
  if (pin.value.join('').length !== 4) {
    error.value = 'Please enter your 4-digit PIN.'
    return
  }

  isLoading.value = true
  try {
    const code = pin.value.join('')
    const res = await $api(`/payments/${props.paymentId}/confirm?pin=${code}`, { method: 'POST' })
    emit('confirmed', res)
  } catch (err: any) {
    error.value = err.response?._data?.detail || 'Failed to confirm payment.'
  } finally {
    isLoading.value = false
  }
}
</script>
