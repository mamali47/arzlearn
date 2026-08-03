import { useEffect, useRef, useState } from 'react'
import { fetchPrices } from '../api/endpoints'
import type { Price } from '../api/types'

const WS_BASE_URL =
  import.meta.env.VITE_WS_BASE_URL ||
  `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}`

const WS_URL = `${WS_BASE_URL}/ws/prices/`
const PING_INTERVAL_MS = 20000
const RECONNECT_BASE_DELAY_MS = 1000
const RECONNECT_MAX_DELAY_MS = 15000

interface PriceSocketMessage {
  type: 'snapshot' | 'update'
  prices: Price[]
}

/**
 * قیمت‌ها را از طریق WebSocket (ws/prices/) بصورت لحظه‌ای دریافت می‌کند
 * (بجای polling در فاز ۳). با قطع اتصال، بصورت خودکار با تاخیر فزاینده
 * دوباره وصل می‌شود؛ در همین حین، آخرین مقادیر دریافتی حفظ می‌شوند.
 */
export function usePrices() {
  const [prices, setPrices] = useState<Price[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isConnected, setIsConnected] = useState(false)

  const socketRef = useRef<WebSocket | null>(null)
  const reconnectTimerRef = useRef<number | null>(null)
  const pingTimerRef = useRef<number | null>(null)
  const reconnectAttemptRef = useRef(0)
  const isUnmountedRef = useRef(false)

  useEffect(() => {
    isUnmountedRef.current = false

    // دریافت اولیه از طریق REST برای نمایش فوری، تا WebSocket وصل شود
    fetchPrices()
      .then((data) => {
        if (!isUnmountedRef.current) {
          setPrices(data)
          setIsLoading(false)
        }
      })
      .catch(() => {
        /* در صورت خطا، منتظر اسنپ‌شات WebSocket می‌مانیم */
      })

    connect()

    return () => {
      isUnmountedRef.current = true
      cleanup()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function connect() {
    cleanupSocket()

    const socket = new WebSocket(WS_URL)
    socketRef.current = socket

    socket.onopen = () => {
      if (isUnmountedRef.current) return
      reconnectAttemptRef.current = 0
      setIsConnected(true)

      pingTimerRef.current = window.setInterval(() => {
        if (socket.readyState === WebSocket.OPEN) socket.send('ping')
      }, PING_INTERVAL_MS)
    }

    socket.onmessage = (event) => {
      if (event.data === 'pong') return
      try {
        const message: PriceSocketMessage = JSON.parse(event.data)
        if (message.prices) {
          setPrices(message.prices)
          setIsLoading(false)
        }
      } catch {
        // پیام ناشناخته را نادیده می‌گیریم
      }
    }

    socket.onclose = () => {
      if (isUnmountedRef.current) return
      setIsConnected(false)
      if (pingTimerRef.current) window.clearInterval(pingTimerRef.current)
      scheduleReconnect()
    }

    socket.onerror = () => {
      socket.close()
    }
  }

  function scheduleReconnect() {
    const attempt = reconnectAttemptRef.current + 1
    reconnectAttemptRef.current = attempt
    const delay = Math.min(RECONNECT_BASE_DELAY_MS * 2 ** (attempt - 1), RECONNECT_MAX_DELAY_MS)

    reconnectTimerRef.current = window.setTimeout(() => {
      if (!isUnmountedRef.current) connect()
    }, delay)
  }

  function cleanupSocket() {
    if (socketRef.current) {
      socketRef.current.onopen = null
      socketRef.current.onmessage = null
      socketRef.current.onclose = null
      socketRef.current.onerror = null
      socketRef.current.close()
      socketRef.current = null
    }
    if (pingTimerRef.current) {
      window.clearInterval(pingTimerRef.current)
      pingTimerRef.current = null
    }
  }

  function cleanup() {
    if (reconnectTimerRef.current) window.clearTimeout(reconnectTimerRef.current)
    cleanupSocket()
  }

  return { prices, isLoading, isConnected }
}
