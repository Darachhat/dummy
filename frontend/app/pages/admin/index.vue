<template>
  <div class="min-h-screen flex bg-gray-50 relative">
    <!-- Overlay for mobile -->
    <div
      v-if="sidebarOpen && !isDesktop"
      class="fixed inset-0 bg-black bg-opacity-40 z-30"
      @click="sidebarOpen = false"
    ></div>

    <!-- Sidebar -->
    <aside
      :class="[
        'bg-white shadow-sm z-40 transform transition-transform duration-300 ease-in-out fixed md:static md:translate-x-0',
        'h-screen md:h-auto w-64 flex flex-col justify-between p-6 md:min-h-screen',
        'rounded-none md:rounded-xl',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full',
      ]"
    >
      <div class="flex-1 flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-8">
            <h1 class="text-2xl font-bold text-gray-800">Admin</h1>
            <button
              v-if="!isDesktop"
              @click="sidebarOpen = false"
              class="text-gray-500 hover:text-gray-800 md:hidden"
            >
              <X class="w-5 h-5" />
            </button>
          </div>

          <!-- ADMIN NAV -->
          <nav class="space-y-3 flex-1">
            <SidebarItem label="Home" icon="Home" to="/admin" :collapsed="!isDesktop" />
            <SidebarItem label="User Management" icon="User" to="/admin/users" :collapsed="!isDesktop" />
            <SidebarItem label="Payments" icon="CreditCard" to="/admin/payments" :collapsed="!isDesktop" />
            <SidebarItem label="Transactions" icon="List" to="/admin/transactions" :collapsed="!isDesktop" />
            <SidebarItem label="Service Management" icon="List" to="/admin/services" :collapsed="!isDesktop" />
          </nav>
        </div>

        <button
          @click="logout"
          class="flex items-center gap-2 text-gray-500 hover:text-red-600 transition mt-8"
        >
          <LogOut class="w-5 h-5" />
          <span>Logout</span>
        </button>
      </div>
    </aside>

    <!-- Main content -->
    <main class="flex-1 flex flex-col p-4 md:p-8 w-full relative">
      <!-- Mobile Navbar -->
      <div class="flex items-center md:hidden mb-6 sticky top-0 bg-gray-50 z-20 px-2">
        <button @click="sidebarOpen = true" class="text-gray-700 hover:text-gray-900">
          <Menu class="w-6 h-6" />
        </button>
        <h2 class="ml-3 text-lg font-semibold">Admin Dashboard</h2>
      </div>

      <!-- Page header -->
      <div class="hidden md:flex justify-between items-center mb-8">
        <h2 class="text-2xl font-bold text-gray-800 capitalize">Admin Dashboard</h2>
      </div>

      <!-- Content -->
      <section class="grid md:grid-cols-3 gap-6">
        <div class="bg-white rounded-xl shadow p-6">
          <p class="text-sm text-gray-500">Manage</p>
          <NuxtLink to="/admin/users" class="block mt-2 font-semibold text-gray-800 hover:underline">
            User Management →
          </NuxtLink>
        </div>

        <div class="bg-white rounded-xl shadow p-6">
          <p class="text-sm text-gray-500">Monitor</p>
          <NuxtLink to="/admin/transactions" class="block mt-2 font-semibold text-gray-800 hover:underline">
            Transactions →
          </NuxtLink>
        </div>

        <div class="bg-white rounded-xl shadow p-6">
          <p class="text-sm text-gray-500">System</p>
          <NuxtLink to="/admin/services" class="block mt-2 font-semibold text-gray-800 hover:underline">
            Service Management →
          </NuxtLink>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import SidebarItem from '~/components/SidebarItem.vue'
import { LogOut, Menu, X } from 'lucide-vue-next'

const { $api } = useNuxtApp()
const { logout } = useAuth()

const isDesktop = ref(false)
const sidebarOpen = ref(false)

onMounted(() => {
  const updateScreenSize = () => { isDesktop.value = window.innerWidth >= 768 }
  updateScreenSize()
  window.addEventListener('resize', updateScreenSize)
})
onBeforeUnmount(() => window.removeEventListener('resize', () => {}))
</script>

<style scoped>
a.router-link-active {
  background-color: #f3f4f6;
  color: #111827;
}
</style>
