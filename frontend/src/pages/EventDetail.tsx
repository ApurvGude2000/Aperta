import React, { useState } from 'react';
import { Navigation } from '../components/design-system/Navigation';
import { Card } from '../components/design-system/Card';
import { Button } from '../components/design-system/Button';

export function EventDetail() {
  const [activeTab, setActiveTab] = useState<'people' | 'conversations' | 'linkedin' | 'insights' | 'graph' | 'analytics'>('people');

  const tabs = [
    { id: 'people', label: 'People', icon: '👥' },
    { id: 'conversations', label: 'Conversations', icon: '💬' },
    { id: 'linkedin', label: 'LinkedIn', icon: '🔗' },
    { id: 'insights', label: 'AI Insights', icon: '🧠' },
    { id: 'graph', label: 'Knowledge Graph', icon: '🕸️' },
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
    <div className="min-h-screen bg-[#F5F7FA]">
      <Navigation isAuthenticated={true} />

      <main className="max-w-7xl mx-auto p-8">
          {/* Header */}
          <div className="mb-8">
            <button className="text-[#00C2FF] font-medium mb-4">← Back to Events</button>
            <div className="flex items-start justify-between mb-6">
              <div>
                <h1 className="font-display text-4xl font-bold text-[#121417] mb-2">
                  TechCrunch Disrupt 2024
                </h1>
                <p className="text-[#6B7280]">March 15, 2024 • 3h 24m • Moscone Center</p>
              </div>
              <div className="flex gap-2">
                <Button variant="secondary" size="sm">
                  Export PDF
                </Button>
                <Button size="sm">Share</Button>
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
                <Card key={idx}>
                  <p className="text-xs text-[#6B7280] uppercase mb-1">{stat.label}</p>
                  <p className="text-2xl font-bold text-[#121417]">{stat.value}</p>
                </Card>
              ))}
            </div>
          </div>

          {/* Tabs */}
          <div className="mb-8">
            <div className="flex gap-0 border-b border-[#E5E7EB] overflow-x-auto">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`
                    px-6 py-4 font-medium text-sm border-b-2 transition-colors whitespace-nowrap
                    ${
                      activeTab === tab.id
                        ? 'text-[#1F3C88] border-[#00C2FF]'
                        : 'text-[#6B7280] border-transparent hover:text-[#1F3C88]'
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
              {people.map((person) => (
                <Card key={person.id} className="flex flex-col">
                  <div className="flex items-start gap-4 mb-4">
                    <div className="text-4xl">{person.avatar}</div>
                    <div className="flex-1">
                      <h3 className="font-bold text-[#121417]">{person.name}</h3>
                      <p className="text-sm text-[#6B7280]">{person.title}</p>
                      {person.linkedIn && <p className="text-xs text-[#00C2FF] mt-1">🔗 LinkedIn Connected</p>}
                    </div>
                  </div>

                  <div className="space-y-2 text-sm mb-4 pb-4 border-b border-[#E5E7EB]">
                    <p className="text-[#6B7280]">Met: {person.met}</p>
                    <p className="text-[#6B7280]">Duration: {person.duration}</p>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {person.topics.map((topic, idx) => (
                        <span key={idx} className="px-2 py-1 bg-[#F5F7FA] rounded text-xs text-[#121417]">
                          {topic}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Button variant="secondary" size="sm" className="w-full">
                      View Conversation
                    </Button>
                    <Button size="sm" className="w-full">
                      Generate Follow-up
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          )}

          {/* Tab Content: Conversations */}
          {activeTab === 'conversations' && (
            <div className="space-y-4">
              {conversations.map((conv) => (
                <Card key={conv.id}>
                  <div className="mb-4 pb-4 border-b border-[#E5E7EB]">
                    <h3 className="font-bold text-lg text-[#121417]">Conversation with {conv.person}</h3>
                    <p className="text-sm text-[#6B7280] mt-1">{conv.time}</p>
                  </div>

                  <div className="grid grid-cols-3 gap-4 mb-4">
                    <div>
                      <p className="text-xs text-[#6B7280] uppercase mb-1">Topics</p>
                      <div className="flex flex-wrap gap-1">
                        {conv.topics.map((topic, idx) => (
                          <span key={idx} className="text-xs px-2 py-1 bg-[#F5F7FA] rounded">
                            {topic}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <p className="text-xs text-[#6B7280] uppercase mb-1">Sentiment</p>
                      <p className="text-sm font-medium text-[#10B981]">😊 {conv.sentiment}</p>
                    </div>
                    <div>
                      <p className="text-xs text-[#6B7280] uppercase mb-1">Privacy</p>
                      <p className="text-sm font-medium text-[#10B981]">🔒 {conv.redactions} items</p>
                    </div>
                  </div>

                  <Button variant="secondary" size="sm" className="w-full">
                    Expand Transcript ▼
                  </Button>
                </Card>
              ))}
            </div>
          )}

          {/* Tab Content: LinkedIn */}
          {activeTab === 'linkedin' && (
            <div className="space-y-6">
              <Card>
                <h3 className="font-bold text-lg text-[#121417] mb-4">Ready to Connect</h3>
                <div className="space-y-4">
                  {people
                    .filter((p) => !p.linkedIn)
                    .map((person) => (
                      <Card key={person.id} className="bg-[#F5F7FA]">
                        <h4 className="font-bold text-[#121417]">{person.name}</h4>
                        <p className="text-sm text-[#6B7280] mt-1">{person.title}</p>
                        <div className="mt-4 p-3 bg-white rounded border border-[#E5E7EB]">
                          <p className="text-xs text-[#6B7280] mb-2">Suggested message:</p>
                          <p className="text-sm text-[#121417]">
                            "Hi {person.name}, great meeting you at TechCrunch Disrupt!"
                          </p>
                        </div>
                        <div className="flex gap-2 mt-4">
                          <Button size="sm" variant="secondary" className="flex-1">
                            Copy Message
                          </Button>
                          <Button size="sm" className="flex-1">
                            Open LinkedIn
                          </Button>
                        </div>
                      </Card>
                    ))}
                </div>
              </Card>
            </div>
          )}

          {/* Tab Content: Insights */}
          {activeTab === 'insights' && (
            <div className="space-y-6">
              <Card>
                <h3 className="font-bold text-lg text-[#121417] mb-4">🧠 Context Analysis</h3>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm font-medium text-[#121417] mb-2">Key Topics</p>
                    <ul className="space-y-1 text-sm text-[#6B7280]">
                      <li>• AI Safety (mentioned 8x)</li>
                      <li>• Series A Funding (5x)</li>
                      <li>• GDPR Compliance (3x)</li>
                    </ul>
                  </div>
                  <div className="pt-4 border-t border-[#E5E7EB]">
                    <p className="text-sm font-medium text-[#121417] mb-2">Overall Sentiment</p>
                    <p className="text-lg text-[#10B981] font-bold">😊 Positive (87% confidence)</p>
                  </div>
                  <div className="pt-4 border-t border-[#E5E7EB]">
                    <p className="text-sm font-medium text-[#121417] mb-2">Goal Alignment</p>
                    <ul className="space-y-1 text-sm">
                      <li className="text-[#10B981]">✅ Found 3 potential investors</li>
                      <li className="text-[#10B981]">✅ Identified partnership opps</li>
                      <li className="text-[#F59E0B]">⚠️ Need technical co-founder</li>
                    </ul>
                  </div>
                </div>
              </Card>

              <Card>
                <h3 className="font-bold text-lg text-[#121417] mb-4">🤝 Introduction Opportunities</h3>
                <Card className="bg-[#F5F7FA] mb-4">
                  <p className="font-medium text-[#121417] mb-2">Alice Chen ↔ Bob Smith</p>
                  <p className="text-sm text-[#6B7280] mb-4">
                    Alice (Investor) is looking for healthcare AI startups. Bob (Founder) needs Series A funding.
                  </p>
                  <Button size="sm" className="w-full">
                    Draft Introduction
                  </Button>
                </Card>
              </Card>
            </div>
          )}

          {/* Tab Content: Graph */}
          {activeTab === 'graph' && (
            <Card className="p-12 text-center">
              <p className="text-4xl mb-4">🕸️</p>
              <p className="text-lg font-medium text-[#121417] mb-2">Knowledge Graph</p>
              <p className="text-[#6B7280]">Interactive visualization showing connections between people, topics, and companies at this event</p>
            </Card>
          )}

          {/* Tab Content: Analytics */}
          {activeTab === 'analytics' && (
            <div className="grid md:grid-cols-2 gap-6">
              <Card>
                <h3 className="font-bold text-[#121417] mb-4">Time Distribution</h3>
                <p className="text-center text-[#6B7280] py-12">📊 Peak time: 11 AM - 12 PM (4 conversations)</p>
              </Card>
              <Card>
                <h3 className="font-bold text-[#121417] mb-4">Networking Effectiveness</h3>
                <div className="space-y-2">
                  <p className="text-sm text-[#6B7280]">Follow-up Rate: <span className="font-bold text-[#121417]">83% (5/6)</span></p>
                  <p className="text-sm text-[#6B7280]">Response Rate: <span className="font-bold text-[#121417]">60% (3/5)</span></p>
                  <p className="text-sm text-[#6B7280]">Connection Quality: <span className="font-bold text-[#10B981]">High</span></p>
                </div>
              </Card>
            </div>
          )}
        </main>
      </div>
  );
}
