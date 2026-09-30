import { useState } from 'react'
import { Outlet } from 'react-router-dom'

import { useTheme } from '@/lib/theme'
import { Header } from './Header'
import { Navigation } from './Navigation'

export interface LayoutProps {
  children?: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)

  // Initialize theme infrastructure based on system preference
  useTheme()

  const toggleSidebar = () => {
    setIsSidebarOpen((current) => !current)
  }

  const closeSidebar = () => {
    setIsSidebarOpen(false)
  }

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-background text-foreground">
      {/* Fixed-height top header */}
      <Header isSidebarOpen={isSidebarOpen} onMenuToggle={toggleSidebar} />

      {/* Body row: sidebar + main fills remaining height */}
      <div className="flex flex-1 overflow-hidden">
        {isSidebarOpen ? (
          <button
            type="button"
            aria-label="Close navigation menu"
            className="fixed inset-0 top-14 z-20 bg-foreground/10 md:hidden"
            onClick={closeSidebar}
          />
        ) : null}

        {/* Left sidebar */}
        <Navigation isOpen={isSidebarOpen} onNavigate={closeSidebar} />

        {/* Main content panel */}
        <main className="flex-1 overflow-y-auto border border-border bg-muted/20 p-6">
          {children || <Outlet />}
        </main>
      </div>
    </div>
  )
}
