import { useAuth, useSignIn, useSignUp } from '@clerk/clerk-react'
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

  return 'Unable to create account. Please review your details and try again.'
}

export function SignUpPage() {
  const { isLoaded, isSignedIn } = useAuth()
  const { signIn, isLoaded: isSignInLoaded } = useSignIn()
  const { signUp, setActive, isLoaded: isSignUpLoaded } = useSignUp()
  const navigate = useNavigate()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [verificationCode, setVerificationCode] = useState('')
  const [isAwaitingVerification, setIsAwaitingVerification] = useState(false)
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

    if (!isSignUpLoaded || !signUp || !setActive) {
      setError('Sign-up is still initializing. Please wait and try again.')
      return
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }

    setIsSubmitting(true)
    setError(null)

    try {
      const result = await signUp.create({
        emailAddress: email,
        password,
      })

      if (result.status === 'complete') {
        await setActive({ session: result.createdSessionId })
        navigate('/', { replace: true })
        return
      }

      await signUp.prepareEmailAddressVerification({ strategy: 'email_code' })
      setIsAwaitingVerification(true)
    } catch (submitError) {
      setError(getClerkErrorMessage(submitError))
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleVerificationSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!isSignUpLoaded || !signUp || !setActive) {
      setError('Verification is still initializing. Please wait and try again.')
      return
    }

    setIsSubmitting(true)
    setError(null)

    try {
      const result = await signUp.attemptEmailAddressVerification({
        code: verificationCode,
      })

      if (result.status === 'complete') {
        await setActive({ session: result.createdSessionId })
        navigate('/', { replace: true })
        return
      }

      setError('Verification is not complete yet. Please try a fresh code.')
    } catch (submitError) {
      setError(getClerkErrorMessage(submitError))
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleOAuthSignUp(strategy: 'oauth_google' | 'oauth_apple' | 'oauth_microsoft') {
    if (!isSignInLoaded || !signIn) {
      setError('Sign-up is still initializing. Please wait and try again.')
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
          <CardTitle className="text-xl">Create your {appDisplayName} account</CardTitle>
          <CardDescription>
            {isAwaitingVerification
              ? 'Enter the verification code sent to your email to activate your account.'
              : 'Sign up with email and password to access your workspace.'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isAwaitingVerification ? (
            <form className="space-y-4" onSubmit={handleVerificationSubmit}>
              <div className="space-y-2">
                <label htmlFor="verification-code" className="text-sm font-medium text-foreground">
                  Verification code
                </label>
                <input
                  id="verification-code"
                  type="text"
                  inputMode="numeric"
                  autoComplete="one-time-code"
                  required
                  value={verificationCode}
                  onChange={(event) => setVerificationCode(event.target.value)}
                  className="flex h-9 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none ring-offset-background placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-2 focus-visible:ring-ring/50"
                />
              </div>

              {error ? <p className="text-sm text-destructive">{error}</p> : null}

              <Button type="submit" className="w-full" disabled={isSubmitting}>
                {isSubmitting ? 'Verifying...' : 'Verify email'}
              </Button>
            </form>
          ) : (
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
                  autoComplete="new-password"
                  required
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  className="flex h-9 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none ring-offset-background placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-2 focus-visible:ring-ring/50"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="confirm-password" className="text-sm font-medium text-foreground">
                  Confirm password
                </label>
                <input
                  id="confirm-password"
                  type="password"
                  autoComplete="new-password"
                  required
                  value={confirmPassword}
                  onChange={(event) => setConfirmPassword(event.target.value)}
                  className="flex h-9 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none ring-offset-background placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-2 focus-visible:ring-ring/50"
                />
              </div>

              {error ? <p className="text-sm text-destructive">{error}</p> : null}

              <Button type="submit" className="w-full" disabled={isSubmitting}>
                {isSubmitting ? 'Creating account...' : 'Create account'}
              </Button>
            </form>
          )}

          {!isAwaitingVerification ? (
            <>
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
                    void handleOAuthSignUp('oauth_google')
                  }}
                >
                  {oauthProviderLoading === 'oauth_google' ? 'Loading...' : 'Google'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  disabled={Boolean(oauthProviderLoading)}
                  onClick={() => {
                    void handleOAuthSignUp('oauth_apple')
                  }}
                >
                  {oauthProviderLoading === 'oauth_apple' ? 'Loading...' : 'Apple'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  disabled={Boolean(oauthProviderLoading)}
                  onClick={() => {
                    void handleOAuthSignUp('oauth_microsoft')
                  }}
                >
                  {oauthProviderLoading === 'oauth_microsoft' ? 'Loading...' : 'Microsoft'}
                </Button>
              </div>
            </>
          ) : null}

          <p className="mt-4 text-sm text-muted-foreground">
            Already have an account?{' '}
            <Link to="/sign-in" className="font-medium text-foreground underline underline-offset-4">
              Sign in
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
