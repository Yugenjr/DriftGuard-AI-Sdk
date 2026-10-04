/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  async rewrites() {
    const backendUrl = process.env.DRIFTGUARD_API_URL || 'http://localhost:8000';
    return [
      {
        source: '/api-proxy/:path*',
        destination: `${backendUrl}/:path*`
      }
    ]
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  }
}
module.exports = nextConfig
