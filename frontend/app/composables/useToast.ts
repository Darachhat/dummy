import { ref } from 'vue'

type Toast = {
  id: number
  message: string
  type: 'success' | 'error' | 'info'
  duration?: number
}

const toasts = ref<Toast[]>([])

export function useToast() {
  const show = (message: string, type: Toast['type'] = 'info', duration = 3000) => {
    const id = Date.now()
    toasts.value.push({ id, message, type, duration })
    setTimeout(() => remove(id), duration)
  }

  const remove = (id: number) => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }

  return { toasts, show, remove }
}
