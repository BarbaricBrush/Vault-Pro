import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Vault Pro",
  description: "Next-generation financial dashboard",
  manifest: "/manifest.json",
  themeColor: "#0B0E14",
  viewport: "width=device-width, initial-scale=1, maximum-scale=1",
};

import { ThemeProvider } from "@/components/ThemeProvider";

// ... existing imports ...

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ThemeProvider>
          <div className="ambient-glow" />
          <div className="ambient-glow-2" />
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
