import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

import { useTheme } from '@/lib/theme'
import { ProtectedLayout } from '@/components/auth/ProtectedLayout'
import { Account } from '@/components/pages/Account'
import { Home } from '@/components/pages/Home'
import { Settings } from '@/components/pages/Settings'
import { SignInPage } from '@/components/pages/SignIn'
import { SignUpPage } from '@/components/pages/SignUp'
import { SsoCallbackPage } from '@/components/pages/SsoCallback'

export default function App() {
  useTheme()

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/sign-in" element={<SignInPage />} />
        <Route path="/sign-up" element={<SignUpPage />} />
        <Route path="/sso-callback" element={<SsoCallbackPage />} />

        <Route element={<ProtectedLayout />}>
          <Route path="/" element={<Home />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/settings/account" element={<Account />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}