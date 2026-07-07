import type { Metadata } from "next";

import Navbar from "@/components/Navbar";
import { DemoModeBanner } from "@/components/system";

import "@xyflow/react/dist/style.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "PlantMind AI",
  description: "Industrial Asset Intelligence Dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        <DemoModeBanner />
        {children}
      </body>
    </html>
  );
}