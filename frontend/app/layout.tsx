import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BandarAI — meja riset saham",
  description: "Riset saham BEI dengan sumber, waktu data, dan batas bukti yang jelas.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="id"><body>{children}</body></html>;
}
