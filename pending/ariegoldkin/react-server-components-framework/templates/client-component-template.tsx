// Client Component Template
'use client' // ⚠️ REQUIRED at the top of the file

import { useState, useEffect } from 'react'

/**
 * Client Component Example
 *
 * Characteristics:
 * - MUST have 'use client' directive
 * - Can use hooks (useState, useEffect, etc.)
 * - Can use browser APIs (window, document, etc.)
 * - Can handle interactivity (onClick, onChange, etc.)
 * - JavaScript IS sent to client (keep bundle small!)
 */

interface ClientComponentProps {
  initialData?: any[]
  onAction?: (data: any) => void
}

export function ClientComponentTemplate({ initialData = [], onAction }: ClientComponentProps) {
  // ✅ Can use React hooks
  const [state, setState] = useState(initialData)
  const [loading, setLoading] = useState(false)

  // ✅ Can use browser APIs
  useEffect(() => {
    // Access localStorage, window, document, etc.
    const stored = localStorage.getItem('key')
    if (stored) {
      setState(JSON.parse(stored))
    }
  }, [])

  // ✅ Handle user interactions
  const handleClick = async () => {
    setLoading(true)
    try {
      // Client-side data fetching
      const response = await fetch('/api/data')
      const data = await response.json()
      setState(data)
      onAction?.(data)
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2>Client Component</h2>

      {/* ✅ Interactive elements */}
      <button onClick={handleClick} disabled={loading}>
        {loading ? 'Loading...' : 'Click me'}
      </button>

      {/* ✅ Can render Server Components passed as children */}
      <div className="content">
        {state.map(item => (
          <div key={item.id}>{item.name}</div>
        ))}
      </div>
    </div>
  )
}

/**
 * Best Practices for Client Components:
 *
 * 1. Keep them small and focused
 * 2. Push 'use client' boundary as low as possible
 * 3. Prefer Server Components for data fetching
 * 4. Use for interactivity only (forms, animations, etc.)
 * 5. Avoid heavy dependencies (increases bundle size)
 */
