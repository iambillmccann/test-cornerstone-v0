import { useEffect, useState } from 'react'
import { appSlug } from '@/lib/branding'

type Theme = 'light' | 'dark' | 'system'

const LEGACY_THEME_STORAGE_KEY = 'cornerstone-theme'
const THEME_STORAGE_KEY = `${appSlug}-theme`

function getStoredTheme(): Theme | null {
  const current = localStorage.getItem(THEME_STORAGE_KEY) as Theme | null
  if (current) {
    return current
  }

  const legacy = localStorage.getItem(LEGACY_THEME_STORAGE_KEY) as Theme | null
  if (legacy) {
    localStorage.setItem(THEME_STORAGE_KEY, legacy)
    localStorage.removeItem(LEGACY_THEME_STORAGE_KEY)
  }

  return legacy
}

/**
 * Get the current system theme preference
 */
function getSystemTheme(): 'light' | 'dark' {
  if (typeof window === 'undefined') return 'light'
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

/**
 * Get the effective theme (resolves 'system' to actual light/dark)
 */
function getEffectiveTheme(theme: Theme): 'light' | 'dark' {
  if (theme === 'system') {
    return getSystemTheme()
  }
  return theme
}

/**
 * Apply theme to document
 */
function applyTheme(theme: Theme): void {
  const effectiveTheme = getEffectiveTheme(theme)
  const isDark = effectiveTheme === 'dark'

  if (isDark) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

/**
 * Hook for theme management
 * Initializes from localStorage or system preference, applies to document
 */
export function useTheme() {
  const [theme, setThemeState] = useState<Theme>(() => {
    // Initialize from localStorage or system preference (synchronously)
    const stored = getStoredTheme()
    const initialTheme = stored || 'system'
    applyTheme(initialTheme)
    return initialTheme
  })

  useEffect(() => {
    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')

    const handleChange = () => {
      if (theme === 'system') {
        applyTheme('system')
      }
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => {
      mediaQuery.removeEventListener('change', handleChange)
    }
  }, [theme])

  // Update DOM and localStorage when theme changes
  useEffect(() => {
    applyTheme(theme)
    localStorage.setItem(THEME_STORAGE_KEY, theme)
  }, [theme])

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme)
  }

  return {
    theme,
    setTheme,
  }
}

/**
 * Initialize theme system (call once at app startup)
 */
export function initializeTheme(): void {
  // Check for stored preference or use system default
  const stored = getStoredTheme()
  const theme = stored || 'system'
  applyTheme(theme)
}
