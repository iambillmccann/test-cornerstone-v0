import { SignedIn, SignedOut, useClerk, useUser } from '@clerk/clerk-react'
import { Bell, LogOut, Menu, Search, Settings, User, X } from 'lucide-react'
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { appDisplayName } from '@/lib/branding'
import { cn } from '@/lib/utils'

interface HeaderProps extends React.HTMLAttributes<HTMLElement> {
  isSidebarOpen?: boolean
  onMenuToggle?: () => void
}

export function Header({
  className,
  isSidebarOpen = false,
  onMenuToggle,
  ...props
}: HeaderProps) {
  const { signOut } = useClerk()
  const { user } = useUser()
  const [isSigningOut, setIsSigningOut] = useState(false)
  const signedOutRedirectUrl = '/sign-in'

  const avatarFallback = useMemo(() => {
    const firstInitial = user?.firstName?.trim().charAt(0)
    const lastInitial = user?.lastName?.trim().charAt(0)

    if (firstInitial || lastInitial) {
      return `${firstInitial ?? ''}${lastInitial ?? ''}`.toUpperCase()
    }

    const fullNameParts = user?.fullName?.trim().split(/\s+/).filter(Boolean) ?? []
    const initialsFromFullName = fullNameParts.slice(0, 2).map((part) => part.charAt(0)).join('')

    return initialsFromFullName.toUpperCase()
  }, [user?.firstName, user?.fullName, user?.lastName])

  const avatarLabel = user?.fullName ?? user?.primaryEmailAddress?.emailAddress ?? 'Account menu'

  async function handleSignOut() {
    if (isSigningOut) {
      return
    }

    setIsSigningOut(true)
    try {
      await signOut({ redirectUrl: signedOutRedirectUrl })
    } finally {
      setIsSigningOut(false)
    }
  }

  return (
    <header
      className={cn(
        'flex h-14 shrink-0 items-center justify-between border border-border bg-background px-4',
        className
      )}
      {...props}
    >
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden"
          aria-label={isSidebarOpen ? 'Close navigation menu' : 'Open navigation menu'}
          aria-expanded={isSidebarOpen}
          onClick={onMenuToggle}
        >
          {isSidebarOpen ? <X className="size-4" /> : <Menu className="size-4" />}
        </Button>
        <div className="size-7 rounded-md bg-primary/10" aria-hidden="true" />
        <h1 className="text-sm font-semibold tracking-wide text-foreground">{appDisplayName}</h1>
      </div>
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon" className="hidden sm:inline-flex" aria-label="Search">
          <Search className="size-4" />
        </Button>
        <Button variant="ghost" size="icon" className="hidden sm:inline-flex" aria-label="Notifications">
          <Bell className="size-4" />
        </Button>
        <SignedOut>
          <Button variant="outline" size="sm" className="ml-1 px-3 text-xs" asChild>
            <Link to="/sign-in">Sign in</Link>
          </Button>
        </SignedOut>
        <SignedIn>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="ml-2 size-10 rounded-full"
                aria-label={avatarLabel}
              >
                <Avatar className="size-8 border border-border/80">
                  {user?.imageUrl ? (
                    <AvatarImage src={user.imageUrl} alt={avatarLabel} />
                  ) : null}
                  <AvatarFallback className="bg-muted text-xs font-medium text-foreground">
                    {avatarFallback ? (
                      avatarFallback
                    ) : (
                      <User className="size-4 text-muted-foreground" aria-hidden="true" />
                    )}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-52" sideOffset={8}>
              <DropdownMenuLabel className="truncate">{avatarLabel}</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                <Link to="/settings" className="flex items-center gap-2">
                  <Settings className="size-4" />
                  Settings
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link to="/settings/account" className="flex items-center gap-2">
                  <User className="size-4" />
                  Account
                </Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                className="text-destructive focus:text-destructive"
                onSelect={(event) => {
                  event.preventDefault()
                  void handleSignOut()
                }}
                disabled={isSigningOut}
              >
                <LogOut className="size-4" />
                {isSigningOut ? 'Signing out...' : 'Sign out'}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </SignedIn>
      </div>
    </header>
  )
}
