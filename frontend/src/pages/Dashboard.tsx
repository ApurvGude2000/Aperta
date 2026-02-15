import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Navigation } from '../components/design-system/Navigation';
import { Sidebar } from '../components/design-system/Sidebar';
import { Button } from '../components/design-system/Button';

export function Dashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [followUps, setFollowUps] = useState([
    { id: 1, eventName: 'TechCrunch Disrupt', action: 'Followed up via email', completed: false },
    { id: 2, eventName: 'YC Demo Day', action: 'Scheduled coffee chat', completed: true },
    { id: 3, eventName: 'Stanford AI Conference', action: 'Waiting for response', completed: false },
  ]);
  const [customAction, setCustomAction] = useState('');

  const metrics = [
    { icon: '👥', label: 'People Met', value: 42, trend: '+12 this week' },
    { icon: '💬', label: 'Conversations', value: 18, trend: '+5 this week' },
    { icon: '✅', label: 'Follow-ups Sent', value: 15, trend: '+3 this week' },
    { icon: '🤝', label: 'Active Connections', value: 34, trend: '+8 this month' },
  ];

  const recentEvents = [
    {
      id: 1,
      name: 'TechCrunch Disrupt',
      conversations: 12,
      duration: '3h 24m',
      date: 'March 15, 2024',
    },
    {
      id: 2,
      name: 'YC Demo Day',
      conversations: 15,
      duration: '5h 12m',
      date: 'March 10, 2024',
    },
    {
      id: 3,
      name: 'Stanford AI Conference',
      conversations: 7,
      duration: '2h 45m',
      date: 'February 28, 2024',
    },
  ];

  const toggleFollowUp = (id: number) => {
    setFollowUps(followUps.map(fu => fu.id === id ? { ...fu, completed: !fu.completed } : fu));
  };

  const addCustomFollowUp = () => {
    if (customAction.trim()) {
      setFollowUps([...followUps, {
        id: Math.max(...followUps.map(f => f.id), 0) + 1,
        eventName: 'Custom',
        action: customAction,
        completed: false,
      }]);
      setCustomAction('');
    }
  };

  const completedCount = followUps.filter(fu => fu.completed).length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-cyan-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-40 right-10 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
      </div>

      <Navigation isAuthenticated={true} />

      <div className="flex relative z-10">
        <Sidebar isOpen={sidebarOpen} />

        <main className="flex-1 p-8">
          {/* Header with Gradient */}
          <div className="mb-12 sticky-section">
            <h1 className="font-display text-5xl font-bold text-white mb-2">Dashboard</h1>
            <p className="text-black text-lg">Welcome back! Here's your networking overview.</p>
          </div>

          {/* Metrics Grid with 3D Cards */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            {metrics.map((metric, idx) => (
              <div
                key={idx}
                className="group relative"
                style={{animation: `bounce-in 0.8s ease-out ${idx * 0.1}s both`}}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 to-purple-500/10 rounded-2xl blur-lg opacity-0 group-hover:opacity-100 transition-opacity"></div>
                <div className="premium-card p-8 border-2 border-cyan-500/10 relative z-10 rounded-2xl">
                  <div className="flex items-start justify-between mb-4">
                    <div className="text-5xl transform group-hover:scale-125 group-hover:rotate-12 transition-transform" style={{animation: 'float 6s ease-in-out infinite'}}>
                      {metric.icon}
                    </div>
                  </div>
                  <div className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent mb-2">
                    {metric.value}
                  </div>
                  <div className="text-sm font-semibold text-black mb-2">{metric.label}</div>
                  <div className="text-xs font-bold text-green-400">{metric.trend}</div>
                </div>
              </div>
            ))}
          </div>

          {/* Recent Events, Follow-ups and AI Assistant Grid */}
          <div className="grid lg:grid-cols-4 gap-8">
            {/* Recent Events */}
            <div className="lg:col-span-2">
              <div className="premium-card rounded-2xl p-8 border-2 border-cyan-500/20 overflow-hidden">
                <div className="pb-6 border-b border-cyan-500/10 mb-6">
                  <h2 className="font-display font-bold text-2xl text-white">Recent Events</h2>
                </div>

                <div className="space-y-4">
                  {recentEvents.map((event, idx) => (
                    <Link
                      key={event.id}
                      to={`/events/${event.id}`}
                      className="group block p-6 rounded-xl border-2 border-cyan-500/10 hover:border-cyan-500/30 bg-slate-800/30 hover:bg-slate-800/50 transition-all transform hover:scale-[1.02]"
                      style={{animation: `slide-in-left 0.6s ease-out ${idx * 0.1}s both`}}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <h3 className="font-bold text-lg text-white group-hover:text-transparent group-hover:bg-gradient-to-r group-hover:from-cyan-400 group-hover:to-purple-400 group-hover:bg-clip-text transition-all">
                            {event.name}
                          </h3>
                          <div className="flex gap-6 mt-2">
                            <span className="text-sm text-black">
                              💬 {event.conversations} <span className="text-black">conversations</span>
                            </span>
                            <span className="text-sm text-black">
                              ⏱️ {event.duration} <span className="text-black">duration</span>
                            </span>
                          </div>
                          <p className="text-xs text-black mt-2">{event.date}</p>
                        </div>
                        <div className="ml-4">
                          <span className="text-cyan-400 group-hover:text-cyan-300 transition-colors">→</span>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            </div>

            {/* Follow-up Checklist */}
            <div>
              <div className="premium-card sticky top-24 rounded-2xl p-8 border-2 border-purple-500/20">
                <div className="pb-6 border-b border-purple-500/10 mb-6">
                  <h2 className="font-display font-bold text-xl text-white">Follow-ups</h2>
                  <p className="text-sm text-black mt-1">{completedCount}/{followUps.length} completed</p>
                </div>

                <div className="space-y-3 mb-6">
                  {followUps.map((followUp) => (
                    <label
                      key={followUp.id}
                      className="flex items-start gap-3 p-3 rounded-lg hover:bg-slate-800/50 transition-all cursor-pointer group"
                    >
                      <input
                        type="checkbox"
                        checked={followUp.completed}
                        onChange={() => toggleFollowUp(followUp.id)}
                        className="mt-1 w-4 h-4 rounded border-cyan-500 text-cyan-500 focus:ring-cyan-500 cursor-pointer"
                      />
                      <div className="flex-1 min-w-0">
                        <p className={`text-sm font-medium ${followUp.completed ? 'text-black line-through' : 'text-black'}`}>
                          {followUp.action}
                        </p>
                        <p className="text-xs text-black">{followUp.eventName}</p>
                      </div>
                    </label>
                  ))}
                </div>

                <div className="space-y-2 pt-4 border-t border-purple-500/10">
                  <input
                    type="text"
                    placeholder="Add custom follow-up..."
                    value={customAction}
                    onChange={(e) => setCustomAction(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && addCustomFollowUp()}
                    className="w-full px-3 py-2 rounded-lg bg-slate-800/50 border border-purple-500/20 text-white placeholder-slate-700 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                  <Button
                    size="sm"
                    onClick={addCustomFollowUp}
                    className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold"
                  >
                    + Add
                  </Button>
                </div>
              </div>
            </div>

            {/* AI Assistant Sidebar */}
            <div>
              <div className="premium-card sticky top-24 rounded-2xl p-8 border-2 border-cyan-500/20">
                <div className="pb-6 border-b border-cyan-500/10 mb-6">
                  <h2 className="font-display font-bold text-xl text-white">🤖 Agent-Echo AI</h2>
                  <p className="text-sm text-black mt-1">Who you can talk to</p>
                </div>

                <div className="space-y-3">
                  <div className="p-4 bg-slate-800/30 rounded-lg border border-cyan-500/10 hover:border-cyan-500/30 transition-all cursor-pointer">
                    <p className="font-semibold text-white mb-1">💡 Get Suggestions</p>
                    <p className="text-xs text-slate-900 font-semibold">Smart follow-up ideas</p>
                  </div>

                  <div className="p-4 bg-slate-800/30 rounded-lg border border-cyan-500/10 hover:border-cyan-500/30 transition-all cursor-pointer">
                    <p className="font-semibold text-white mb-1">📧 Draft Messages</p>
                    <p className="text-xs text-slate-900 font-semibold">Personalized templates</p>
                  </div>

                  <div className="p-4 bg-slate-800/30 rounded-lg border border-cyan-500/10 hover:border-cyan-500/30 transition-all cursor-pointer">
                    <p className="font-semibold text-white mb-1">🎯 Find Connections</p>
                    <p className="text-xs text-slate-900 font-semibold">Mutual connections</p>
                  </div>

                  <div className="p-4 bg-slate-800/30 rounded-lg border border-cyan-500/10 hover:border-cyan-500/30 transition-all cursor-pointer">
                    <p className="font-semibold text-white mb-1">📊 Analytics</p>
                    <p className="text-xs text-slate-900 font-semibold">Networking insights</p>
                  </div>
                </div>

                <div className="space-y-3 mt-6">
                  <Link to="/#how-it-works">
                    <Button className="w-full bg-slate-700 hover:bg-slate-600 text-white font-bold">
                      Learn More
                    </Button>
                  </Link>
                  <Button className="w-full bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 text-white font-bold">
                    Chat with AI
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
