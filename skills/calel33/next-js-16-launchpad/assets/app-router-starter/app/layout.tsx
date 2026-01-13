export const metadata = {
  title: 'Next.js 16 Starter',
  description: 'Turbopack + Cache Components baseline layout',
}

export default function RootLayout({
  children,
  modal,
}: {
  children: React.ReactNode
  modal?: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen bg-gray-50 text-gray-900">
        <div className="mx-auto flex max-w-4xl flex-col gap-6 p-6">
          <header className="flex flex-col gap-2">
            <p className="text-sm uppercase tracking-wide text-gray-500">
              Next.js 16 Reference Shell
            </p>
            <h1 className="text-3xl font-semibold">Next.js 16 Launchpad</h1>
          </header>
          <main>{children}</main>
        </div>
        {modal}
      </body>
    </html>
  )
}
