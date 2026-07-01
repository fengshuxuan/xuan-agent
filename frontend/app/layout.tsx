import "./globals.css";

export const metadata = {
  title: "Xuan Agent",
  description: "SaaS-ready agent assistant",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
