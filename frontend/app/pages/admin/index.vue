<template>
  <div class="flex h-screen">
    <!-- Sidebar -->
    <aside class="w-64 bg-gray-900 text-white p-4 flex flex-col">
      <h2 class="text-xl font-bold mb-6">Admin Panel</h2>
      <nav class="space-y-2">
        <NuxtLink to="/admin/users" class="block px-3 py-2 rounded hover:bg-gray-700">User Management</NuxtLink>
        <NuxtLink to="/admin/services" class="block px-3 py-2 rounded hover:bg-gray-700">Service Management</NuxtLink>
        <NuxtLink to="/admin/transactions" class="block px-3 py-2 rounded hover:bg-gray-700">Transaction Management</NuxtLink>
        <NuxtLink to="/admin/payments" class="block px-3 py-2 rounded hover:bg-gray-700">Payment Management</NuxtLink>
      </nav>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 bg-gray-50 p-6 overflow-y-auto">
      <NuxtPage />
    </main>
  </div>
</template>

<script setup lang="ts">
// This acts as a layout container
</script>
