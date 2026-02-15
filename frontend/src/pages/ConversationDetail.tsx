// ABOUTME: Detail page for viewing a single conversation with AI analysis
// ABOUTME: Shows transcript, participants, entities, action items

import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import type { ConversationResponse, AnalysisResult } from '../types';
import { AudioTranscriptionViewer } from '../components/AudioTranscriptionViewer';

export function ConversationDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [conversation, setConversation] = useState<ConversationResponse | null>(null);
  const [_analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [audioData, setAudioData] = useState<any>(null);
  const [transcriptionData, setTranscriptionData] = useState<any>(null);
  const [loadingAudio, setLoadingAudio] = useState(false);

  useEffect(() => {
    if (id) {
      loadConversation(id);
      loadAudioData(id);
    }
  }, [id]);

  const loadConversation = async (conversationId: string) => {
    try {
      setLoading(true);
      const data = await api.getConversation(conversationId);
      setConversation(data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load conversation');
    } finally {
      setLoading(false);
    }
  };

  const loadAudioData = async (conversationId: string) => {
    try {
      setLoadingAudio(true);
      // Try to fetch audio and transcription data from the backend
      // This would be an API call like: const data = await api.getAudioRecording(conversationId);
      // For now, we'll leave this as a placeholder for when the API is ready
      // setAudioData(data.audio);
      // setTranscriptionData(data.transcription);
    } catch (err: any) {
      console.warn('Could not load audio data:', err.message);
    } finally {
      setLoadingAudio(false);
    }
  };

  const handleAnalyze = async () => {
    if (!id) return;

    setAnalyzing(true);
    try {
      const data = await api.analyzeConversation(id);
      setAnalysis(data);
      // Reload conversation to get updated data
      await loadConversation(id);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze conversation');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleExport = async (format: 'json' | 'txt' | 'markdown') => {
    if (!id) return;

    try {
      const data = await api.exportConversation(id, format);
      const blob = new Blob([data], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `conversation-${id}.${format}`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to export conversation');
    }
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto p-6 text-center">
        <div className="text-gray-500">Loading conversation...</div>
      </div>
    );
  }

  if (error && !conversation) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">
          <p className="font-medium">Error</p>
          <p>{error}</p>
        </div>
        <button
          onClick={() => navigate('/')}
          className="mt-4 text-blue-600 hover:text-blue-800"
        >
          ← Back to Conversations
        </button>
      </div>
    );
  }

  if (!conversation) {
    return (
      <div className="max-w-6xl mx-auto p-6 text-center">
        <div className="text-gray-500">Conversation not found</div>
        <button
          onClick={() => navigate('/')}
          className="mt-4 text-blue-600 hover:text-blue-800"
        >
          ← Back to Conversations
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/')}
          className="mb-4 text-blue-600 hover:text-blue-800 font-medium"
        >
          ← Back to Conversations
        </button>

        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold mb-2">
              {conversation.title || 'Untitled Conversation'}
            </h1>
            <div className="text-gray-600 space-x-3">
              {conversation.event_name && <span>🎯 {conversation.event_name}</span>}
              <span>📅 {new Date(conversation.started_at).toLocaleString()}</span>
              {conversation.location && <span>📍 {conversation.location}</span>}
              <span className="px-2 py-1 rounded bg-blue-100 text-blue-800 text-sm">
                {conversation.status}
              </span>
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleAnalyze}
              disabled={analyzing}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {analyzing ? 'Analyzing...' : 'Run AI Analysis'}
            </button>
            <div className="relative group">
              <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                Export
              </button>
              <div className="absolute right-0 mt-2 w-32 bg-white border border-gray-200 rounded-lg shadow-lg hidden group-hover:block">
                <button
                  onClick={() => handleExport('json')}
                  className="block w-full text-left px-4 py-2 hover:bg-gray-100"
                >
                  JSON
                </button>
                <button
                  onClick={() => handleExport('txt')}
                  className="block w-full text-left px-4 py-2 hover:bg-gray-100"
                >
                  Text
                </button>
                <button
                  onClick={() => handleExport('markdown')}
                  className="block w-full text-left px-4 py-2 hover:bg-gray-100"
                >
                  Markdown
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg mb-6">
          <p>{error}</p>
        </div>
      )}

      {/* Audio & Transcription Viewer */}
      {(audioData || transcriptionData) && (
        <AudioTranscriptionViewer
          audio={audioData}
          transcription={transcriptionData}
          conversationId={id || ''}
          isLoading={loadingAudio}
        />
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Transcript */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Transcript</h2>
            <div className="bg-gray-50 border border-gray-200 rounded p-4 whitespace-pre-wrap font-mono text-sm">
              {conversation.transcript || 'No transcript available'}
            </div>
          </div>
        </div>

        {/* Right Column - Analysis */}
        <div className="space-y-6">
          {/* Participants */}
          {conversation.participants && conversation.participants.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Participants ({conversation.participants.length})</h2>
              <div className="space-y-3">
                {conversation.participants.map((participant) => (
                  <div key={participant.id} className="border-b border-gray-100 pb-3 last:border-0">
                    <div className="font-medium">{participant.name || 'Unknown'}</div>
                    {participant.company && (
                      <div className="text-sm text-gray-600">{participant.company}</div>
                    )}
                    {participant.title && (
                      <div className="text-sm text-gray-500">{participant.title}</div>
                    )}
                    {participant.lead_score > 0 && (
                      <div className="text-xs text-blue-600 mt-1">
                        Lead Score: {participant.lead_score.toFixed(1)}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Entities */}
          {conversation.entities && conversation.entities.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Entities ({conversation.entities.length})</h2>
              <div className="space-y-2">
                {conversation.entities.slice(0, 10).map((entity) => (
                  <div key={entity.id} className="flex items-start gap-2">
                    <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs font-medium">
                      {entity.entity_type}
                    </span>
                    <span className="text-sm">{entity.entity_value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Items */}
          {conversation.action_items && conversation.action_items.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Action Items ({conversation.action_items.length})</h2>
              <div className="space-y-3">
                {conversation.action_items.map((item) => (
                  <div key={item.id} className="flex items-start gap-2">
                    <input
                      type="checkbox"
                      checked={item.completed}
                      readOnly
                      className="mt-1"
                    />
                    <div className="flex-1">
                      <div className={item.completed ? 'line-through text-gray-500' : ''}>
                        {item.description}
                      </div>
                      {item.responsible_party && (
                        <div className="text-xs text-gray-500 mt-1">
                          Assigned to: {item.responsible_party}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Prompt to analyze if no data */}
          {(!conversation.participants || conversation.participants.length === 0) &&
            (!conversation.entities || conversation.entities.length === 0) &&
            (!conversation.action_items || conversation.action_items.length === 0) && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
                <p className="text-blue-900 font-medium mb-2">No Analysis Yet</p>
                <p className="text-sm text-blue-700 mb-4">
                  Run AI analysis to extract participants, entities, and action items from this conversation.
                </p>
                <button
                  onClick={handleAnalyze}
                  disabled={analyzing}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
                >
                  {analyzing ? 'Analyzing...' : 'Analyze Now'}
                </button>
              </div>
            )}
        </div>
      </div>
    </div>
  );
}
