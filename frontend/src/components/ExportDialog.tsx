// ABOUTME: Dialog component for exporting conversations in various formats
// ABOUTME: Supports JSON, TXT, and Markdown export formats

import { useState } from 'react';
import { exportConversation } from '../api/client';

interface ExportDialogProps {
  conversationId: number;
  conversationTitle: string;
  isOpen: boolean;
  onClose: () => void;
}

type ExportFormat = 'json' | 'txt' | 'markdown';

export default function ExportDialog({ conversationId, conversationTitle, isOpen, onClose }: ExportDialogProps) {
  const [format, setFormat] = useState<ExportFormat>('json');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleExport = async () => {
    setLoading(true);
    setError(null);

    try {
      const blob = await exportConversation(conversationId, format);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      
      // Set filename based on format
      const extension = format === 'markdown' ? 'md' : format;
      const sanitizedTitle = conversationTitle.replace(/[^a-z0-9]/gi, '_').toLowerCase();
      a.download = `${sanitizedTitle}_${conversationId}.${extension}`;
      
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to export conversation');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 shadow-xl">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Export Conversation</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
            aria-label="Close"
          >
            ×
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-lg mb-4 text-sm">
            {error}
          </div>
        )}

        <div className="mb-6">
          <p className="text-sm text-gray-600 mb-4">
            Export "{conversationTitle}" in your preferred format.
          </p>

          <div className="space-y-2">
            <label className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
              <input
                type="radio"
                name="format"
                value="json"
                checked={format === 'json'}
                onChange={(e) => setFormat(e.target.value as ExportFormat)}
                className="w-4 h-4 text-blue-600"
              />
              <div>
                <div className="font-medium">JSON</div>
                <div className="text-sm text-gray-500">Structured data format</div>
              </div>
            </label>

            <label className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
              <input
                type="radio"
                name="format"
                value="txt"
                checked={format === 'txt'}
                onChange={(e) => setFormat(e.target.value as ExportFormat)}
                className="w-4 h-4 text-blue-600"
              />
              <div>
                <div className="font-medium">Plain Text</div>
                <div className="text-sm text-gray-500">Simple text file</div>
              </div>
            </label>

            <label className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
              <input
                type="radio"
                name="format"
                value="markdown"
                checked={format === 'markdown'}
                onChange={(e) => setFormat(e.target.value as ExportFormat)}
                className="w-4 h-4 text-blue-600"
              />
              <div>
                <div className="font-medium">Markdown</div>
                <div className="text-sm text-gray-500">Formatted document</div>
              </div>
            </label>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={handleExport}
            disabled={loading}
            className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {loading ? 'Exporting...' : 'Export'}
          </button>
          <button
            onClick={onClose}
            disabled={loading}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
