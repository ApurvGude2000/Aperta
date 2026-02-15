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

export const api = {
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

  // ============= Health Check =============

  // Check if the API is healthy
  healthCheck: async (): Promise<{ status: string }> => {
    const response = await client.get('/health');
    return response.data;
  },
};

// Export the client for custom requests if needed
export default client;
