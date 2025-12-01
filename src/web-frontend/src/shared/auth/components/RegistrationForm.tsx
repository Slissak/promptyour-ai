'use client';

import React, { useState } from 'react';
import { authService } from '../services/authService';
import { RegistrationData } from '../types/index';

interface RegistrationFormProps {
  onRegisterSuccess: () => void;
  onShowLogin?: () => void;
}

const RegistrationForm: React.FC<RegistrationFormProps> = ({ onRegisterSuccess, onShowLogin }) => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      setIsLoading(false);
      return;
    }

    try {
      await authService.register({ name, email, password });
      setSuccess(true);
      onRegisterSuccess();
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-md w-full space-y-8">
      <div>
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Create your account
        </h2>
        {onShowLogin && (
            <p className="mt-2 text-center text-sm text-gray-600">
                Or{' '}
                <button onClick={onShowLogin} className="font-medium text-primary-600 hover:text-primary-500">
                sign in to existing account
                </button>
            </p>
        )}
      </div>

      <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
        {error && (
          <div className="rounded-md bg-red-50 p-4">
            <p className="text-sm font-medium text-red-800">{error}</p>
          </div>
        )}
        {success && (
            <div className="rounded-md bg-green-50 p-4">
                <h3 className="text-sm font-medium text-green-800 mb-2">
                ✅ Account created successfully!
                </h3>
                <p className="text-sm text-green-700">
                📧 Please check your email inbox for a confirmation link.
                </p>
            </div>
        )}

        <div className="rounded-md shadow-sm space-y-3">
            <div>
                <label htmlFor="name" className="sr-only">Name</label>
                <input
                    id="name"
                    name="name"
                    type="text"
                    required
                    className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
                    placeholder="Your Name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    disabled={isLoading || success}
                />
            </div>
            <div>
                <label htmlFor="email-address" className="sr-only">Email address</label>
                <input
                    id="email-address"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
                    placeholder="Email address"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    disabled={isLoading || success}
                />
            </div>
            <div>
                <label htmlFor="password" className="sr-only">Password</label>
                <input
                    id="password"
                    name="password"
                    type="password"
                    autoComplete="new-password"
                    required
                    className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
                    placeholder="Password (min. 6 characters)"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    disabled={isLoading || success}
                />
            </div>
            <div>
                <label htmlFor="confirm-password" className="sr-only">Confirm Password</label>
                <input
                    id="confirm-password"
                    name="confirm-password"
                    type="password"
                    autoComplete="new-password"
                    required
                    className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
                    placeholder="Confirm password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    disabled={isLoading || success}
                />
            </div>
        </div>

        <div>
          <button
            type="submit"
            disabled={isLoading || success}
            className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Creating account...' : success ? 'Account created!' : 'Create account'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default RegistrationForm;
