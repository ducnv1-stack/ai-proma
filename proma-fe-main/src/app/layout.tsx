import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import {MuiThemeProvider} from "../components/providers/MuiThemeProvider"
import { AppProvider } from '@/contexts/AppContext';
const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Famarex - AI Agent for Facebook Marketing",
  description: "Revolutionize your Facebook marketing with AI-powered automation and insights",
  keywords: "AI, Facebook Marketing, Automation, Social Media, Marketing Agent",
  authors: [{ name: "Famarex Team" }],
};

export const viewport = {
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
        suppressHydrationWarning
      >
        <AppProvider>
          <MuiThemeProvider>
            {children}
          </MuiThemeProvider>
        </AppProvider>
      </body>
    </html>
  );
}
