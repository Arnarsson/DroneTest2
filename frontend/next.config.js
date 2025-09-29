/** @type {import('next').NextConfig} */
const nextConfig = {
  rewrites: async () => {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NODE_ENV === 'development'
          ? 'http://127.0.0.1:8000/api/:path*'
          : '/api/:path*',
      },
    ]
  },
  images: {
    domains: ['unpkg.com'],
  },
  // Enable SWC minification for better performance
  swcMinify: true,
  // Optimize for production
  poweredByHeader: false,
  compress: true,
}

module.exports = nextConfig