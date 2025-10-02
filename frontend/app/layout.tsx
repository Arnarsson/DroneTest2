import type { Metadata } from 'next'
import './globals.css'
import { Providers } from './providers'

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL ?? 'https://www.dronemap.cc'),
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
}

export const viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}