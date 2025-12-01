
// Shared types for authentication

export interface User {
  id: string;
  name: string;
  email: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegistrationData extends LoginCredentials {
  name: string;
}

export interface AuthResponse {
  token: string;
  user: User;
}
