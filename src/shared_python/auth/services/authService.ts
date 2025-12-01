
import { createClient } from '../../../web-frontend/src/lib/supabase/client';
import { User, AuthResponse, LoginCredentials, RegistrationData } from '../types';

export const authService = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const supabase = createClient();
    const { data, error } = await supabase.auth.signInWithPassword(credentials);

    if (error) {
      throw new Error(error.message);
    }

    if (!data.user || !data.session) {
        throw new Error('Login failed: No user or session data returned.');
    }

    return {
      token: data.session.access_token,
      user: {
        id: data.user.id,
        email: data.user.email || '',
        name: data.user.user_metadata.name || ''
      },
    };
  },

  register: async (registrationData: RegistrationData): Promise<AuthResponse> => {
    const supabase = createClient();
    const { data, error } = await supabase.auth.signUp({
        email: registrationData.email,
        password: registrationData.password,
        options: {
            data: {
                name: registrationData.name
            }
        }
    });

    if (error) {
      throw new Error(error.message);
    }

    if (!data.user || !data.session) {
        throw new Error('Registration failed: No user or session data returned.');
    }

    return {
        token: data.session.access_token,
        user: {
          id: data.user.id,
          email: data.user.email || '',
          name: data.user.user_metadata.name || ''
        },
      };
  },

  logout: async (): Promise<void> => {
    const supabase = createClient();
    const { error } = await supabase.auth.signOut();
    if (error) {
      throw new Error(error.message);
    }
  },

  getCurrentUser: async (): Promise<User | null> => {
    const supabase = createClient();
    const { data: { user } } = await supabase.auth.getUser();

    if (user) {
        return {
            id: user.id,
            email: user.email || '',
            name: user.user_metadata.name || ''
        }
    }
    return null;
  },
};
