/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['unpkg.com'],
  },
  // Enable SWC minification for better performance
  swcMinify: true,
  // Optimize for production
  poweredByHeader: false,
  compress: true,
}