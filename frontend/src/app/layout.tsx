export const metadata = {
  title: 'Car Ads Platform',
  description: 'Plataforma de anúncios de veículos',
}

import { Providers } from '@/components/providers'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
