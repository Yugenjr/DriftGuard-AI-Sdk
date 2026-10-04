import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/sections/Footer";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });
const jetbrainsMono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono" });

export const metadata: Metadata = {
  title: "DriftGuard — Production AI Model Monitoring & Autonomous Retraining",
  description: "DriftGuard monitors production ML models, detects drift, tracks model health, and triggers configurable retraining workflows through a developer-first Python SDK.",
  openGraph: {
    title: "DriftGuard — Production AI Model Monitoring & Autonomous Retraining",
    description: "DriftGuard monitors production ML models, detects drift, tracks model health, and triggers configurable retraining workflows through a developer-first Python SDK.",
  }
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`scroll-smooth ${inter.variable} ${jetbrainsMono.variable}`}>
      <body>
        <Navbar />
        <main className="overflow-hidden pt-20">
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}
