<template>
  <div class="relative group">
    <NuxtLink
      :to="to"
      class="flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-200 w-full"
      :class="[
        isActive
          ? 'bg-gray-100 text-gray-900 font-medium'
          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900',
      ]"
    >
      <component :is="iconComponent" class="w-5 h-5 shrink-0" />

      <!-- Always show label on mobile OR when expanded on desktop -->
      <span v-if="!isDesktop || !collapsed" class="truncate">
        {{ label }}
      </span>
    </NuxtLink>

    <div
      v-if="isDesktop && collapsed"
      class="absolute left-full top-1/2 transform -translate-y-1/2 ml-2
             bg-gray-900 text-white text-xs font-medium py-1 px-2 rounded-md
             opacity-0 pointer-events-none group-hover:opacity-100
             transition-opacity whitespace-nowrap z-50"
    >
      {{ label }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Home, CreditCard, List, User, LogOut } from 'lucide-vue-next'

const props = defineProps({
  label: { type: String, required: true },
  icon: { type: String, required: true },
  to: { type: String, required: true },
  collapsed: { type: Boolean, default: false },
})

const route = useRoute()
const isDesktop = ref(false)

onMounted(() => {
  const updateScreen = () => {
    isDesktop.value = window.innerWidth >= 768
  }
  updateScreen()
  window.addEventListener('resize', updateScreen)
})

const icons: Record<string, any> = {
  Home,
  CreditCard,
  List,
  User,
  LogOut,
}

const iconComponent = computed(() => icons[props.icon] || Home)
const isActive = computed(() => route.path === props.to)
</script>

<style scoped>
a.router-link-active {
  background-color: #f3f4f6;
  color: #111827;
}
</style>
