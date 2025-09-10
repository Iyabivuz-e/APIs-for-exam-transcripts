/**
 * Core TypeScript types for the application
 * 
 * Keep types simple and close to API responses
 * Senior tip: Mirror backend schemas for consistency
 */

// User-related types
export interface User {
  id: number;
  email: string;
  role: UserRole;
  created_at: string;
  updated_at: string;
}

export type UserRole = 'admin' | 'supervisor' | 'user';

// Authentication types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

// Exam-related types
export interface Exam {
  id: number;
  title: string;
  description?: string; // Optional since backend doesn't always include it
  date: string;
  created_at: string;
  updated_at: string;
}

export interface CreateExamData {
  title: string;
  date: string;
  // description removed since backend doesn't support it
}

export interface VoteAssignment {
  user_id: number;
  exam_id: number;
  vote: number;
}

export interface UserExam {
  user_id?: number; // Optional for backward compatibility
  exam_id: number;
  exam_title: string;
  exam_date: string;
  vote?: number;
  voted_at?: string;
  is_graded: boolean;
  grade_status: string;
  letter_grade: string;
  exam?: Exam; // Optional for backward compatibility
}

// API response types
export interface ApiResponse<T> {
  data?: T;
  error?: boolean;
  message?: string;
  status_code?: number;
}

// Pagination types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Form state types
export interface FormState {
  isLoading: boolean;
  error: string | null;
}

// Component prop types
export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
}
