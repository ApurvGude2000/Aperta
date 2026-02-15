// ABOUTME: Card component for displaying conversation summary in list view
// ABOUTME: Shows title, preview, metadata (date, location, participant count)

import type { ConversationListItem } from '../types';

interface Props {
  conversation: ConversationListItem;
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return '#10b981';
      case 'archived':
        return '#6b7280';
      case 'pending':
        return '#f59e0b';
      default:
        return '#3b82f6';
    }
  };

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
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
        <h3 style={{ margin: '0 0 8px 0', fontSize: '18px', fontWeight: '600' }}>
          {conversation.title || 'Untitled Conversation'}
        </h3>
        <span
          style={{
            padding: '4px 8px',
            borderRadius: '4px',
            fontSize: '12px',
            fontWeight: '500',
            backgroundColor: getStatusColor(conversation.status) + '20',
            color: getStatusColor(conversation.status),
          }}
        >
          {conversation.status}
        </span>
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', fontSize: '14px', color: '#6b7280', marginTop: '12px' }}>
        <span>📅 {formatDate(conversation.started_at)}</span>
        <span>👥 {conversation.participant_count} participant{conversation.participant_count !== 1 ? 's' : ''}</span>
        {conversation.location && <span>📍 {conversation.location}</span>}
      </div>

      {conversation.event_name && (
        <div style={{ marginTop: '8px', fontSize: '14px', color: '#3b82f6', fontWeight: '500' }}>
          🎯 {conversation.event_name}
        </div>
      )}
    </div>
  );
}
