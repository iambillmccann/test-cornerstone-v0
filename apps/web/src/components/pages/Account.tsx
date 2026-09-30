import { useAuth, useClerk, useUser } from '@clerk/clerk-react'
import { useState } from 'react'
import { Navigate } from 'react-router-dom'

import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { appDisplayName } from '@/lib/branding'

export function Account() {
  const { isLoaded, isSignedIn } = useAuth()
  const { signOut } = useClerk()
  const { user, isLoaded: isUserLoaded } = useUser()
  const [isSigningOut, setIsSigningOut] = useState(false)

  if (!isLoaded || !isUserLoaded) {
    return (
      <div className="text-sm text-muted-foreground">
        Loading account details...
      </div>
    )
  }

  if (!isSignedIn || !user) {
    return <Navigate to="/sign-in" replace />
  }

  const fullName = user.fullName || user.username || 'Not set'
  const primaryEmail = user.primaryEmailAddress?.emailAddress || 'Not set'
  const avatarUrl = user.imageUrl

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">Account</CardTitle>
          <CardDescription>
            Manage your identity details connected to your {appDisplayName} workspace.
          </CardDescription>
        </CardHeader>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Identity</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {avatarUrl ? (
            <img
              src={avatarUrl}
              alt={fullName}
              className="h-16 w-16 rounded-full border border-border"
            />
          ) : null}

          <div className="space-y-2 text-sm">
            <p>
              <span className="font-medium text-foreground">Name:</span> {fullName}
            </p>
            <p>
              <span className="font-medium text-foreground">Email:</span> {primaryEmail}
            </p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Session</CardTitle>
          <CardDescription>Sign out from your current session.</CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            variant="outline"
            onClick={async () => {
              setIsSigningOut(true)
              try {
                await signOut({ redirectUrl: '/sign-in' })
              } finally {
                setIsSigningOut(false)
              }
            }}
            disabled={isSigningOut}
          >
            {isSigningOut ? 'Signing out...' : 'Sign out'}
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}