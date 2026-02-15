// ABOUTME: Form component for creating and editing conversations
// ABOUTME: Handles conversation metadata and transcript input with validation

import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { createConversation, getConversation, updateConversation } from '../api/client';
import type { Conversation } from '../types';

export default function ConversationForm() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const isEditing = !!id;

  const [title, setTitle] = useState('');
  const [transcript, setTranscript] = useState('');
  const [metadata, setMetadata] = useState<Record<string, any>>({
    date: new Date().toISOString().split('T')[0],
    location: '',
    participants: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [initialLoading, setInitialLoading] = useState(isEditing);

  useEffect(() => {
    if (isEditing) {
      loadConversation();
    }
  }, [id]);

  const loadConversation = async () => {
    try {
      const conversation = await getConversation(Number(id));
      setTitle(conversation.title);
      setTranscript(conversation.transcript);
      setMetadata(conversation.metadata || {});
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load conversation');
    } finally {
      setInitialLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const conversationData = {
        title,
        transcript,
        metadata,
      };

      if (isEditing) {
        await updateConversation(Number(id), conversationData);
      } else {
        await createConversation(conversationData);
      }

      navigate('/conversations');
    } catch (err: any) {
      setError(err.response?.data?.detail || `Failed to ${isEditing ? 'update' : 'create'} conversation`);
    } finally {
      setLoading(false);
    }
  };

  const handleMetadataChange = (key: string, value: string) => {
    setMetadata((prev) => ({ ...prev, [key]: value }));
  };

  if (initialLoading) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="text-center text-gray-500">Loading conversation...</div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">
          {isEditing ? 'Edit Conversation' : 'New Conversation'}
        </h1>
        <button
          onClick={() => navigate('/conversations')}
          className="text-gray-600 hover:text-gray-900 font-medium"
        >
          Cancel
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg mb-4">
          <p className="font-medium">Error</p>
          <p>{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="title" className="block text-sm font-medium mb-2">
            Title *
          </label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="e.g., Career Fair Networking Session"
            required
          />
        </div>

        <div>
          <label htmlFor="transcript" className="block text-sm font-medium mb-2">
            Transcript *
          </label>
          <textarea
            id="transcript"
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
            rows={15}
            placeholder="Paste your conversation transcript here..."
            required
          />
          <p className="text-sm text-gray-500 mt-1">
            Character count: {transcript.length}
          </p>
        </div>

        <div className="border-t pt-6">
          <h2 className="text-lg font-semibold mb-4">Metadata (Optional)</h2>
          
          <div className="space-y-4">
            <div>
              <label htmlFor="date" className="block text-sm font-medium mb-2">
                Date
              </label>
              <input
                type="date"
                id="date"
                value={metadata.date || ''}
                onChange={(e) => handleMetadataChange('date', e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label htmlFor="location" className="block text-sm font-medium mb-2">
                Location
              </label>
              <input
                type="text"
                id="location"
                value={metadata.location || ''}
                onChange={(e) => handleMetadataChange('location', e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., Tech Conference, Virtual Meeting"
              />
            </div>

            <div>
              <label htmlFor="participants" className="block text-sm font-medium mb-2">
                Participants
              </label>
              <input
                type="text"
                id="participants"
                value={metadata.participants || ''}
                onChange={(e) => handleMetadataChange('participants', e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., John Doe, Jane Smith"
              />
            </div>

            <div>
              <label htmlFor="tags" className="block text-sm font-medium mb-2">
                Tags
              </label>
              <input
                type="text"
                id="tags"
                value={metadata.tags || ''}
                onChange={(e) => handleMetadataChange('tags', e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., networking, career, tech"
              />
              <p className="text-sm text-gray-500 mt-1">
                Separate tags with commas
              </p>
            </div>
          </div>
        </div>

        <div className="flex gap-3 pt-4">
          <button
            type="submit"
            disabled={loading || !title.trim() || !transcript.trim()}
            className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {loading ? 'Saving...' : isEditing ? 'Update Conversation' : 'Create Conversation'}
          </button>
          <button
            type="button"
            onClick={() => navigate('/conversations')}
            className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
