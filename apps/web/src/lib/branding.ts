const DEFAULT_APP_SLUG = 'cornerstone'
const DEFAULT_APP_DISPLAY_NAME = 'Cornerstone'
const DEFAULT_API_NAME = 'cornerstone-api'

export const appSlug = import.meta.env.VITE_APP_SLUG?.trim() || DEFAULT_APP_SLUG
export const appDisplayName =
  import.meta.env.VITE_APP_DISPLAY_NAME?.trim() || DEFAULT_APP_DISPLAY_NAME
export const appDescription =
  import.meta.env.VITE_APP_DESCRIPTION?.trim() || `${appDisplayName} SaaS template`
export const apiName = import.meta.env.VITE_API_NAME?.trim() || DEFAULT_API_NAME
