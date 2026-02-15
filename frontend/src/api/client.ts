// ABOUTME: API client for communicating with the FastAPI backend
// ABOUTME: Provides typed methods for all API endpoints

import axios from 'axios';
import type { Conversation, QuestionRequest, QuestionResponse, ImprovementSuggestion } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Get all conversations
  getConversations: async (): Promise<Conversation[]> => {
    const response = await client.get('/conversations');
    return response.data;
  },

  // Get a specific conversation
  getConversation: async (id: string): Promise<Conversation> => {
    const response = await client.get(`/conversations/${id}`);
    return response.data;
  },

  // Ask a question about a conversation
  askQuestion: async (request: QuestionRequest): Promise<QuestionResponse> => {
    const response = await client.post(
      `/conversations/${request.conversation_id}/question`,
      request
    );
    return response.data;
  },

  // Get improvement suggestions
  getImprovements: async (conversationId: string): Promise<ImprovementSuggestion[]> => {
    const response = await client.get(`/conversations/${conversationId}/improvements`);
    return response.data;
  },
};
