'use client';

import { useRouter, useParams } from 'next/navigation';
import LoginForm from '@/shared/auth/components/LoginForm';

export default function LoginPage() {
  const router = useRouter();
  const params = useParams();
  const locale = params.locale as string;

  const handleLoginSuccess = () => {
    router.push(`/${locale}`);
    router.refresh();
  };

  const handleShowRegister = () => {
    router.push(`/${locale}/signup`);
  };

  const handleForgotPassword = () => {
    router.push(`/${locale}/forgot-password`);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <LoginForm 
        onLoginSuccess={handleLoginSuccess} 
        onShowRegister={handleShowRegister}
        onForgotPassword={handleForgotPassword}
      />
    </div>
  );
}
