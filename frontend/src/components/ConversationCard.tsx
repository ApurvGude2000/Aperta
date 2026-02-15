// ABOUTME: Card component for displaying conversation summary in list view
// ABOUTME: Shows title, preview, metadata (date, duration, word count)

import type { Conversation } from '../types';

interface Props {
  conversation: Conversation;
  onClick: () => void;
}

export function ConversationCard({ conversation, onClick }: Props) {
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    return `${minutes} min`;
  };

  const preview = conversation.transcript.substring(0, 150) + (conversation.transcript.length > 150 ? '...' : '');

  return (
    <div
      onClick={onClick}
      className="conversation-card"
      style={{
        border: '1px solid #e5e7eb',
        borderRadius: '8px',
        padding: '20px',
        marginBottom: '16px',
        cursor: 'pointer',
        transition: 'all 0.2s',
        backgroundColor: 'white',
      }}
      onMouseOver={(e) => {
        e.currentTarget.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
        e.currentTarget.style.borderColor = '#3b82f6';
      }}
      onMouseOut={(e) => {
        e.currentTarget.style.boxShadow = 'none';
        e.currentTarget.style.borderColor = '#e5e7eb';
      }}
    >
      <h3 style={{ margin: '0 0 8px 0', fontSize: '18px', fontWeight: '600' }}>
        {conversation.title}
      </h3>

      <p style={{ color: '#6b7280', margin: '0 0 12px 0', lineHeight: '1.5' }}>
        {preview}
      </p>

      <div style={{ display: 'flex', gap: '16px', fontSize: '14px', color: '#9ca3af' }}>
        <span>📅 {formatDate(conversation.start_time)}</span>
        <span>⏱️ {formatDuration(conversation.duration)}</span>
        <span>📝 {conversation.word_count} words</span>
      </div>

      {conversation.event_name && (
        <div style={{ marginTop: '8px', fontSize: '14px', color: '#3b82f6' }}>
          🎯 {conversation.event_name}
        </div>
      )}
    </div>
  );
}
