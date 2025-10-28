import { defineNuxtPlugin } from '#app'
import * as LucideIcons from 'lucide-vue-next'

export default defineNuxtPlugin((nuxtApp) => {
  for (const [name, component] of Object.entries(LucideIcons)) {
    nuxtApp.vueApp.component(name, component)
  }
})
