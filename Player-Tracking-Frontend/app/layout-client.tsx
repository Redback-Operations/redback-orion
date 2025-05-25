'use client';

import { usePathname } from 'next/navigation';
import { SessionProvider } from "next-auth/react";
import { ThemeProvider } from '@/components/theme-provider';
import Navbar from '@/components/navbar';

export default function LayoutClient({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const hideNavbar = pathname === '/login' || pathname === '/signup';

  return (
    <SessionProvider>
      <ThemeProvider
        attribute="class"
        defaultTheme="system"
        enableSystem
        disableTransitionOnChange
      >
        {!hideNavbar && <Navbar />}
        {children}
      </ThemeProvider>
    </SessionProvider>
  );
}
