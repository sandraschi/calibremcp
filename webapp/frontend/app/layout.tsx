import type { Metadata } from "next";
import "./globals.css";

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
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
