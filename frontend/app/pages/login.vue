<template>
  <div class="min-h-screen flex flex-col md:flex-row">
    <!-- Left side: Background image -->
    <div
      class="hidden md:flex md:w-1/2 bg-cover bg-center"
      style="background-image: url('/images/dummybank-bg.jpg');"
    ></div>

    <!-- Right side: Login form -->
    <div
      class="flex flex-1 flex-col justify-center items-center bg-gray-50 px-6 py-12"
    >
      <!-- Logo / App Title -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900">DummyBank</h1>
        <p class="text-gray-500 text-sm mt-1">Secure Digital Banking Access</p>
      </div>

      <!-- Login Card -->
      <div
        class="bg-white w-full max-w-md shadow-lg rounded-2xl p-8 border border-gray-100"
      >
        <h2 class="text-lg font-semibold text-gray-800 text-center mb-6">
          Sign in to your account
        </h2>

        <form @submit.prevent="submit" class="space-y-5">
          <!-- Phone Number -->
          <div>
            <label class="block text-sm text-gray-600 mb-1">Phone Number</label>
            <input
              v-model="phone"
              type="text"
              placeholder="Enter your phone number"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-gray-800 focus:outline-none"
            />
          </div>

          <!-- Password -->
          <div>
            <label class="block text-sm text-gray-600 mb-1">Password</label>
            <input
              v-model="password"
              type="password"
              placeholder="Enter your password"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-gray-800 focus:outline-none"
            />
          </div>

          <!-- Error -->
          <p
            v-if="error"
            class="text-red-600 text-sm text-center -mt-2"
          >
            {{ error }}
          </p>

          <!-- Login Button -->
          <button
            type="submit"
            class="w-full py-2 bg-gradient-to-r from-gray-800 to-gray-900 text-white rounded-lg font-medium hover:opacity-90 transition"
          >
            Sign In
          </button>

          <!-- Register Link -->
          <!-- <div class="text-center mt-4">
            <p class="text-sm text-gray-500">
              Don’t have an account?
              <a
                href="/register"
                class="text-gray-800 font-medium hover:underline"
              >
                Create one
              </a>
            </p>
          </div> -->
        </form>
      </div>

      <!-- Footer -->
      <div class="mt-8 text-center text-xs text-gray-500">
        <p>© 2025 DummyBank. All rights reserved.</p>
        <p class="mt-1">Version 1.0.0</p>
      </div>
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
    error.value = 'Invalid phone or password'
  }
}
</script>
