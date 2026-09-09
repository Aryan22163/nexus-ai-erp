import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NEXUS AI - AI-Native Business Operating System",
  description: "Enterprise ERP + CRM + Finance + Inventory + HR + Autonomous AI Copilot",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased bg-[#090d16] text-slate-100 flex flex-col min-h-screen">
        {children}
      </body>
    </html>
  );
}
