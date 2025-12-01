'use client';

import { useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import RegistrationForm from '@/shared/auth/components/RegistrationForm';

export default function SignupPage() {
  const router = useRouter();
  const params = useParams();
  const locale = params.locale as string;
  const [isSuccess, setIsSuccess] = useState(false);

  const handleRegisterSuccess = () => {
    setIsSuccess(true);
    // Optionally redirect after a delay
    setTimeout(() => {
        router.push(`/${locale}/login`);
    }, 3000);
  };

  const handleShowLogin = () => {
    router.push(`/${locale}/login`);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <RegistrationForm 
            onRegisterSuccess={handleRegisterSuccess} 
            onShowLogin={handleShowLogin}
        />
    </div>
  );
}
