// ABOUTME: Form component for creating and editing conversations
// ABOUTME: Handles conversation metadata and transcript input with validation

import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { api } from '../api/client';
import type { ConversationCreate, ConversationUpdate } from '../types';

export function ConversationForm() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const isEditing = !!id;

  const [title, setTitle] = useState('');
  const [transcript, setTranscript] = useState('');
  const [location, setLocation] = useState('');
  const [eventName, setEventName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [initialLoading, setInitialLoading] = useState(isEditing);

  useEffect(() => {
    if (isEditing && id) {
      loadConversation();
    }
  }, [id]);

  const loadConversation = async () => {
    if (!id) return;

    try {
      const conversation = await api.getConversation(id);
      setTitle(conversation.title || '');
      setTranscript(conversation.transcript || '');
      setLocation(conversation.location || '');
      setEventName(conversation.event_name || '');
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
      if (isEditing && id) {
        const updateData: ConversationUpdate = {
          title: title.trim() || undefined,
          transcript: transcript.trim(),
          location: location.trim() || undefined,
          event_name: eventName.trim() || undefined,
        };
        await api.updateConversation(id, updateData);
      } else {
        const createData: ConversationCreate = {
          title: title.trim() || undefined,
          transcript: transcript.trim(),
          location: location.trim() || undefined,
          event_name: eventName.trim() || undefined,
          started_at: new Date().toISOString(),
        };
        await api.createConversation(createData);
      }

      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || `Failed to ${isEditing ? 'update' : 'create'} conversation`);
    } finally {
      setLoading(false);
    }
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
          onClick={() => navigate('/')}
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
            Title
          </label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="e.g., Career Fair Networking Session"
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
              <label htmlFor="location" className="block text-sm font-medium mb-2">
                Location
              </label>
              <input
                type="text"
                id="location"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., Tech Conference, Virtual Meeting"
              />
            </div>

            <div>
              <label htmlFor="eventName" className="block text-sm font-medium mb-2">
                Event Name
              </label>
              <input
                type="text"
                id="eventName"
                value={eventName}
                onChange={(e) => setEventName(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., Tech Meetup 2024, Career Fair"
              />
            </div>
          </div>
        </div>

        <div className="flex gap-3 pt-4">
          <button
            type="submit"
            disabled={loading || !transcript.trim()}
            className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {loading ? 'Saving...' : isEditing ? 'Update Conversation' : 'Create Conversation'}
          </button>
          <button
            type="button"
            onClick={() => navigate('/')}
            className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
