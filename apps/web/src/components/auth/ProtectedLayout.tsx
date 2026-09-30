import { useAuth } from '@clerk/clerk-react'
import { Navigate, Outlet } from 'react-router-dom'

import { Layout } from '@/components/layout/Layout'

export function ProtectedLayout() {
  const { isLoaded, isSignedIn } = useAuth()

  if (!isLoaded) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background p-6 text-sm text-muted-foreground">
        Loading your workspace...
      </div>
    )
  }

  if (!isSignedIn) {
    return <Navigate to="/sign-in" replace />
  }

  return (
    <Layout>
      <Outlet />
    </Layout>
  )
}
