// این تایپ‌ها دقیقاً منطبق با خروجی سریالایزرهای Django REST Framework (فاز ۲) هستند.

export interface Tag {
  id: number
  name: string
  slug: string
}

export interface CategoryParentRef {
  id: number
  name: string
  slug: string
}

export interface CategoryMini {
  id: number
  name: string
  slug: string
  parent: CategoryParentRef | null
}

export interface Category {
  id: number
  name: string
  slug: string
  order: number
  children: Category[]
}

export interface ArticleListItem {
  id: number
  title: string
  slug: string
  image: string | null
  summary: string
  category: CategoryMini
  main_tags: Tag[]
  published_at: string
  reading_time_minutes: number
}

export interface ArticleFAQ {
  id: number
  question: string
  answer: string
}

export interface ArticleDetail extends ArticleListItem {
  body: string
  secondary_tags: Tag[]
  author_username: string | null
  views_count: number
  related_articles: ArticleListItem[]
  faqs: ArticleFAQ[]
}

export interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export type PriceSymbol = 'BTC' | 'ETH' | 'SOL' | 'USD' | 'GOLD18'
export type PriceCurrency = 'USD' | 'IRR'

export interface Price {
  symbol: PriceSymbol
  name_fa: string
  price_value: string
  currency: PriceCurrency
  change_percent: string
  is_positive_change: boolean
  updated_at: string
}

export interface SocialLink {
  id: number
  platform_name: string
  icon: string | null
  url: string
  order: number
}

export interface TopBanner {
  id: number
  image: string | null
  link_url: string
}

export interface Exchange {
  id: number
  name: string
  logo: string | null
  maker_fee: string
  taker_fee: string
  rating: string
  short_description: string
  registration_url: string
  order: number
}

export type EconomicEventImportance = 'high' | 'medium' | 'low'

export interface EconomicEvent {
  id: number
  title: string
  country: string
  importance: EconomicEventImportance
  event_date: string
  event_time: string | null
  shamsi_date: string
  day_name_fa: string
  actual: string
  forecast: string
  previous: string
}

export interface User {
  id: number
  username: string
  display_name: string
  email: string
  avatar: string | null
  is_email_verified: boolean
  date_joined: string
}

export interface CommentItem {
  id: number
  article: number
  display_name: string
  avatar: string | null
  parent: number | null
  body: string
  created_at: string
  is_owner: boolean
}

export interface AuthResponse {
  token: string
  user: User
}

export interface ApiFieldErrors {
  [field: string]: string[] | string
}
