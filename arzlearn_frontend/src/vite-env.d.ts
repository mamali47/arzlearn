/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_MEDIA_BASE_URL: string
  readonly VITE_WS_BASE_URL: string
  readonly VITE_ADS_ENABLED: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
