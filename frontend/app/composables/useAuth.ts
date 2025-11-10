export const useAuth = () => {
  const { $api, $token } = useNuxtApp()
  const me = useState<any>('me', () => null)

  const login = async (phone: string, password: string) => {
    try {
      const res: any = await $api('/auth/login', {
        method: 'POST',
        body: { phone, password }
      })
      $token.value = res.access_token
      await fetchMe()
    } catch (err) {
      throw new Error('Invalid credentials')
    }
  }

  const logout = () => {
    $token.value = null
    localStorage.removeItem('token')
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

  const isLoggedIn = computed(() => !!$token.value)

  return { me, login, logout, fetchMe, isLoggedIn }
}
