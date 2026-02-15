import React, { useState } from 'react';
import { Navigation } from '../components/design-system/Navigation';
import { Sidebar } from '../components/design-system/Sidebar';
import { Button } from '../components/design-system/Button';

export function Transcripts() {
  const [selectedTranscript, setSelectedTranscript] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');

  const transcripts = [
    {
      id: 1,
      title: 'TechCrunch Disrupt - Conversation 1',
      date: 'March 15, 2024',
      duration: '15:32',
      speakers: ['Alice Johnson', 'Bob Smith', 'Carol White'],
      segments: [
        { speaker: 'Alice Johnson', time: '0:00', text: 'Hi everyone, welcome to TechCrunch Disrupt. Great to see everyone here today.' },
        { speaker: 'Bob Smith', time: '0:15', text: '[PII REDACTED: Bob introduces himself and discusses AI safety concerns]' },
        { speaker: 'Carol White', time: '1:05', text: 'That\'s a fascinating perspective. Let me share our approach to privacy protection.' },
        { speaker: 'Alice Johnson', time: '2:15', text: 'Thank you for that insight. How do you see this evolving in the next few years?' },
        { speaker: 'Bob Smith', time: '3:00', text: 'We believe the market will consolidate around privacy-first solutions by 2026.' },
      ],
    },
    {
      id: 2,
      title: 'YC Demo Day - Pitch Discussion',
      date: 'March 10, 2024',
      duration: '22:45',
      speakers: ['David Lee', 'Emma Wilson', 'Frank Brown'],
      segments: [
        { speaker: 'David Lee', time: '0:00', text: 'Thanks for having us at YC Demo Day. Excited to share our vision.' },
        { speaker: 'Emma Wilson', time: '1:20', text: '[PII REDACTED: Emma discusses company metrics and growth]' },
        { speaker: 'Frank Brown', time: '3:15', text: 'What\'s your go-to-market strategy looking like for Q2?' },
      ],
    },
    {
      id: 3,
      title: 'Stanford AI Conference - Panel Discussion',
      date: 'February 28, 2024',
      duration: '18:00',
      speakers: ['Grace Chen', 'Henry Adams', 'Ivy Martinez'],
      segments: [
        { speaker: 'Grace Chen', time: '0:00', text: 'Good morning everyone. Today we\'re discussing AI safety and responsible deployment.' },
        { speaker: 'Henry Adams', time: '1:45', text: '[PII REDACTED: Henry shares research findings on bias in AI systems]' },
      ],
    },
  ];

  const currentTranscript = transcripts.find(t => t.id === selectedTranscript);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-cyan-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-40 right-10 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
      </div>

      <Navigation isAuthenticated={true} />

      <div className="flex relative z-10">
        <Sidebar isOpen={true} />

        <main className="flex-1 p-8">
          {/* Header */}
          <div className="mb-8 sticky-section">
            <h1 className="font-display text-5xl font-bold text-white mb-2">Transcripts</h1>
            <p className="text-black text-lg">View and search your conversation transcripts</p>
          </div>

          {/* Main Content - Two Column Layout */}
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Left Column - Transcript List */}
            <div className="lg:col-span-1">
              {/* Search */}
              <div className="mb-6">
                <input
                  type="text"
                  placeholder="Search transcripts..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full px-4 py-3 rounded-lg bg-slate-800/50 border border-cyan-500/30 text-white placeholder-slate-700 focus:outline-none focus:ring-2 focus:ring-cyan-500 backdrop-blur-lg"
                />
              </div>

              {/* Transcript List */}
              <div className="space-y-3 max-h-[calc(100vh-300px)] overflow-y-auto">
                {transcripts.map((transcript, idx) => (
                  <button
                    key={transcript.id}
                    onClick={() => setSelectedTranscript(transcript.id)}
                    className={`w-full text-left p-4 rounded-xl transition-all border-2 ${
                      selectedTranscript === transcript.id
                        ? 'bg-cyan-500/10 border-cyan-500/50 shadow-lg shadow-cyan-500/20'
                        : 'bg-slate-800/30 border-cyan-500/10 hover:border-cyan-500/30'
                    }`}
                    style={{animation: `slide-in-left 0.5s ease-out ${idx * 0.05}s both`}}
                  >
                    <h3 className="font-semibold text-white mb-1">{transcript.title}</h3>
                    <p className="text-xs text-slate-800 mb-2">{transcript.date}</p>
                    <div className="flex gap-2 flex-wrap">
                      {transcript.speakers.map((speaker) => (
                        <span key={speaker} className="text-xs px-2 py-1 rounded bg-purple-500/20 text-purple-300">
                          {speaker.split(' ')[0]}
                        </span>
                      ))}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Right Column - Transcript Viewer */}
            {currentTranscript && (
              <div className="lg:col-span-2">
                <div className="premium-card rounded-2xl p-8 border-2 border-cyan-500/20 h-full">
                  {/* Transcript Header */}
                  <div className="flex items-start justify-between mb-8 pb-6 border-b border-cyan-500/10">
                    <div>
                      <h2 className="font-display text-2xl font-bold text-white mb-2">{currentTranscript.title}</h2>
                      <p className="text-slate-800 text-sm">{currentTranscript.date} • {currentTranscript.duration}</p>
                    </div>
                    <Button className="bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 text-white font-bold shadow-lg shadow-cyan-500/50">
                      📥 Export
                    </Button>
                  </div>

                  {/* Transcript Content */}
                  <div className="space-y-6 max-h-[calc(100vh-400px)] overflow-y-auto pr-4">
                    {currentTranscript.segments.map((segment, idx) => (
                      <div
                        key={idx}
                        className="p-4 rounded-lg bg-slate-800/30 border border-cyan-500/10 hover:border-cyan-500/30 transition-all"
                        style={{animation: `scroll-reveal 0.5s ease-out ${idx * 0.05}s both`}}
                      >
                        <div className="flex items-start gap-4">
                          <div className="flex-shrink-0">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold">
                              {segment.speaker.charAt(0)}
                            </div>
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-semibold text-white">{segment.speaker}</span>
                              <span className="text-xs text-slate-800">{segment.time}</span>
                            </div>
                            <p className="text-black text-sm leading-relaxed">
                              {segment.text}
                            </p>
                            {segment.text.includes('[PII REDACTED') && (
                              <span className="inline-block mt-2 text-xs px-2 py-1 rounded bg-orange-500/20 text-orange-300 border border-orange-500/30">
                                🔒 PII Redacted
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
