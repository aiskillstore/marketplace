'use client'

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div className="rounded border border-red-200 bg-red-50 p-4">
      <p className="font-medium text-red-800">{error.message}</p>
      <button
        onClick={() => reset()}
        className="mt-2 rounded border border-red-300 px-3 py-1 text-sm"
      >
        Try again
      </button>
    </div>
  )
}
