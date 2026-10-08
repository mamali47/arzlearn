import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { AuthProvider } from './context/AuthContext'
import { ThemeProvider } from './context/ThemeContext'
import './index.css'

// نکته: اینجا عمداً createRoot است، نه hydrateRoot. HTML ایستایی که
// generate_static_pages می‌سازد (div.pre) ساختار DOM ری‌اکت را ندارد؛ پس
// hydrate همیشه mismatch می‌دهد و ری‌اکت مجبور می‌شود همه چیز را دوباره
// رندر کند. createRoot محتوای ایستا را تمیز با نسخه‌ی تعاملی جایگزین می‌کند.
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          <App />
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  </React.StrictMode>
)
