// frontend/composables/useAuth.ts
export const useAuth = () => {
  const { $api, $token } = useNuxtApp()
  const me = useState<any>('me', () => null)

  const login = async (phone: string, password: string) => {
    const res: any = await $api('/auth/login', {
      method: 'POST',
      body: { phone, password }
    })
    $token.value = res.access_token
    me.value = await $api('/me')
  }

  const logout = () => {
    $token.value = null
    me.value = null
    navigateTo('/login')
  }

  const fetchMe = async () => {
    try {
      me.value = await $api('/me')
    } catch {
      me.value = null
    }
  }

  return { me, login, logout, fetchMe }
}
