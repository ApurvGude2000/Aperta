// ABOUTME: Detail page for viewing a single conversation with AI features
// ABOUTME: Shows transcript, allows questions, displays improvement suggestions

import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import type { Conversation, ImprovementSuggestion, QuestionResponse } from '../types';

export function ConversationDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [improvements, setImprovements] = useState<ImprovementSuggestion[]>([]);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState<QuestionResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [askingQuestion, setAskingQuestion] = useState(false);

  useEffect(() => {
    if (id) {
      loadConversation(id);
      loadImprovements(id);
    }
  }, [id]);

  const loadConversation = async (conversationId: string) => {
    try {
      const data = await api.getConversation(conversationId);
      setConversation(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadImprovements = async (conversationId: string) => {
    try {
      const data = await api.getImprovements(conversationId);
      setImprovements(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleAskQuestion = async () => {
    if (!id || !question.trim()) return;

    setAskingQuestion(true);
    try {
      const response = await api.askQuestion({
        conversation_id: id,
        question: question.trim(),
      });
      setAnswer(response);
    } catch (err) {
      console.error(err);
    } finally {
      setAskingQuestion(false);
    }
  };

  if (loading) {
    return <div style={{ padding: '40px', textAlign: 'center' }}>Loading...</div>;
  }

  if (!conversation) {
    return <div style={{ padding: '40px', textAlign: 'center' }}>Conversation not found</div>;
  }

  const priorityColors = {
    high: '#ef4444',
    medium: '#f59e0b',
    low: '#10b981',
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '20px' }}>
      {/* Header */}
      <button
        onClick={() => navigate('/')}
        style={{
          marginBottom: '20px',
          padding: '8px 16px',
          border: '1px solid #e5e7eb',
          borderRadius: '6px',
          background: 'white',
          cursor: 'pointer',
        }}
      >
        ← Back to Conversations
      </button>

      <h1 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '8px' }}>
        {conversation.title}
      </h1>

      <div style={{ color: '#6b7280', marginBottom: '24px' }}>
        {conversation.event_name && <span>🎯 {conversation.event_name} • </span>}
        <span>📅 {new Date(conversation.start_time).toLocaleString()}</span>
        {conversation.location && <span> • 📍 {conversation.location}</span>}
      </div>

      {/* Transcript */}
      <div style={{ marginBottom: '32px' }}>
        <h2 style={{ fontSize: '24px', fontWeight: '600', marginBottom: '16px' }}>
          Transcript
        </h2>
        <div
          style={{
            background: '#f9fafb',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            padding: '20px',
            lineHeight: '1.8',
          }}
        >
          {conversation.transcript}
        </div>
      </div>

      {/* Ask Questions */}
      <div style={{ marginBottom: '32px' }}>
        <h2 style={{ fontSize: '24px', fontWeight: '600', marginBottom: '16px' }}>
          Ask Questions (Placeholder)
        </h2>
        <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about this conversation..."
            style={{
              flex: 1,
              padding: '12px',
              border: '1px solid #e5e7eb',
              borderRadius: '6px',
              fontSize: '14px',
            }}
            onKeyPress={(e) => e.key === 'Enter' && handleAskQuestion()}
          />
          <button
            onClick={handleAskQuestion}
            disabled={askingQuestion || !question.trim()}
            style={{
              padding: '12px 24px',
              background: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: askingQuestion ? 'wait' : 'pointer',
              opacity: !question.trim() ? 0.5 : 1,
            }}
          >
            {askingQuestion ? 'Asking...' : 'Ask'}
          </button>
        </div>

        {answer && (
          <div
            style={{
              background: '#eff6ff',
              border: '1px solid #3b82f6',
              borderRadius: '8px',
              padding: '16px',
            }}
          >
            <div style={{ fontWeight: '600', marginBottom: '8px', color: '#1e40af' }}>
              Answer:
            </div>
            <div style={{ marginBottom: '12px' }}>{answer.answer}</div>
            <div style={{ fontSize: '12px', color: '#6b7280' }}>
              Confidence: {(answer.confidence * 100).toFixed(0)}%
            </div>
          </div>
        )}
      </div>

      {/* Improvements */}
      <div>
        <h2 style={{ fontSize: '24px', fontWeight: '600', marginBottom: '16px' }}>
          Improvement Suggestions (Placeholder)
        </h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {improvements.map((improvement, index) => (
            <div
              key={index}
              style={{
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                padding: '16px',
                background: 'white',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontWeight: '600', color: '#1f2937' }}>
                  {improvement.category}
                </span>
                <span
                  style={{
                    padding: '2px 8px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    fontWeight: '600',
                    background: priorityColors[improvement.priority] + '20',
                    color: priorityColors[improvement.priority],
                  }}
                >
                  {improvement.priority.toUpperCase()}
                </span>
              </div>
              <div style={{ color: '#4b5563' }}>{improvement.suggestion}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
