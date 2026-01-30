import type { Metadata } from "next";
import { Crimson_Pro, Source_Sans_3 } from "next/font/google";
import { AppLayout } from "@/components/layout/app-layout";
import "./globals.css";

const crimson = Crimson_Pro({
  subsets: ["latin"],
  variable: "--font-heading",
  display: "swap",
});

const sourceSans = Source_Sans_3({
  subsets: ["latin"],
  variable: "--font-body",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Calibre Webapp",
  description: "Modern web interface for Calibre library management",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${crimson.variable} ${sourceSans.variable}`}>
      <body className="font-sans antialiased bg-slate-900 text-slate-100 min-h-screen">
        <AppLayout>{children}</AppLayout>
      </body>
    </html>
  );
}
