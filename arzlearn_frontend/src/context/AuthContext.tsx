import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { fetchMe, loginUser, logoutUser, registerUser } from '../api/endpoints'
import { TOKEN_STORAGE_KEY } from '../api/client'
import type { User } from '../api/types'

interface AuthContextValue {
  user: User | null
  isLoading: boolean
  login: (identifier: string, password: string) => Promise<void>
  register: (
    username: string,
    displayName: string,
    email: string,
    password: string,
    passwordConfirm: string
  ) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem(TOKEN_STORAGE_KEY)
    if (!token) {
      setIsLoading(false)
      return
    }
    fetchMe()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem(TOKEN_STORAGE_KEY)
        setUser(null)
      })
      .finally(() => setIsLoading(false))
  }, [])

  async function login(identifier: string, password: string) {
    const data = await loginUser({ identifier, password })
    localStorage.setItem(TOKEN_STORAGE_KEY, data.token)
    setUser(data.user)
  }

  async function register(
    username: string,
    displayName: string,
    email: string,
    password: string,
    passwordConfirm: string
  ) {
    const data = await registerUser({
      username,
      display_name: displayName,
      email,
      password,
      password_confirm: passwordConfirm,
    })
    localStorage.setItem(TOKEN_STORAGE_KEY, data.token)
    setUser(data.user)
  }

  async function logout() {
    try {
      await logoutUser()
    } finally {
      localStorage.removeItem(TOKEN_STORAGE_KEY)
      setUser(null)
    }
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth باید داخل AuthProvider استفاده شود.')
  }
  return context
}
