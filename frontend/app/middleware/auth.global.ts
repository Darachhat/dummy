export default defineNuxtRouteMiddleware((to, from) => {
  const token = useState<string | null>('token')

  // Public routes
  const publicPages = ['/login']
  const authRequired = !publicPages.includes(to.path)

  // If trying to access private route without token → redirect to login
  if (authRequired && !token.value) {
    return navigateTo('/login')
  }

  // If already logged in and tries to visit login → redirect to home
  if (!authRequired && token.value) {
    return navigateTo('/')
  }
})
