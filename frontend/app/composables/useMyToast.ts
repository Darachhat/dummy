// app/composables/useMyToast.ts
import { ref } from 'vue'

type Toast = {
  id: number
  message: string
  type: 'success' | 'error' | 'info'
  duration?: number
}

const toasts = ref<Toast[]>([])

export function useMyToast() {
  const _push = (message: string, type: Toast['type'] = 'info', duration = 3000) => {
    const id = Date.now() + Math.floor(Math.random() * 1000)
    toasts.value.push({ id, message, type, duration })
    setTimeout(() => remove(id), duration)
  }

  const show = (message: string, type: Toast['type'] = 'info', duration = 3000) => {
    _push(message, type, duration)
  }

  const add = (arg1: any, arg2?: any, arg3?: any) => {
    if (arg1 && typeof arg1 === 'object') {
      const message = arg1.title || arg1.message || 'Notification'
      const color = (arg1.color as Toast['type']) || (arg1.type as Toast['type']) || 'info'
      const duration = arg1.duration ?? 3000
      _push(message, color, duration)
      return
    }

    const message = String(arg1 ?? '')
    const type = (arg2 as Toast['type']) || 'info'
    const duration = typeof arg3 === 'number' ? arg3 : 3000
    _push(message, type, duration)
  }

  const remove = (id: number) => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }

  return { toasts, show, add, remove }
}
