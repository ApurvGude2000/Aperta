import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Navigation } from '../components/design-system/Navigation';
import { Card } from '../components/design-system/Card';
import { Button } from '../components/design-system/Button';
import { api } from '../api/client';

type TabType = 'people' | 'followups' | 'intros';

export function EventDetailNew() {
  const { id } = useParams<{ id: string }>();
  const [activeTab, setActiveTab] = useState<TabType>('people');
  const [event, setEvent] = useState<any>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      fetchEventDetails();
    }
  }, [id]);

  const fetchEventDetails = async () => {
    try {
      setLoading(true);
      // Fetch conversation/event details
      const eventData = await api.getConversation(id!);
      setEvent(eventData);

      // TODO: Fetch agent analysis results if needed
      // const analysisData = await api.analyzeConversation(id!);
      // setAnalysis(analysisData);
    } catch (error) {
      console.error('Error fetching event details:', error);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'people', label: 'People', icon: '👥', agentName: 'Context Understanding' },
    { id: 'followups', label: 'Follow-up Message', icon: '📧', agentName: 'Follow-Up Agent' },
    { id: 'intros', label: 'Intros Suggested', icon: '🤝', agentName: 'Cross-Pollination' },
  ];

  const metrics = [
    { label: 'PEOPLE MET', value: event?.participants?.length || 0 },
    { label: 'CONVERSATIONS', value: event?.transcript ? 1 : 0 },
    { label: 'FOLLOW-UPS SENT', value: 0 }, // TODO: Get from follow-up messages
    { label: 'INTROS SUGGESTED', value: 0 }, // TODO: Get from cross-pollination agent
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F5F7FA]">
        <Navigation isAuthenticated={true} />
        <main className="max-w-7xl mx-auto p-8">
          <p className="text-[#6B7280]">Loading event details...</p>
        </main>
      </div>
    );
  }

  if (!event) {
    return (
      <div className="min-h-screen bg-[#F5F7FA]">
        <Navigation isAuthenticated={true} />
        <main className="max-w-7xl mx-auto p-8">
          <p className="text-[#6B7280]">Event not found</p>
        </main>
      </div>
    );
  }

  const eventTitle = event.title?.replace('.txt', '').replace(/_/g, ' ') || 'Untitled Event';

  return (
    <div className="min-h-screen bg-[#F5F7FA]">
      <Navigation isAuthenticated={true} />

      <main className="max-w-7xl mx-auto p-8">
          {/* Back Button */}
          <Link
            to="/events"
            className="inline-flex items-center gap-2 text-[#1F3C88] hover:text-[#00C2FF] mb-6 font-medium"
          >
            ← Back to Events
          </Link>

          {/* Event Title */}
          <h1 className="font-display text-4xl font-bold text-[#121417] mb-8">
            {eventTitle}
          </h1>

          {/* Metrics Grid */}
          <div className="grid md:grid-cols-4 gap-6 mb-8">
            {metrics.map((metric, idx) => (
              <Card key={idx}>
                <p className="text-xs font-medium text-[#6B7280] uppercase mb-2">
                  {metric.label}
                </p>
                <p className="text-4xl font-bold text-[#00C2FF]">{metric.value}</p>
              </Card>
            ))}
          </div>

          {/* Tabs */}
          <div className="border-b border-[#E5E7EB] mb-6">
            <div className="flex gap-8">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as TabType)}
                  className={`
                    flex items-center gap-2 px-4 py-3 border-b-2 font-medium transition-colors
                    ${
                      activeTab === tab.id
                        ? 'border-[#1F3C88] text-[#1F3C88]'
                        : 'border-transparent text-[#6B7280] hover:text-[#1F3C88]'
                    }
                  `}
                >
                  <span className="text-lg">{tab.icon}</span>
                  <span>{tab.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Tab Content */}
          <div>
            {/* People Tab */}
            {activeTab === 'people' && (
              <div className="grid md:grid-cols-3 gap-6">
                {event.participants && event.participants.length > 0 ? (
                  event.participants.map((person: any, idx: number) => (
                    <Card key={idx}>
                      <div className="flex items-start gap-3 mb-4">
                        <div className="text-3xl">👤</div>
                        <div className="flex-1">
                          <h3 className="font-bold text-[#121417]">{person.name || 'Unknown'}</h3>
                          {person.title && person.company && (
                            <p className="text-sm text-[#6B7280]">
                              {person.title}, {person.company}
                            </p>
                          )}
                          {person.linkedin_url && (
                            <p className="text-xs text-[#00C2FF] mt-1">🔗 LinkedIn Connected</p>
                          )}
                        </div>
                      </div>

                      {person.email && (
                        <p className="text-xs text-[#6B7280] mb-4">📧 {person.email}</p>
                      )}

                      <div className="space-y-2">
                        <Button variant="secondary" size="sm" className="w-full">
                          View Conversation
                        </Button>
                        <Button size="sm" className="w-full">
                          Generate Follow-up
                        </Button>
                      </div>
                    </Card>
                  ))
                ) : (
                  <Card className="col-span-3 text-center py-12">
                    <p className="text-[#6B7280]">No participants extracted yet</p>
                    <p className="text-sm text-[#9CA3AF] mt-2">
                      Run the Context Understanding Agent to extract people from this conversation
                    </p>
                  </Card>
                )}
              </div>
            )}


            {/* Follow-ups Tab */}
            {activeTab === 'followups' && (
              <div className="grid md:grid-cols-3 gap-6">
                {event.participants && event.participants.length > 0 ? (
                  event.participants.map((person: any, idx: number) => (
                    <Card key={idx}>
                      <div className="flex items-start gap-3 mb-4">
                        <div className="text-3xl">👤</div>
                        <div>
                          <h3 className="font-bold text-[#121417]">{person.name || 'Unknown'}</h3>
                          {person.company && (
                            <p className="text-sm text-[#6B7280]">{person.company}</p>
                          )}
                        </div>
                      </div>

                      <div className="bg-[#F5F7FA] rounded-lg p-4 mb-4">
                        <p className="text-xs text-[#6B7280] mb-2">Generated Follow-up:</p>
                        <p className="text-sm text-[#121417]">
                          Click "Generate Follow-up" to create a personalized message using AI.
                        </p>
                      </div>

                      <Button size="sm" className="w-full">
                        Generate Follow-up
                      </Button>
                    </Card>
                  ))
                ) : (
                  <Card className="col-span-3 text-center py-12">
                    <p className="text-[#6B7280]">No participants to follow up with</p>
                    <p className="text-sm text-[#9CA3AF] mt-2">
                      Extract people first to generate follow-up messages
                    </p>
                  </Card>
                )}
              </div>
            )}

            {/* Intros Tab */}
            {activeTab === 'intros' && (
              <div className="grid md:grid-cols-3 gap-6">
                <Card className="col-span-3 text-center py-12">
                  <p className="text-[#6B7280]">Introduction suggestions coming soon</p>
                  <p className="text-sm text-[#9CA3AF] mt-2">
                    Run the Cross-Pollination Agent to find introduction opportunities
                  </p>
                </Card>
              </div>
            )}
          </div>
      </main>
    </div>
  );
}
