// middleware/auth.global.ts
export default defineNuxtRouteMiddleware((to) => {
  const token = useState<string | null>('token')
  const user =  useState<any>('user')
  const isAuth = !!token.value

  const publicPages = ['/login']
  const authRequired = !publicPages.includes(to.path)

  if (authRequired && !isAuth) return navigateTo('/login')
  if (!authRequired && isAuth) return navigateTo('/')
})
