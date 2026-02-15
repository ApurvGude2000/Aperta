// ABOUTME: Q&A interface for asking questions about conversations using AI agents
// ABOUTME: Routes questions to appropriate agents and displays intelligent responses

import { useState } from 'react';
import { askQuestion } from '../api/client';

interface RoutingDecision {
  selected_agents: string[];
  execution_mode: string;
  reasoning: string;
}

interface QAResponse {
  answer: string;
  routing_decision?: RoutingDecision;
  conversation_id: number;
  timestamp: string;
}

export default function AskQuestions() {
  const [question, setQuestion] = useState('');
  const [conversationId, setConversationId] = useState<number | ''>('');
  const [useRag, setUseRag] = useState(true);
  const [response, setResponse] = useState<QAResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const result = await askQuestion({
        question,
        conversation_id: conversationId === '' ? undefined : Number(conversationId),
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

      <form onSubmit={handleSubmit} className="space-y-4 mb-8">
        <div>
          <label htmlFor="question" className="block text-sm font-medium mb-2">
            Question
          </label>
          <textarea
            id="question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={4}
            placeholder="What would you like to know about your conversations?"
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="conversationId" className="block text-sm font-medium mb-2">
              Conversation ID (optional)
            </label>
            <input
              type="number"
              id="conversationId"
              value={conversationId}
              onChange={(e) => setConversationId(e.target.value === '' ? '' : parseInt(e.target.value))}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Leave empty for all conversations"
            />
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
            <p className="text-gray-700 whitespace-pre-wrap">{response.answer}</p>
          </div>

          {response.routing_decision && (
            <div className="border-t pt-4 mt-4">
              <h3 className="text-lg font-semibold mb-2">Routing Information</h3>
              <div className="space-y-2 text-sm">
                <div>
                  <span className="font-medium">Selected Agents:</span>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {response.routing_decision.selected_agents.map((agent) => (
                      <span
                        key={agent}
                        className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs"
                      >
                        {agent}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <span className="font-medium">Execution Mode:</span>{' '}
                  <span className="text-gray-600">{response.routing_decision.execution_mode}</span>
                </div>
                <div>
                  <span className="font-medium">Reasoning:</span>
                  <p className="text-gray-600 mt-1">{response.routing_decision.reasoning}</p>
                </div>
              </div>
            </div>
          )}

          <div className="border-t pt-3 mt-4 text-sm text-gray-500">
            <span>Conversation ID: {response.conversation_id}</span>
            <span className="mx-2">•</span>
            <span>Timestamp: {new Date(response.timestamp).toLocaleString()}</span>
          </div>
        </div>
      )}
    </div>
  );
}
