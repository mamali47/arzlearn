/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_MEDIA_BASE_URL: string
  readonly VITE_WS_BASE_URL: string
  readonly VITE_ADS_ENABLED: string
  readonly VITE_SITE_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
