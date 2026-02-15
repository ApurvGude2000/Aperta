import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Navigation } from '../components/design-system/Navigation';
import { Sidebar } from '../components/design-system/Sidebar';
import { Button } from '../components/design-system/Button';

export function EventDetail() {
  const [activeTab, setActiveTab] = useState<'people' | 'conversations' | 'followup' | 'improvement' | 'linkedin' | 'analytics'>('people');
  const [improvements, setImprovements] = useState<string>('');
  const [linkedInSearch, setLinkedInSearch] = useState<string>('');

  const tabs = [
    { id: 'people', label: 'People', icon: '👥' },
    { id: 'conversations', label: 'Conversations', icon: '💬' },
    { id: 'followup', label: 'Follow-up Message', icon: '✉️' },
    { id: 'improvement', label: 'Improvement', icon: '💡' },
    { id: 'linkedin', label: 'Find LinkedIn', icon: '🔗' },
    { id: 'analytics', label: 'Analytics', icon: '📊' },
  ];

  const people = [
    {
      id: 1,
      name: 'Alice Chen',
      title: 'Partner, Acme VC',
      avatar: '👩‍💼',
      met: 'March 15, 10:30 AM',
      duration: '24 minutes',
      topics: ['AI Safety', 'Funding'],
      linkedIn: true,
    },
    {
      id: 2,
      name: 'Bob Smith',
      title: 'Founder, TechCorp',
      avatar: '👨‍💼',
      met: 'March 15, 11:00 AM',
      duration: '18 minutes',
      topics: ['Product Dev', 'Series A'],
      linkedIn: false,
    },
    {
      id: 3,
      name: 'Unknown Person #1',
      title: 'No identification',
      avatar: '❓',
      met: 'March 15, 11:45 AM',
      duration: '8 minutes',
      topics: ['Product Development'],
      linkedIn: false,
    },
  ];

  const conversations = [
    {
      id: 1,
      person: 'Alice Chen',
      time: '10:30 AM - 10:54 AM',
      topics: ['AI Safety', 'Series A', 'GDPR'],
      sentiment: 'Positive',
      redactions: 3,
    },
    {
      id: 2,
      person: 'Bob Smith',
      time: '11:00 AM - 11:18 AM',
      topics: ['Product Development', 'Funding'],
      sentiment: 'Positive',
      redactions: 2,
    },
  ];

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
            <Link to="/events" className="text-cyan-400 hover:text-cyan-300 font-medium mb-4 inline-block">
              ← Back to Events
            </Link>
            <div className="flex items-start justify-between mb-6">
              <div>
                <h1 className="font-display text-5xl font-bold text-white mb-2">
                  TechCrunch Disrupt 2024
                </h1>
                <p className="text-slate-800 text-lg">March 15, 2024 • 3h 24m • Moscone Center</p>
              </div>
              <div className="flex gap-2">
                <Button variant="secondary" className="border-2 border-purple-400 text-purple-300 hover:bg-purple-500/10 font-bold">
                  Export PDF
                </Button>
                <Button className="bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 text-white font-bold shadow-lg shadow-cyan-500/50">
                  Share
                </Button>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-4 gap-4 mb-8">
              {[
                { label: 'People Met', value: 6 },
                { label: 'Conversations', value: 12 },
                { label: 'Follow-ups Sent', value: 5 },
                { label: 'Intros Suggested', value: 3 },
              ].map((stat, idx) => (
                <div
                  key={idx}
                  className="premium-card rounded-xl p-6 border-2 border-cyan-500/10"
                  style={{animation: `bounce-in 0.8s ease-out ${idx * 0.1}s both`}}
                >
                  <p className="text-xs text-slate-800 uppercase font-semibold mb-1">{stat.label}</p>
                  <p className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">{stat.value}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Tabs */}
          <div className="mb-8 border-b border-cyan-500/20">
            <div className="flex gap-0 overflow-x-auto">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`
                    px-6 py-4 font-medium text-sm border-b-2 transition-all whitespace-nowrap
                    ${
                      activeTab === tab.id
                        ? 'text-cyan-400 border-cyan-400'
                        : 'text-slate-800 border-transparent hover:text-cyan-300'
                    }
                  `}
                >
                  {tab.icon} {tab.label}
                </button>
              ))}
            </div>
          </div>

          {/* Tab Content: People */}
          {activeTab === 'people' && (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {people.map((person, idx) => (
                <div
                  key={person.id}
                  className="group relative premium-card rounded-2xl p-8 border-2 border-cyan-500/10 h-full hover:border-cyan-500/30 hover:shadow-2xl hover:shadow-cyan-500/20 flex flex-col"
                  style={{animation: `slide-in-left 0.8s ease-out ${idx * 0.1}s both`}}
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/5 to-purple-500/5 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>

                  <div className="relative flex-1">
                    <div className="flex items-start gap-4 mb-4">
                      <div className="text-5xl">{person.avatar}</div>
                      <div className="flex-1">
                        <h3 className="font-bold text-white text-lg">{person.name}</h3>
                        <p className="text-sm text-slate-800">{person.title}</p>
                        {person.linkedIn && <p className="text-xs text-cyan-400 mt-1 font-semibold">🔗 LinkedIn Connected</p>}
                      </div>
                    </div>

                    <div className="space-y-2 text-sm mb-4 pb-4 border-t border-cyan-500/10">
                      <p className="text-slate-800 pt-3">🕐 {person.met}</p>
                      <p className="text-slate-800">⏱ {person.duration}</p>
                      <div className="flex flex-wrap gap-2 mt-3">
                        {person.topics.map((topic, idx) => (
                          <span key={idx} className="px-3 py-1 bg-cyan-500/10 rounded-full text-xs text-cyan-300 border border-cyan-500/20">
                            {topic}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="relative space-y-3">
                    <Button variant="secondary" className="w-full border-2 border-purple-400 text-purple-300 hover:bg-purple-500/10 font-bold">
                      View Conversation
                    </Button>
                    <Button className="w-full bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 text-white font-bold">
                      Generate Follow-up
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Tab Content: Conversations */}
          {activeTab === 'conversations' && (
            <div className="space-y-4">
              {conversations.map((conv, idx) => (
                <div
                  key={conv.id}
                  className="premium-card rounded-2xl p-8 border-2 border-cyan-500/10 hover:border-cyan-500/30 transition-all"
                  style={{animation: `scroll-reveal 0.5s ease-out ${idx * 0.1}s both`}}
                >
                  <div className="mb-4 pb-4 border-b border-cyan-500/10">
                    <h3 className="font-bold text-xl text-white">Conversation with {conv.person}</h3>
                    <p className="text-sm text-slate-800 mt-1">{conv.time}</p>
                  </div>

                  <div className="grid grid-cols-3 gap-4 mb-4">
                    <div>
                      <p className="text-xs text-slate-800 uppercase font-semibold mb-2">Topics</p>
                      <div className="flex flex-wrap gap-1">
                        {conv.topics.map((topic, idx) => (
                          <span key={idx} className="text-xs px-2 py-1 bg-cyan-500/10 rounded text-cyan-300 border border-cyan-500/20">
                            {topic}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <p className="text-xs text-slate-800 uppercase font-semibold mb-2">Sentiment</p>
                      <p className="text-sm font-bold text-green-400">😊 {conv.sentiment}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-800 uppercase font-semibold mb-2">Privacy</p>
                      <p className="text-sm font-bold text-green-400">🔒 {conv.redactions} items</p>
                    </div>
                  </div>

                  <Button variant="secondary" className="w-full border-2 border-purple-400 text-purple-300 hover:bg-purple-500/10 font-bold">
                    Expand Transcript ▼
                  </Button>
                </div>
              ))}
            </div>
          )}

          {/* Tab Content: Follow-up Message */}
          {activeTab === 'followup' && (
            <div className="space-y-6">
              <div className="premium-card rounded-2xl p-8 border-2 border-cyan-500/20">
                <h3 className="font-display text-2xl font-bold text-white mb-6">Personalized Follow-up Messages</h3>
                <div className="space-y-4">
                  {people
                    .filter((p) => !p.linkedIn)
                    .map((person, idx) => (
                      <div
                        key={person.id}
                        className="bg-slate-800/30 rounded-lg p-6 border border-cyan-500/10"
                        style={{animation: `slide-in-left 0.5s ease-out ${idx * 0.1}s both`}}
                      >
                        <h4 className="font-bold text-white text-lg">{person.name}</h4>
                        <p className="text-sm text-black mt-1">{person.title}</p>
                        <div className="mt-4 space-y-3">
                          <div>
                            <p className="text-xs text-slate-800 mb-2 font-semibold">💼 Option 1 (Professional):</p>
                            <p className="text-sm text-black p-3 bg-slate-800/50 rounded border border-cyan-500/20">
                              "Hi {person.name}, it was great discussing {person.topics[0]} at TechCrunch. I'd love to continue the conversation."
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-slate-800 mb-2 font-semibold">🤝 Option 2 (Friendly):</p>
                            <p className="text-sm text-black p-3 bg-slate-800/50 rounded border border-cyan-500/20">
                              "Hey {person.name}! Had a great time chatting at the event. Let's grab coffee and dive deeper into {person.topics[0]}?"
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-slate-800 mb-2 font-semibold">✨ Option 3 (Specific):</p>
                            <p className="text-sm text-black p-3 bg-slate-800/50 rounded border border-cyan-500/20">
                              "Following up from our chat about {person.topics[0]} and {person.topics[1]}. I think there's a great opportunity to collaborate."
                            </p>
                          </div>
                        </div>
                        <div className="flex gap-2 mt-4">
                          <Button variant="secondary" className="flex-1 border-2 border-purple-400 text-purple-300 hover:bg-purple-500/10 font-bold text-sm">
                            📋 Copy
                          </Button>
                          <Button className="flex-1 bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 text-white font-bold text-sm">
                            📧 Send Email
                          </Button>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          )}

          {/* Tab Content: Improvement */}
          {activeTab === 'improvement' && (
            <div className="space-y-6">
              <div className="premium-card rounded-2xl p-8 border-2 border-cyan-500/20">
                <h3 className="font-display text-2xl font-bold text-white mb-6">💡 Reflection & Improvement</h3>
                <div className="space-y-4">
                  <div className="p-4 rounded-lg bg-slate-800/30 border border-cyan-500/10">
                    <p className="text-sm font-semibold text-black mb-3">✅ What went well</p>
                    <textarea
                      placeholder="Note what went well in your conversations..."
                      defaultValue="Had great technical discussions, good rapport with attendees"
                      className="w-full px-3 py-2 rounded bg-slate-800/50 border border-cyan-500/20 text-black text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 placeholder-slate-700"
                      rows={3}
                    />
                  </div>

                  <div className="p-4 rounded-lg bg-slate-800/30 border border-cyan-500/10">
                    <p className="text-sm font-semibold text-black mb-3">🎯 What could be improved</p>
                    <textarea
                      placeholder="What could you do better next time?..."
                      defaultValue="Could have prepared more specific talking points, should follow up faster"
                      className="w-full px-3 py-2 rounded bg-slate-800/50 border border-cyan-500/20 text-black text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 placeholder-slate-700"
                      rows={3}
                    />
                  </div>

                  <div className="p-4 rounded-lg bg-slate-800/30 border border-cyan-500/10">
                    <p className="text-sm font-semibold text-black mb-3">📝 Notes for next time</p>
                    <textarea
                      placeholder="Personal reminders for future networking..."
                      defaultValue="Remember to ask more questions, listen more than talk"
                      className="w-full px-3 py-2 rounded bg-slate-800/50 border border-cyan-500/20 text-black text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 placeholder-slate-700"
                      rows={3}
                    />
                  </div>

                  <Button className="w-full bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 text-white font-bold">
                    💾 Save Reflection
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* Tab Content: Find LinkedIn */}
          {activeTab === 'linkedin' && (
            <div className="space-y-6">
              <div className="premium-card rounded-2xl p-8 border-2 border-cyan-500/20">
                <h3 className="font-display text-2xl font-bold text-white mb-6">🔗 Find LinkedIn Profiles</h3>

                <div className="mb-6">
                  <input
                    type="text"
                    placeholder="Search person name or company..."
                    value={linkedInSearch}
                    onChange={(e) => setLinkedInSearch(e.target.value)}
                    className="w-full px-4 py-3 rounded-lg bg-slate-800/50 border border-cyan-500/30 text-white placeholder-slate-700 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 mb-4"
                  />
                </div>

                <div className="space-y-4">
                  {[
                    { name: 'Alice Chen', company: 'Acme Ventures', title: 'Partner', connected: false },
                    { name: 'Bob Smith', company: 'TechCorp', title: 'Founder', connected: true },
                  ].map((person, idx) => (
                    <div
                      key={idx}
                      className="bg-slate-800/30 rounded-lg p-6 border border-cyan-500/10 hover:border-cyan-500/30 transition-all"
                      style={{animation: `slide-in-left 0.5s ease-out ${idx * 0.1}s both`}}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h4 className="font-bold text-white text-lg">{person.name}</h4>
                          <p className="text-sm text-black">{person.title} at {person.company}</p>
                        </div>
                        {person.connected && (
                          <span className="text-xs px-3 py-1 rounded-full bg-green-500/20 text-green-300 border border-green-500/30">
                            ✓ Connected
                          </span>
                        )}
                      </div>
                      <div className="flex gap-2 mt-4">
                        <Button variant="secondary" className="flex-1 border-2 border-purple-400 text-purple-300 hover:bg-purple-500/10 font-bold text-sm">
                          🔗 View Profile
                        </Button>
                        <Button className={`flex-1 ${person.connected ? 'bg-gray-600 text-black' : 'bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white'} font-bold text-sm`}>
                          {person.connected ? '✓ Connected' : '+ Connect'}
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Tab Content: Analytics (replaced Insights) */}
          {activeTab === 'analytics' && (
            <div className="space-y-6">
              <div className="premium-card rounded-2xl p-8 border-2 border-cyan-500/20">
                <h3 className="font-display text-2xl font-bold text-white mb-6">📊 Event Analytics</h3>
                <div className="space-y-4">
                  <div className="p-4 rounded-lg bg-slate-800/30 border border-cyan-500/10">
                    <p className="text-sm font-semibold text-black mb-3">Key Topics</p>
                    <ul className="space-y-2 text-sm text-black">
                      <li>• AI Safety (mentioned 8x)</li>
                      <li>• Series A Funding (5x)</li>
                      <li>• GDPR Compliance (3x)</li>
                    </ul>
                  </div>

                  <div className="p-4 rounded-lg bg-slate-800/30 border border-cyan-500/10">
                    <p className="text-sm font-semibold text-black mb-2">Overall Sentiment</p>
                    <p className="text-lg text-green-400 font-bold">😊 Positive (87% confidence)</p>
                  </div>

                  <div className="p-4 rounded-lg bg-slate-800/30 border border-cyan-500/10">
                    <p className="text-sm font-semibold text-black mb-3">Performance Metrics</p>
                    <ul className="space-y-2 text-sm">
                      <li className="text-green-400 font-medium">✅ Found 3 potential investors</li>
                      <li className="text-green-400 font-medium">✅ Identified partnership opps</li>
                      <li className="text-orange-400 font-medium">⚠️ Need technical co-founder</li>
                    </ul>
                  </div>
                </div>
              </div>

              <div className="premium-card rounded-2xl p-8 border-2 border-cyan-500/20">
                <h3 className="font-display text-2xl font-bold text-white mb-6">🤝 Introduction Opportunities</h3>
                <div className="bg-slate-800/30 rounded-lg p-6 border border-cyan-500/10 mb-4">
                  <p className="font-semibold text-white mb-2">Alice Chen ↔ Bob Smith</p>
                  <p className="text-sm text-slate-800 mb-4">
                    Alice (Investor) is looking for healthcare AI startups. Bob (Founder) needs Series A funding.
                  </p>
                  <Button className="w-full bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 text-white font-bold">
                    Draft Introduction
                  </Button>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
