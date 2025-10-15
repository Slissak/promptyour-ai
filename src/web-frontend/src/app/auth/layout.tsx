import '../globals.css';

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="font-english">
        {children}
      </body>
    </html>
  );
}
