import { AuthenticateWithRedirectCallback } from '@clerk/clerk-react'

export function SsoCallbackPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/20 p-6 text-sm text-muted-foreground">
      <AuthenticateWithRedirectCallback signInForceRedirectUrl="/" signUpForceRedirectUrl="/" />
    </div>
  )
}