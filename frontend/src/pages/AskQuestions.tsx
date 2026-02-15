// ABOUTME: Q&A interface for asking questions about conversations using AI agents
// ABOUTME: Routes questions to appropriate agents and displays intelligent responses

import { useState, useEffect } from 'react';
import { api } from '../api/client';
import type { AskQuestionResponse, ConversationListItem } from '../types';

export function AskQuestions() {
  const [question, setQuestion] = useState('');
  const [conversationId, setConversationId] = useState('');
  const [useRag, setUseRag] = useState(true);
  const [response, setResponse] = useState<AskQuestionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversations, setConversations] = useState<ConversationListItem[]>([]);
  const [loadingConversations, setLoadingConversations] = useState(false);

  // Load conversations on mount
  useEffect(() => {
    const loadConversations = async () => {
      setLoadingConversations(true);
      try {
        const convs = await api.getConversations();
        setConversations(convs);
      } catch (err) {
        console.error('Failed to load conversations:', err);
      } finally {
        setLoadingConversations(false);
      }
    };
    loadConversations();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const result = await api.askQuestion({
        question,
        conversation_id: conversationId.trim() || undefined,
        use_rag: useRag,
      });
      setResponse(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get response');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Ask Questions</h1>

      <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg mb-6">
        <h2 className="font-semibold text-blue-900 mb-2">How it works</h2>
        <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
          <li>Ask questions about your conversations - the AI will route them to the appropriate agents</li>
          <li><strong>Select a conversation</strong> to ask specific questions about that meeting/event</li>
          <li>Or ask general questions without selecting a conversation</li>
          <li>Available agents: Context Understanding, Strategic Networking, Follow-Up, Privacy Guardian, Perception</li>
        </ul>
        {conversations.length === 0 && (
          <div className="mt-3 pt-3 border-t border-blue-300">
            <p className="text-sm text-blue-900 font-medium">
              👉 No conversations yet! <a href="/conversations/new" className="underline hover:text-blue-700">Create your first conversation</a> to get started.
            </p>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="space-y-4 mb-8">
        <div>
          <label htmlFor="question" className="block text-sm font-medium mb-2">
            Question *
          </label>
          <textarea
            id="question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={4}
            placeholder="e.g., Who are the key people I met at the tech conference? What follow-up actions should I take?"
            required
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="conversationId" className="block text-sm font-medium mb-2">
              Select Conversation (optional)
            </label>
            <select
              id="conversationId"
              value={conversationId}
              onChange={(e) => setConversationId(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={loadingConversations}
            >
              <option value="">General question (no specific conversation)</option>
              {conversations.map((conv) => (
                <option key={conv.id} value={conv.id}>
                  {conv.title || `Conversation from ${new Date(conv.started_at).toLocaleDateString()}`}
                  {conv.location ? ` - ${conv.location}` : ''}
                </option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-1">
              {loadingConversations
                ? 'Loading conversations...'
                : conversations.length === 0
                  ? 'No conversations yet. Create one first!'
                  : 'Select a conversation to ask questions about it'}
            </p>
          </div>

          <div className="flex items-end">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={useRag}
                onChange={(e) => setUseRag(e.target.checked)}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-sm font-medium">Use RAG Context</span>
            </label>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
        >
          {loading ? 'Processing...' : 'Ask Question'}
        </button>
      </form>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg mb-4">
          <p className="font-medium">Error</p>
          <p>{error}</p>
        </div>
      )}

      {response && (
        <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
          <div className="mb-4">
            <h2 className="text-xl font-semibold mb-2">Answer</h2>
            <p className="text-gray-700 whitespace-pre-wrap">{response.final_answer}</p>
          </div>

          <div className="border-t pt-4 mt-4">
            <h3 className="text-lg font-semibold mb-2">Agent Routing</h3>
            <div className="space-y-2 text-sm">
              <div>
                <span className="font-medium">Routed to Agents:</span>
                <div className="flex flex-wrap gap-2 mt-1">
                  {response.routed_agents.map((agent) => (
                    <span
                      key={agent}
                      className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-xs font-medium"
                    >
                      {agent}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <span className="font-medium">Execution Time:</span>{' '}
                <span className="text-gray-600">{response.execution_time.toFixed(2)}s</span>
              </div>
            </div>
          </div>

          <div className="border-t pt-3 mt-4 text-sm text-gray-500">
            <div className="flex flex-wrap gap-x-4 gap-y-1">
              <span>Session ID: {response.session_id}</span>
              <span>Interaction ID: {response.interaction_id}</span>
              <span>Timestamp: {new Date(response.timestamp).toLocaleString()}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
