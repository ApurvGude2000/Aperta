// ABOUTME: TypeScript type definitions for the Aperta web app
// ABOUTME: Matches the Pydantic models from the FastAPI backend

// Conversation types
export interface ConversationCreate {
  title?: string;
  transcript: string;
  status?: string;
  recording_url?: string;
  location?: string;
  event_name?: string;
  started_at?: string;
  ended_at?: string;
}

export interface ConversationUpdate {
  title?: string;
  transcript?: string;
  status?: string;
  recording_url?: string;
  location?: string;
  event_name?: string;
  ended_at?: string;
}

export interface ParticipantResponse {
  id: string;
  name?: string;
  email?: string;
  company?: string;
  title?: string;
  linkedin_url?: string;
  phone?: string;
  consent_status: string;
  lead_priority?: string;
  lead_score: number;
}

export interface EntityResponse {
  id: string;
  entity_type: string;
  entity_value: string;
  confidence: number;
  context?: string;
}

export interface ActionItemResponse {
  id: string;
  description: string;
  responsible_party?: string;
  due_date?: string;
  completed: boolean;
}

export interface ConversationResponse {
  id: string;
  user_id: string;
  title?: string;
  status: string;
  transcript?: string;
  recording_url?: string;
  location?: string;
  event_name?: string;
  started_at: string;
  ended_at?: string;
  created_at: string;
  updated_at: string;
  participants: ParticipantResponse[];
  entities: EntityResponse[];
  action_items: ActionItemResponse[];
}

export interface ConversationListItem {
  id: string;
  title?: string;
  status: string;
  location?: string;
  event_name?: string;
  started_at: string;
  created_at: string;
  participant_count: number;
}

export interface AnalysisResult {
  participants: ParticipantResponse[];
  entities: EntityResponse[];
  action_items: ActionItemResponse[];
  context_summary?: string;
  sentiment?: string;
  privacy_warnings: string[];
}

// Q&A types
export interface AskQuestionRequest {
  question: string;
  conversation_id?: string;
  use_rag?: boolean;
}

export interface AskQuestionResponse {
  session_id: string;
  interaction_id: string;
  question: string;
  final_answer: string;
  routed_agents: string[];
  execution_time: number;
  timestamp: string;
}

export interface QASessionSummary {
  id: string;
  conversation_id?: string;
  created_at: string;
  interaction_count: number;
}

export interface QAInteractionDetail {
  id: string;
  question: string;
  final_answer?: string;
  routed_agents: string[];
  responses: Record<string, any>;
  execution_time?: number;
  timestamp: string;
}

export interface QASessionDetail {
  id: string;
  conversation_id?: string;
  created_at: string;
  interactions: QAInteractionDetail[];
}

// Export format
export type ExportFormat = 'json' | 'txt' | 'markdown';
