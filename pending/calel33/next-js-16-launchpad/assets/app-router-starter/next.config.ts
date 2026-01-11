import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  cacheComponents: true,
  reactCompiler: true,
  images: {
    localPatterns: [
      {
        pathname: '/assets/**',
        search: '?v=*',
      },
    ],
  },
}

export default nextConfig
