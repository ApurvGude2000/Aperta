import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Navigation } from '../components/design-system/Navigation';
import { Card } from '../components/design-system/Card';
import { Button } from '../components/design-system/Button';
import { api } from '../api/client';

export function Dashboard() {
  const [metrics, setMetrics] = useState<any[]>([]);
  const [activityFeed, setActivityFeed] = useState<any[]>([]);
  const [followUps, setFollowUps] = useState<any[]>([]);
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Q&A state
  const [selectedEvent, setSelectedEvent] = useState<string>('all');
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [askingQuestion, setAskingQuestion] = useState(false);
  const [routedAgents, setRoutedAgents] = useState<string[]>([]);
  const [executionTime, setExecutionTime] = useState<number>(0);
  const [questionType, setQuestionType] = useState<string>('');

  const suggestedQuestions = [
    'Who should I follow up with and what should I say?',
    'What were the key topics discussed and what patterns do you see?',
    'Compare my conversations - who had the most actionable discussion?',
  ];

  useEffect(() => {
    fetchDashboardData();
    fetchFollowUps();
    fetchEvents();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const data = await api.getDashboardMetrics();
      setMetrics(data.metrics || []);
      setActivityFeed(data.recent_activity || []);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setMetrics([]);
      setActivityFeed([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchFollowUps = async () => {
    try {
      const data = await api.getFollowUpSuggestions(3);
      setFollowUps(data.suggestions || []);
    } catch (error) {
      console.error('Error fetching follow-ups:', error);
      setFollowUps([]);
    }
  };

  const fetchEvents = async () => {
    try {
      const conversations = await api.getConversations();
      setEvents(conversations || []);
    } catch (error) {
      console.error('Error fetching events:', error);
      setEvents([]);
    }
  };

  const handleAskQuestion = async (questionText: string) => {
    if (!questionText.trim()) return;

    setAskingQuestion(true);
    setQuestion(questionText);
    setAnswer('');
    setRoutedAgents([]);
    setExecutionTime(0);
    setQuestionType('');

    try {
      const requestPayload = {
        question: questionText,
        conversation_id: selectedEvent !== 'all' ? selectedEvent : undefined,
        use_rag: true
      };

      const response = await api.askQuestion(requestPayload);

      setAnswer(response.final_answer);
      setRoutedAgents(response.routed_agents || []);
      setExecutionTime(response.execution_time || 0);
      setQuestionType(response.agent_trace?.routing?.question_type || '');
    } catch (error: any) {
      setAnswer(`Sorry, I encountered an error processing your question. ${error?.response?.data?.detail || error?.message || 'Please try again.'}`);
      setRoutedAgents([]);
    } finally {
      setAskingQuestion(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'hot': return 'bg-red-100 text-red-700 border-red-200';
      case 'warm': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'cold': return 'bg-blue-100 text-blue-700 border-blue-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  return (
    <div className="min-h-screen bg-[#F5F7FA]">
      <Navigation isAuthenticated={true} />

      <main className="max-w-7xl mx-auto p-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="font-display text-3xl font-bold text-[#121417] mb-2">Dashboard</h1>
            <p className="text-[#6B7280]">Welcome back! Here's your networking overview.</p>
          </div>

          {/* Ask Aperta Section */}
          <Card className="mb-8">
            <div className="flex items-center gap-3 mb-6">
              <img src="/TH_logo.png" alt="Aperta" className="h-8" />
              <div>
                <h2 className="font-bold text-xl text-[#121417]">Ask Aperta</h2>
                <p className="text-sm text-[#6B7280]">Get insights from your conversations</p>
              </div>
            </div>

            {/* Event Selector */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-[#121417] mb-2">
                Select Event (Optional)
              </label>
              <select
                value={selectedEvent}
                onChange={(e) => setSelectedEvent(e.target.value)}
                className="w-full px-4 py-2 rounded-lg border border-[#E5E7EB] focus:outline-none focus:ring-2 focus:ring-[#1F3C88]"
              >
                <option value="all">All Events</option>
                {events.map((event) => (
                  <option key={event.id} value={event.id}>
                    {event.title?.replace('.txt', '').replace(/_/g, ' ') || 'Untitled Event'}
                  </option>
                ))}
              </select>
            </div>

            {/* Suggested Questions */}
            <div className="mb-4">
              <p className="text-xs font-medium text-[#6B7280] uppercase mb-3">Suggested Questions:</p>
              <div className="grid md:grid-cols-3 gap-2">
                {suggestedQuestions.map((q, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleAskQuestion(q)}
                    disabled={askingQuestion}
                    className="text-left text-sm p-3 rounded-lg bg-[#F5F7FA] hover:bg-[#E5E7EB] text-[#121417] transition-colors disabled:opacity-50"
                  >
                    • {q}
                  </button>
                ))}
              </div>
            </div>

            {/* Question Input */}
            <div className="flex gap-2">
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAskQuestion(question)}
                placeholder="Ask a question about your conversations..."
                disabled={askingQuestion}
                className="flex-1 px-4 py-3 rounded-lg border border-[#E5E7EB] focus:outline-none focus:ring-2 focus:ring-[#1F3C88] disabled:opacity-50"
              />
              <Button
                onClick={() => handleAskQuestion(question)}
                disabled={askingQuestion || !question.trim()}
              >
                {askingQuestion ? 'Asking...' : 'Ask'}
              </Button>
            </div>

            {/* Answer Display */}
            {answer && (
              <div className="mt-4 p-4 bg-gradient-to-r from-[#1F3C88]/5 to-[#00C2FF]/5 rounded-lg border border-[#1F3C88]/20">
                {/* Agent Trace Bar */}
                {routedAgents.length > 0 && (
                  <div className="flex flex-wrap items-center gap-2 mb-3 pb-3 border-b border-[#1F3C88]/10">
                    <span className="text-xs font-medium text-[#6B7280]">Agents:</span>
                    {routedAgents.map((agent, idx) => (
                      <span
                        key={idx}
                        className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                          agent === 'conversation_retrieval' ? 'bg-blue-100 text-blue-700' :
                          agent === 'insight' ? 'bg-purple-100 text-purple-700' :
                          agent === 'followup' ? 'bg-green-100 text-green-700' :
                          agent === 'recommendation' ? 'bg-orange-100 text-orange-700' :
                          'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {agent === 'conversation_retrieval' ? 'Retrieval' :
                         agent === 'followup' ? 'Follow-Up' :
                         agent === 'insight' ? 'Insight' :
                         agent === 'recommendation' ? 'Recommendation' :
                         agent}
                      </span>
                    ))}
                    {questionType && (
                      <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-[#1F3C88]/10 text-[#1F3C88]">
                        {questionType}
                      </span>
                    )}
                    {executionTime > 0 && (
                      <span className="text-xs text-[#9CA3AF] ml-auto">
                        {executionTime.toFixed(1)}s
                      </span>
                    )}
                  </div>
                )}
                <p className="text-sm font-medium text-[#1F3C88] mb-2">Answer:</p>
                <p className="text-[#121417] whitespace-pre-wrap">{answer}</p>
              </div>
            )}
          </Card>

          {/* Activity Feed and Follow-ups */}
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Activity Feed */}
            <div className="lg:col-span-2">
              <Card className="p-0">
                <div className="p-6 border-b border-[#E5E7EB]">
                  <h2 className="font-bold text-lg text-[#121417]">Recent Activity</h2>
                </div>

                <div className="divide-y divide-[#E5E7EB]">
                  {loading ? (
                    <div className="p-6">
                      <p className="text-[#6B7280]">Loading activity...</p>
                    </div>
                  ) : activityFeed.length === 0 ? (
                    <div className="p-6 text-center">
                      <p className="text-[#6B7280]">No recent activity</p>
                      <p className="text-sm text-[#9CA3AF] mt-2">Start by adding a conversation or event</p>
                    </div>
                  ) : (
                    activityFeed.map((item, idx) => (
                      <Link
                        key={idx}
                        to={item.link}
                        className="block p-6 hover:bg-[#F5F7FA] transition-colors cursor-pointer"
                      >
                        <div className="flex gap-4">
                          <div className="text-2xl">{item.icon}</div>
                          <div className="flex-1">
                            <h3 className="font-medium text-[#121417]">{item.title}</h3>
                            {item.subtitle && (
                              <p className="text-sm text-[#6B7280] mt-1">{item.subtitle}</p>
                            )}
                            {item.description && (
                              <p className="text-sm text-[#6B7280] mt-1">{item.description}</p>
                            )}
                            <p className="text-xs text-[#9CA3AF] mt-2">{item.time}</p>
                          </div>
                        </div>
                      </Link>
                    ))
                  )}
                </div>
              </Card>
            </div>

            {/* Follow-ups Section */}
            <div>
              <Card>
                <div className="mb-6">
                  <h2 className="font-bold text-lg text-[#121417] mb-2">Suggested Follow-ups</h2>
                  <p className="text-xs text-[#6B7280]">AI-recommended people to reach out to</p>
                </div>

                <div className="space-y-4">
                  {followUps.map((person, idx) => (
                    <div
                      key={idx}
                      className="p-4 rounded-lg border border-[#E5E7EB] hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <h3 className="font-medium text-[#121417]">{person.name}</h3>
                          {person.company && (
                            <p className="text-xs text-[#6B7280]">{person.company}</p>
                          )}
                        </div>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getPriorityColor(person.priority)}`}>
                          {person.priority}
                        </span>
                      </div>

                      <p className="text-xs text-[#6B7280] mb-3">{person.reason}</p>

                      {person.last_interaction && (
                        <p className="text-xs text-[#9CA3AF] mb-3">Last contact: {person.last_interaction}</p>
                      )}

                      {person.email && (
                        <Button size="sm" variant="secondary" className="w-full">
                          Send Follow-up
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          </div>
      </main>
    </div>
  );
}
