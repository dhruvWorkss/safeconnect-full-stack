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
  metadataBase: new URL(process.env.SITE_URL || "http://localhost:3000"),
  title: "SafeConnect — Trust & Safety Operations",
  description: "A modern command center for moderation teams to investigate risk, protect communities, and act with confidence.",
  openGraph: {
    title: "SafeConnect — Trust & Safety Operations",
    description: "Trust & Safety, in command.",
    images: [{ url: "/og.png", width: 1680, height: 941, alt: "SafeConnect trust and safety command center" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "SafeConnect — Trust & Safety Operations",
    description: "Trust & Safety, in command.",
    images: ["/og.png"],
  },
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
