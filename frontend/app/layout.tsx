import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import './globals.css'
import { Providers } from './providers'

const inter = Inter({ subsets: ['latin'] })

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

export default async function RootLayout({
  children,
  params: { locale }
}: {
  children: React.ReactNode
  params: { locale: string }
}) {
  const messages = await getMessages();

  return (
    <html lang={locale || 'en'} suppressHydrationWarning>
      <body className={inter.className}>
        <NextIntlClientProvider messages={messages}>
          <Providers>{children}</Providers>
        </NextIntlClientProvider>
      </body>
    </html>
  )
}