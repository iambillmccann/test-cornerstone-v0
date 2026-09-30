import { useAuth, useUser } from '@clerk/clerk-react'
import { useEffect, useState } from 'react'

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { appDisplayName } from '@/lib/branding'

interface AppUserProfile {
  id: string
  email: string | null
  display_name: string | null
  avatar_url: string | null
}

export function Home() {
  const { getToken } = useAuth()
  const { user } = useUser()
  const [profile, setProfile] = useState<AppUserProfile | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const controller = new AbortController()

    const apiBaseUrl =
      import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') ?? 'http://localhost:8000'

    async function fetchProfileWithToken(token: string): Promise<AppUserProfile> {
      const response = await fetch(`${apiBaseUrl}/api/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        signal: controller.signal,
      })

      if (!response.ok) {
        const errorData = (await response.json()) as {
          error?: { message?: string }
        }
        const message = errorData?.error?.message ?? 'Unable to load profile'
        const error = new Error(message)
        ;(error as Error & { status?: number }).status = response.status
        throw error
      }

      return (await response.json()) as AppUserProfile
    }

    async function loadProfile() {
      try {
        const token = await getToken({ skipCache: true })
        if (!token) {
          throw new Error('No Clerk session token is available.')
        }

        const data = await fetchProfileWithToken(token)
        setProfile(data)
      } catch (err: unknown) {
        const isAuthError =
          err instanceof Error &&
          (err as Error & { status?: number }).status === 401

        if (isAuthError && !controller.signal.aborted) {
          try {
            await new Promise((resolve) => setTimeout(resolve, 300))
            const refreshedToken = await getToken({ skipCache: true })
            if (refreshedToken) {
              const retriedProfile = await fetchProfileWithToken(refreshedToken)
              setProfile(retriedProfile)
              setError(null)
              return
            }
          } catch {
            // Fall through to default error handling.
          }
        }

        if (controller.signal.aborted) {
          return
        }
        const message = err instanceof Error ? err.message : 'Unknown error'
        setError(message)
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false)
        }
      }
    }

    void loadProfile()

    return () => {
      controller.abort()
    }
  }, [getToken])

  const displayName = profile?.display_name || user?.fullName || user?.username || 'User'
  const displayEmail = profile?.email || user?.primaryEmailAddress?.emailAddress || 'Not set'
  const displayAvatarUrl = profile?.avatar_url || user?.imageUrl || null

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">Welcome to {appDisplayName}</CardTitle>
          <CardDescription>
            A clean, reusable SaaS shell ready for feature development.
          </CardDescription>
        </CardHeader>
      </Card>

      {loading && (
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Loading your profile...</p>
          </CardContent>
        </Card>
      )}

      {error && (
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-destructive">Error: {error}</p>
          </CardContent>
        </Card>
      )}

      {!loading && !error && (profile || user) && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Your Profile</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {displayAvatarUrl && (
              <img
                src={displayAvatarUrl}
                alt={displayName}
                className="h-16 w-16 rounded-full"
              />
            )}
            <div className="space-y-2 text-sm">
              <p>
                <span className="font-medium">Name:</span> {displayName}
              </p>
              <p>
                <span className="font-medium">Email:</span> {displayEmail}
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-28 rounded-md border border-dashed border-border bg-muted/40" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-28 rounded-md border border-dashed border-border bg-muted/40" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Insights</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-28 rounded-md border border-dashed border-border bg-muted/40" />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
