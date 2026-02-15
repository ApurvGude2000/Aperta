/**
 * ABOUTME: Component for displaying audio recordings with transcriptions
 * ABOUTME: Shows audio player, speaker diarization, and extracted insights
 */

import { useState, useRef, useEffect } from 'react';

interface AudioSegment {
  speaker_id: number;
  start_time: number;
  end_time: number;
  text: string;
  confidence: number;
}

interface TranscriptionData {
  id: string;
  conversation_id: string;
  raw_text?: string;
  formatted_text?: string;
  speaker_count: number;
  speaker_names: Record<string, string>;
  segments: AudioSegment[];
  confidence_score?: number;
  sentiment?: string;
  summary?: string;
  entities: any[];
  action_items: any[];
  created_at: string;
}

interface AudioRecording {
  id: string;
  conversation_id: string;
  file_path: string;
  duration: number;
  original_filename: string;
  processing_status: string;
  created_at: string;
}

interface AudioTranscriptionViewerProps {
  audio?: AudioRecording;
  transcription?: TranscriptionData;
  conversationId: string;
  isLoading?: boolean;
}

export function AudioTranscriptionViewer({
  audio,
  transcription,
  conversationId,
  isLoading = false,
}: AudioTranscriptionViewerProps) {
  const [currentTime, setCurrentTime] = useState(0);
  const [selectedSpeaker, setSelectedSpeaker] = useState<number | null>(null);
  const [expandedSegment, setExpandedSegment] = useState<number | null>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-12 bg-gray-200 rounded"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (!audio && !transcription) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-gray-50 border border-gray-200 text-gray-700 p-6 rounded-lg text-center">
          <p>No audio or transcription available for this conversation</p>
        </div>
      </div>
    );
  }

  const speakerList = transcription
    ? Object.entries(transcription.speaker_names).map(([id, name]) => ({
        id: parseInt(id),
        name,
      }))
    : [];

  const filteredSegments = transcription?.segments
    ? selectedSpeaker !== null
      ? transcription.segments.filter((s) => s.speaker_id === selectedSpeaker)
      : transcription.segments
    : [];

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Audio Player */}
      {audio && (
        <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              📻 Audio Recording
            </h3>
            <p className="text-sm text-gray-600 mb-4">{audio.original_filename}</p>
            <audio
              ref={audioRef}
              controls
              className="w-full bg-gray-100 rounded"
              onTimeUpdate={() =>
                audioRef.current && setCurrentTime(audioRef.current.currentTime)
              }
            >
              <source src={audio.file_path} />
              Your browser does not support the audio element.
            </audio>
            <div className="mt-2 flex justify-between text-xs text-gray-500">
              <span>Duration: {formatTime(audio.duration)}</span>
              <span>Current: {formatTime(currentTime)}</span>
            </div>
          </div>
        </div>
      )}

      {/* Transcription Analysis */}
      {transcription && (
        <div className="space-y-6">
          {/* Summary and Sentiment */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <div className="space-y-4">
              {transcription.summary && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-900 mb-2">
                    Summary
                  </h4>
                  <p className="text-sm text-gray-700">{transcription.summary}</p>
                </div>
              )}

              <div className="flex gap-4 flex-wrap">
                <div>
                  <p className="text-xs text-gray-600">Sentiment</p>
                  <p className="text-sm font-semibold text-gray-900">
                    {transcription.sentiment || 'Unknown'}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-600">Confidence</p>
                  <p className="text-sm font-semibold text-gray-900">
                    {transcription.confidence_score
                      ? `${Math.round(
                          transcription.confidence_score * 100
                        )}%`
                      : 'N/A'}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-600">Speakers</p>
                  <p className="text-sm font-semibold text-gray-900">
                    {transcription.speaker_count}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Speaker Filter */}
          {speakerList.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-gray-900 mb-3">
                Filter by Speaker
              </h4>
              <div className="flex gap-2 flex-wrap">
                <button
                  onClick={() => setSelectedSpeaker(null)}
                  className={`px-3 py-2 text-sm rounded-full font-medium transition ${
                    selectedSpeaker === null
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  All Speakers
                </button>
                {speakerList.map((speaker) => (
                  <button
                    key={speaker.id}
                    onClick={() => setSelectedSpeaker(speaker.id)}
                    className={`px-3 py-2 text-sm rounded-full font-medium transition ${
                      selectedSpeaker === speaker.id
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {speaker.name}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Transcript Segments */}
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-gray-900">Transcript</h4>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {filteredSegments.map((segment, index) => {
                const speakerName =
                  transcription.speaker_names[segment.speaker_id] ||
                  `Speaker ${segment.speaker_id}`;
                const isExpanded = expandedSegment === index;

                return (
                  <div
                    key={index}
                    className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition"
                  >
                    <div
                      onClick={() =>
                        setExpandedSegment(isExpanded ? null : index)
                      }
                      className="cursor-pointer"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <span className="inline-block bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded mr-2">
                            {speakerName}
                          </span>
                          <span className="text-xs text-gray-500">
                            {formatTime(segment.start_time)} -{' '}
                            {formatTime(segment.end_time)}
                          </span>
                        </div>
                        <div className="text-xs text-gray-500">
                          {(segment.confidence * 100).toFixed(0)}%
                        </div>
                      </div>

                      <p
                        className={`mt-2 text-sm text-gray-700 ${
                          isExpanded ? '' : 'line-clamp-2'
                        }`}
                      >
                        {segment.text}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Extracted Entities */}
          {transcription.entities && transcription.entities.length > 0 && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <h4 className="text-sm font-semibold text-gray-900 mb-3">
                Extracted Entities
              </h4>
              <div className="space-y-2">
                {transcription.entities.map((entity: any, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <span className="inline-block bg-green-100 text-green-800 text-xs font-semibold px-2.5 py-0.5 rounded">
                      {entity.type || 'Entity'}
                    </span>
                    <span className="text-sm text-gray-700">
                      {typeof entity === 'string' ? entity : entity.value}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Items */}
          {transcription.action_items && transcription.action_items.length > 0 && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
              <h4 className="text-sm font-semibold text-gray-900 mb-3">
                Action Items
              </h4>
              <ul className="space-y-2">
                {transcription.action_items.map((item: any, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <input
                      type="checkbox"
                      className="mt-1 rounded"
                      defaultChecked={false}
                    />
                    <span className="text-sm text-gray-700">
                      {typeof item === 'string' ? item : item.description}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Raw Transcript */}
          {transcription.formatted_text && (
            <details className="bg-gray-50 border border-gray-200 rounded-lg p-6">
              <summary className="cursor-pointer text-sm font-semibold text-gray-900">
                View Full Transcript
              </summary>
              <pre className="mt-4 p-4 bg-white border border-gray-200 rounded overflow-auto text-xs text-gray-700 max-h-48">
                {transcription.formatted_text}
              </pre>
            </details>
          )}
        </div>
      )}
    </div>
  );
}

// Helper function to format time
function formatTime(seconds: number): string {
  if (!Number.isFinite(seconds)) return '0:00';
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs
      .toString()
      .padStart(2, '0')}`;
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`;
}
