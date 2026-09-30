import { useAuth, useSignIn } from '@clerk/clerk-react'
import { useState, type FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'

import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { appDisplayName } from '@/lib/branding'

function getClerkErrorMessage(error: unknown): string {
  if (typeof error === 'object' && error !== null) {
    const maybeError = error as {
      errors?: Array<{ longMessage?: string; message?: string }>
      message?: string
    }
    const firstError = maybeError.errors?.[0]
    if (firstError?.longMessage) {
      return firstError.longMessage
    }
    if (firstError?.message) {
      return firstError.message
    }
    if (maybeError.message) {
      return maybeError.message
    }
  }

  return 'Unable to sign in. Please verify your credentials and try again.'
}

export function SignInPage() {
  const { isLoaded, isSignedIn } = useAuth()
  const { signIn, setActive, isLoaded: isSignInLoaded } = useSignIn()
  const navigate = useNavigate()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [oauthProviderLoading, setOauthProviderLoading] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  if (!isLoaded) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-muted/20 p-6 text-sm text-muted-foreground">
        Loading session...
      </div>
    )
  }

  if (isSignedIn) {
    return <Navigate to="/" replace />
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!isSignInLoaded || !signIn || !setActive) {
      setError('Sign-in is still initializing. Please wait and try again.')
      return
    }

    setIsSubmitting(true)
    setError(null)

    try {
      const result = await signIn.create({
        identifier: email,
        password,
      })

      if (result.status === 'complete') {
        await setActive({ session: result.createdSessionId })
        navigate('/', { replace: true })
        return
      }

      setError('Sign-in requires additional steps that are not enabled in this UI flow.')
    } catch (submitError) {
      setError(getClerkErrorMessage(submitError))
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleOAuthSignIn(strategy: 'oauth_google' | 'oauth_apple' | 'oauth_microsoft') {
    if (!isSignInLoaded || !signIn) {
      setError('Sign-in is still initializing. Please wait and try again.')
      return
    }

    setError(null)
    setOauthProviderLoading(strategy)

    try {
      const redirectUrl = `${window.location.origin}/sso-callback`
      const redirectUrlComplete = `${window.location.origin}/`

      await signIn.authenticateWithRedirect({
        strategy,
        redirectUrl,
        redirectUrlComplete,
      })
    } catch (oauthError) {
      setError(getClerkErrorMessage(oauthError))
      setOauthProviderLoading(null)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/20 p-6">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-xl">Sign in to {appDisplayName}</CardTitle>
          <CardDescription>
            Enter your email and password to continue to your workspace.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form className="space-y-4" onSubmit={handleSubmit}>
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium text-foreground">
                Email
              </label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                className="flex h-9 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none ring-offset-background placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-2 focus-visible:ring-ring/50"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium text-foreground">
                Password
              </label>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="flex h-9 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none ring-offset-background placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-2 focus-visible:ring-ring/50"
              />
            </div>

            {error ? <p className="text-sm text-destructive">{error}</p> : null}

            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? 'Signing in...' : 'Sign in'}
            </Button>
          </form>

          <div className="my-4 flex items-center gap-3">
            <span className="h-px flex-1 bg-border" />
            <span className="text-xs uppercase tracking-wide text-muted-foreground">Or continue with</span>
            <span className="h-px flex-1 bg-border" />
          </div>

          <div className="grid gap-2 sm:grid-cols-3">
            <Button
              type="button"
              variant="outline"
              disabled={Boolean(oauthProviderLoading)}
              onClick={() => {
                void handleOAuthSignIn('oauth_google')
              }}
            >
              {oauthProviderLoading === 'oauth_google' ? 'Loading...' : 'Google'}
            </Button>
            <Button
              type="button"
              variant="outline"
              disabled={Boolean(oauthProviderLoading)}
              onClick={() => {
                void handleOAuthSignIn('oauth_apple')
              }}
            >
              {oauthProviderLoading === 'oauth_apple' ? 'Loading...' : 'Apple'}
            </Button>
            <Button
              type="button"
              variant="outline"
              disabled={Boolean(oauthProviderLoading)}
              onClick={() => {
                void handleOAuthSignIn('oauth_microsoft')
              }}
            >
              {oauthProviderLoading === 'oauth_microsoft' ? 'Loading...' : 'Microsoft'}
            </Button>
          </div>

          <p className="mt-4 text-sm text-muted-foreground">
            Need an account?{' '}
            <Link to="/sign-up" className="font-medium text-foreground underline underline-offset-4">
              Create one
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
