import { AxiosError } from 'axios'
import type { ApiFieldErrors } from '../api/types'

/**
 * تبدیل خطاهای DRF (که معمولاً بصورت { field: ["پیام خطا"] } یا { detail: "..." } برمی‌گردند)
 * به یک شیء ساده field -> پیام فارسی، برای نمایش زیر هر فیلد فرم.
 */
export function parseApiErrors(error: unknown): { general?: string; fields: Record<string, string> } {
  const fields: Record<string, string> = {}

  if (error instanceof AxiosError && error.response?.data) {
    const rawData = error.response.data

    // اگر پاسخ JSON نبود (مثلاً یک صفحه‌ی خطای HTML خام از سمت سرور)، تلاش برای
    // پردازش field-by-field انجام نشود؛ چون Object.entries روی یک رشته، آن را
    // کاراکتر به کاراکتر می‌شکافد و یک پیام خطای بی‌معنی (مثل یک کاراکتر تنها) نشان می‌دهد.
    if (typeof rawData !== 'object' || rawData === null) {
      const status = error.response.status
      return {
        general:
          status >= 500
            ? 'خطای سرور رخ داد (کد 500). لطفاً بعداً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.'
            : 'خطایی رخ داد. لطفاً دوباره تلاش کنید.',
        fields,
      }
    }

    const data = rawData as ApiFieldErrors & { detail?: string; non_field_errors?: string[] }

    if (data.detail) {
      return { general: data.detail, fields }
    }

    if (data.non_field_errors) {
      return {
        general: Array.isArray(data.non_field_errors) ? data.non_field_errors[0] : data.non_field_errors,
        fields,
      }
    }

    Object.entries(data).forEach(([key, value]) => {
      fields[key] = Array.isArray(value) ? value[0] : String(value)
    })

    if (Object.keys(fields).length > 0) {
      return { fields }
    }
  }

  return { general: 'خطایی رخ داد. لطفاً دوباره تلاش کنید.', fields }
}

export function formatDatePersian(isoDate: string): string {
  try {
    return new Intl.DateTimeFormat('fa-IR-u-ca-persian', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    }).format(new Date(isoDate))
  } catch {
    return isoDate
  }
}

export function formatNumber(value: string | number): string {
  const num = typeof value === 'string' ? Number(value) : value
  if (Number.isNaN(num)) return String(value)
  return new Intl.NumberFormat('en-US').format(num)
}
