import { useLocation, Link } from 'react-router-dom'
import { Home } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface NavigationProps extends React.HTMLAttributes<HTMLElement> {
  isOpen?: boolean
  onNavigate?: () => void
}

export function Navigation({
  className,
  isOpen = false,
  onNavigate,
  ...props
}: NavigationProps) {
  const location = useLocation()

  const navItems = [
    { label: 'Home', href: '/', icon: Home },
  ]

  const isActivePath = (href: string) => location.pathname === href

  return (
    <nav
      className={cn(
        'fixed inset-y-14 left-0 z-30 flex w-60 shrink-0 flex-col overflow-y-auto border border-border bg-sidebar transition-transform duration-200 md:static md:inset-auto md:translate-x-0',
        isOpen ? 'translate-x-0' : '-translate-x-full',
        className
      )}
      {...props}
    >
      <div className="p-3">
        <p className="px-2 py-2 text-xs font-semibold uppercase tracking-wide text-foreground">
          Navigation
        </p>
        <ul className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = isActivePath(item.href)

            return (
              <li key={item.label}>
                <Button
                  asChild
                  variant="ghost"
                  className={cn(
                    'h-9 w-full justify-start gap-2.5 rounded-md px-2.5 text-sm text-muted-foreground',
                    isActive && 'bg-accent text-foreground hover:bg-accent'
                  )}
                >
                  <Link to={item.href} onClick={onNavigate}>
                    <Icon
                      className={cn(
                        'size-4 text-muted-foreground',
                        isActive && 'text-foreground'
                      )}
                    />
                    <span>{item.label}</span>
                  </Link>
                </Button>
              </li>
            )
          })}
        </ul>
      </div>
    </nav>
  )
}
