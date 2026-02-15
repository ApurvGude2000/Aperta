// ABOUTME: API client for communicating with the FastAPI backend
// ABOUTME: Provides typed methods for all API endpoints

import axios from 'axios';
import type {
  ConversationCreate,
  ConversationUpdate,
  ConversationResponse,
  ConversationListItem,
  AnalysisResult,
  AskQuestionRequest,
  AskQuestionResponse,
  QASessionSummary,
  QASessionDetail,
  ExportFormat,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests if available
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth types
interface LoginRequest {
  email: string;
  password: string;
}

interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  full_name?: string;
  company?: string;
}

interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

interface UserResponse {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  company?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

interface LoginResponse {
  user: UserResponse;
  tokens: TokenResponse;
}

export const api = {
  // ============= Auth Endpoints =============

  // Login with email and password
  login: async (email: string, password: string): Promise<LoginResponse> => {
    const response = await client.post('/auth/login', { email, password });
    return response.data;
  },

  // Register a new user
  register: async (data: RegisterRequest): Promise<LoginResponse> => {
    const response = await client.post('/auth/register', data);
    return response.data;
  },

  // Get current user
  getCurrentUser: async (): Promise<UserResponse> => {
    const response = await client.get('/auth/me');
    return response.data;
  },

  // Logout (clear local storage)
  logout: () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },

  // ============= Conversation Endpoints =============

  // Get all conversations
  getConversations: async (): Promise<ConversationListItem[]> => {
    const response = await client.get('/conversations');
    return response.data;
  },

  // Get a specific conversation with full details
  getConversation: async (id: string): Promise<ConversationResponse> => {
    const response = await client.get(`/conversations/${id}`);
    return response.data;
  },

  // Create a new conversation
  createConversation: async (data: ConversationCreate): Promise<ConversationResponse> => {
    const response = await client.post('/conversations', data);
    return response.data;
  },

  // Update an existing conversation
  updateConversation: async (id: string, data: ConversationUpdate): Promise<ConversationResponse> => {
    const response = await client.put(`/conversations/${id}`, data);
    return response.data;
  },

  // Delete a conversation
  deleteConversation: async (id: string): Promise<void> => {
    await client.delete(`/conversations/${id}`);
  },

  // Analyze a conversation (runs agent analysis)
  analyzeConversation: async (id: string): Promise<AnalysisResult> => {
    const response = await client.post(`/conversations/${id}/analyze`);
    return response.data;
  },

  // Export a conversation in different formats
  exportConversation: async (id: string, format: ExportFormat): Promise<string> => {
    const response = await client.get(`/conversations/${id}/export`, {
      params: { format },
    });
    return response.data;
  },

  // ============= Q&A Endpoints =============

  // Ask a question (routes to appropriate agents)
  askQuestion: async (request: AskQuestionRequest): Promise<AskQuestionResponse> => {
    const response = await client.post('/qa/ask', request);
    return response.data;
  },

  // Get all Q&A sessions
  getQASessions: async (): Promise<QASessionSummary[]> => {
    const response = await client.get('/qa/sessions');
    return response.data;
  },

  // Get a specific Q&A session with all interactions
  getQASession: async (sessionId: string): Promise<QASessionDetail> => {
    const response = await client.get(`/qa/sessions/${sessionId}`);
    return response.data;
  },

  // Delete a Q&A session
  deleteQASession: async (sessionId: string): Promise<void> => {
    await client.delete(`/qa/sessions/${sessionId}`);
  },

  // ============= Dashboard Endpoints =============

  // Get dashboard metrics
  getDashboardMetrics: async (): Promise<any> => {
    const response = await client.get('/dashboard/metrics');
    return response.data;
  },

  // Get follow-up suggestions
  getFollowUpSuggestions: async (limit: number = 3): Promise<any> => {
    const response = await client.get('/dashboard/follow-ups', { params: { limit } });
    return response.data;
  },

  // ============= Health Check =============

  // Check if the API is healthy
  healthCheck: async (): Promise<{ status: string }> => {
    const response = await client.get('/health');
    return response.data;
  },
};

// Export the client for custom requests if needed
export default client;
