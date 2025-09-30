import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'

const inter = Inter({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700', '800'],
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'DroneWatch - Real-time Drone Incident Tracking',
  description: 'Live tracking and verification of drone incidents across the Nordics with evidence-based reporting',
  keywords: 'drone, incidents, tracking, nordics, denmark, security, airports',
  authors: [{ name: 'DroneWatch' }],
  openGraph: {
    title: 'DroneWatch - Real-time Drone Incident Tracking',
    description: 'Live tracking and verification of drone incidents across the Nordics',
    type: 'website',
    locale: 'en_US',
    images: ['/og-image.png'],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'DroneWatch',
    description: 'Live tracking of drone incidents across the Nordics',
  },
  viewport: 'width=device-width, initial-scale=1, maximum-scale=5',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}