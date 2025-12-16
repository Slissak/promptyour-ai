'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { LanguageSelector } from '@/components/layout/LanguageSelector';
import { UserMenu } from '@/components/auth/UserMenu';
import { createClient } from '@/lib/supabase/client';
import type { User } from '@/shared/auth/types';

interface HomeHeaderProps {
  locale: string;
  title: string;
}

export function HomeHeader({ locale, title }: HomeHeaderProps) {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const supabase = createClient();

    const checkAuth = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession();
        if (session?.user) {
            setCurrentUser({
                id: session.user.id,
                email: session.user.email || '',
                name: session.user.user_metadata.full_name || ''
            });
        } else {
            setCurrentUser(null);
        }
      } catch (error) {
        console.error('Error checking auth status:', error);
      } finally {
        setIsLoading(false);
      }
    };
    checkAuth();

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
        if (session?.user) {
            setCurrentUser({
                id: session.user.id,
                email: session.user.email || '',
                name: session.user.user_metadata.full_name || ''
            });
        } else {
            setCurrentUser(null);
        }
        setIsLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  return (
    <header className="flex justify-between items-center mb-8">
      <h1 className="text-3xl font-bold text-gray-900">
        {title}
      </h1>
      <div className="flex items-center gap-4">
        <LanguageSelector />
        {!isLoading && (
          currentUser ? (
            <UserMenu userEmail={currentUser.email || ''} />
          ) : (
            <Link
              href={`/${locale}/login`}
              className="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors"
            >
              Sign in
            </Link>
          )
        )}
      </div>
    </header>
  );
}
