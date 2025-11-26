<template>
  <div class="flex min h-screen">
    <!-- Sidebar -->
    <aside
      :class="[
        'border-r shadow-sm bg-white z-40 transform transition-transform duration-300 ease-in-out fixed md:static md:translate-x-0',
        'h-screen md:h-auto w-64 flex flex-col justify-between p-6',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      ]"
    >
      <div>
        <div class="flex items-center justify-between mb-8">
          <NuxtLink
  to="/adm"
  class="text-2xl font-bold hover:text-neutral transition-colors"
>
  cdcOSP - ADM
</NuxtLink>

          <UButton
            v-if="!isDesktop"
            color="neutral"
            variant="ghost"
            icon="i-lucide-x"
            @click="sidebarOpen = false"
          />
        </div>

        <!-- Navigation -->
        <nav class="space-y-2">
          <SidebarItem label="Home" icon="Home" to="/adm" />
          <SidebarItem label="User" icon="User" to="/adm/users" />
          <SidebarItem label="Transactions" icon="CreditCard" to="/adm/payments" />
          <SidebarItem label="Transactions Log" icon="List" to="/adm/transactions" />
          <SidebarItem label="Services" icon="Settings" to="/adm/services" />
        </nav>
      </div>

      <UButton
        color="error"
        variant="subtle"
        label="Logout"
        icon="i-lucide-log-out"
        class="mt-8"
        @click="logout"
      />
    </aside>

    <!-- Main -->
    <main class="flex-1 p-4 md:p-8 overflow-x-hidden">
      <!-- Mobile Navbar -->
      <div class="flex items-center md:hidden mb-6 sticky top-0 z-20 bg-white/70 backdrop-blur">
        <UButton icon="i-lucide-menu" color="neutral" variant="ghost" @click="sidebarOpen = true" />
        <h2 class="ml-3 text-lg font-semibold truncate">{{ adminTitle }}</h2>
      </div>

      <!-- Page content -->
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import SidebarItem from '~/components/SidebarItem.vue'
import { useMediaQuery } from '@vueuse/core'

const { logout } = useAuth()

// match your index.vue behavior
const isDesktop = useMediaQuery('(min-width: 768px)')
const sidebarOpen = ref(false)

// page-provided title (via composable)
const adminTitle = useAdminTitle()
</script>
