import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

// UPDATE FOR ACTUAL COMPANY
export const metadata: Metadata = {
  title: 'NimbusFlow Support | AI Customer Assistant',
  description: 'Get instant help with your NimbusFlow questions',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
