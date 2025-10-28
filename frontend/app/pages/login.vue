<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="bg-white rounded-2xl shadow-lg w-full max-w-sm p-8">
      <h1 class="text-3xl font-bold text-center mb-6 text-gray-800">
        Dummy Bank
      </h1>

      <form @submit.prevent="submit" class="space-y-4">
        <div>
          <label class="block text-sm text-gray-600 mb-1">Phone</label>
          <input
            v-model="phone"
            type="text"
            placeholder="Enter your phone"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-black focus:outline-none"
          />
        </div>

        <div>
          <label class="block text-sm text-gray-600 mb-1">Password</label>
          <input
            v-model="password"
            type="password"
            placeholder="Enter your password"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-black focus:outline-none"
          />
        </div>

        <button
          type="submit"
          class="w-full py-2 bg-black text-white rounded-lg hover:bg-gray-900 transition"
        >
          Login
        </button>

        <p v-if="error" class="text-red-600 text-sm text-center mt-2">
          {{ error }}
        </p>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
const { login } = useAuth()
const phone = ref('')
const password = ref('')
const error = ref('')

const submit = async () => {
  try {
    error.value = ''
    await login(phone.value, password.value)
    navigateTo('/')
  } catch {
    error.value = 'Invalid credentials'
  }
}
</script>
