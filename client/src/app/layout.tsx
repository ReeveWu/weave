import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Weave — PDF to Study Notes",
  description: "Upload PDFs and let AI weave them into structured study handouts.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-TW" className="h-full antialiased">
      <body className="min-h-full flex flex-col bg-background text-foreground">
        {children}
      </body>
    </html>
  );
}
