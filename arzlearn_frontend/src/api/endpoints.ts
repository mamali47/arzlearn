import apiClient from './client'
import type {
  ArticleDetail,
  ArticleListItem,
  AuthResponse,
  Category,
  CommentItem,
  EconomicEvent,
  Exchange,
  Paginated,
  Price,
  SocialLink,
  TopBanner,
  User,
} from './types'

// ---------------- accounts ----------------
export async function registerUser(payload: {
  username: string
  display_name: string
  email: string
  password: string
  password_confirm: string
}): Promise<AuthResponse> {
  const { data } = await apiClient.post<AuthResponse>('/accounts/register/', payload)
  return data
}

export async function loginUser(payload: {
  identifier: string
  password: string
}): Promise<AuthResponse> {
  const { data } = await apiClient.post<AuthResponse>('/accounts/login/', payload)
  return data
}

export async function logoutUser(): Promise<void> {
  await apiClient.post('/accounts/logout/')
}

export async function fetchMe(): Promise<User> {
  const { data } = await apiClient.get<User>('/accounts/me/')
  return data
}

// ---------------- articles ----------------
export async function fetchCategories(): Promise<Category[]> {
  const { data } = await apiClient.get<Category[]>('/articles/categories/')
  return data
}

export async function fetchCategoryArticles(
  slug: string,
  page = 1
): Promise<Paginated<ArticleListItem> & { category?: Category }> {
  const { data } = await apiClient.get(`/articles/categories/${slug}/`, {
    params: { page },
  })
  return data
}

export async function fetchLatestNews(): Promise<ArticleListItem[]> {
  const { data } = await apiClient.get<ArticleListItem[]>('/articles/latest-news/')
  return data
}

export async function fetchLatestAnalysis(): Promise<ArticleListItem[]> {
  const { data } = await apiClient.get<ArticleListItem[]>('/articles/latest-analysis/')
  return data
}

export async function searchArticles(query: string): Promise<Paginated<ArticleListItem>> {
  const { data } = await apiClient.get<Paginated<ArticleListItem>>('/articles/search/', {
    params: { q: query },
  })
  return data
}

export async function fetchArticleBySlug(slug: string): Promise<ArticleDetail> {
  const { data } = await apiClient.get<ArticleDetail>(`/articles/${slug}/`)
  return data
}

// ---------------- comments ----------------
export async function fetchComments(articleSlug: string): Promise<CommentItem[]> {
  const { data } = await apiClient.get<Paginated<CommentItem> | CommentItem[]>('/comments/', {
    params: { article: articleSlug },
  })
  return Array.isArray(data) ? data : data.results
}

export async function postComment(payload: {
  article: number
  body: string
  parent?: number | null
}): Promise<CommentItem> {
  const { data } = await apiClient.post<CommentItem>('/comments/', payload)
  return data
}

export async function updateComment(id: number, body: string): Promise<CommentItem> {
  const { data } = await apiClient.patch<CommentItem>(`/comments/${id}/`, { body })
  return data
}

export async function deleteComment(id: number): Promise<void> {
  await apiClient.delete(`/comments/${id}/`)
}

// ---------------- prices ----------------
export async function fetchPrices(): Promise<Price[]> {
  const { data } = await apiClient.get<Price[]>('/prices/')
  return data
}

// ---------------- socials ----------------
export async function fetchSocialLinks(): Promise<SocialLink[]> {
  const { data } = await apiClient.get<SocialLink[]>('/socials/')
  return data
}

// ---------------- exchanges ----------------
export async function fetchExchanges(): Promise<Exchange[]> {
  const { data } = await apiClient.get<Exchange[]>('/exchanges/')
  return data
}

// ---------------- economic calendar ----------------
export async function fetchTodayEconomicEvents(): Promise<EconomicEvent[]> {
  const { data } = await apiClient.get<EconomicEvent[]>('/economic-calendar/today/')
  return data
}

export async function fetchWeekEconomicEvents(): Promise<EconomicEvent[]> {
  const { data } = await apiClient.get<EconomicEvent[]>('/economic-calendar/week/')
  return data
}

// ---------------- top banner ----------------
export async function fetchActiveTopBanner(): Promise<TopBanner | null> {
  const { data } = await apiClient.get<TopBanner | null>('/topbanner/active/')
  return data
}
