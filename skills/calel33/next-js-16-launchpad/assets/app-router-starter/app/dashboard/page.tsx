import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import { Suspense } from 'react'

async function loadStats() {
  const res = await fetch('https://jsonplaceholder.typicode.com/todos?_limit=5', {
    cache: 'no-store',
  })
  return res.json()
}

async function StatsPanel() {
  const stats = await loadStats()
  return (
    <ul className="space-y-2">
      {stats.map((item: { id: number; title: string }) => (
        <li key={item.id} className="rounded border border-gray-200 p-3">
          {item.title}
        </li>
      ))}
    </ul>
  )
}

export default async function DashboardPage() {
  const session = (await cookies()).get('auth-token')?.value
  if (!session) {
    redirect('/login')
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold">Dashboard</h2>
      <Suspense fallback={<p className="text-gray-500">Loading stats...</p>}>
        <StatsPanel />
      </Suspense>
    </div>
  )
}
