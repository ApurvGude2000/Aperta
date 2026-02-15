// ABOUTME: TypeScript type definitions for the web app
// ABOUTME: Matches the data models from the iOS app and backend API

export interface TranscriptSegment {
  id: string;
  text: string;
  timestamp: string;
  speaker_id?: string;
  confidence: number;
}

export interface Conversation {
  id: string;
  title: string;
  transcript: string;
  start_time: string;
  end_time?: string;
  duration: number;
  segments: TranscriptSegment[];
  event_name?: string;
  location?: string;
  word_count: number;
}

export interface QuestionRequest {
  conversation_id: string;
  question: string;
}

export interface QuestionResponse {
  answer: string;
  confidence: number;
  sources: string[];
}

export interface ImprovementSuggestion {
  category: string;
  suggestion: string;
  priority: 'low' | 'medium' | 'high';
}
