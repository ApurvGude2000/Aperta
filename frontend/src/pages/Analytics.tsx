import React from 'react';
import { Navigation } from '../components/design-system/Navigation';
import { Sidebar } from '../components/design-system/Sidebar';

export function Analytics() {
  const metrics = [
    {
      label: 'Total Connections',
      value: '147',
      change: '+12%',
      icon: '👥',
      color: 'from-cyan-500 to-blue-500',
    },
    {
      label: 'Conversations',
      value: '342',
      change: '+28%',
      icon: '💬',
      color: 'from-purple-500 to-pink-500',
    },
    {
      label: 'Follow-up Rate',
      value: '78%',
      change: '+5%',
      icon: '📈',
      color: 'from-orange-400 to-pink-500',
    },
    {
      label: 'Response Rate',
      value: '82%',
      change: '+3%',
      icon: '✓',
      color: 'from-green-400 to-teal-500',
    },
  ];

  const weeklyData = [
    { day: 'Mon', conversations: 23, connections: 8 },
    { day: 'Tue', conversations: 28, connections: 12 },
    { day: 'Wed', conversations: 31, connections: 15 },
    { day: 'Thu', conversations: 27, connections: 10 },
    { day: 'Fri', conversations: 35, connections: 18 },
    { day: 'Sat', conversations: 19, connections: 6 },
    { day: 'Sun', conversations: 15, connections: 4 },
  ];

  const maxConversations = Math.max(...weeklyData.map(d => d.conversations));

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
            <h1 className="font-display text-5xl font-bold text-white mb-2">Analytics</h1>
            <p className="text-black text-lg">Track your networking performance and insights</p>
          </div>

          {/* Key Metrics Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            {metrics.map((metric, idx) => (
              <div
                key={idx}
                className="group relative premium-card rounded-2xl p-8 border-2 border-cyan-500/10 hover:border-cyan-500/30 hover:shadow-2xl hover:shadow-cyan-500/20 cursor-pointer"
                style={{animation: `bounce-in 0.8s ease-out ${idx * 0.1}s both`}}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/5 to-purple-500/5 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>

                <div className="relative">
                  <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${metric.color} flex items-center justify-center text-xl mb-4 shadow-lg transform group-hover:scale-125 transition-transform`}>
                    {metric.icon}
                  </div>
                  <p className="text-slate-800 text-sm mb-2">{metric.label}</p>
                  <p className="text-3xl font-bold text-white mb-2">{metric.value}</p>
                  <span className="text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-300 font-semibold">
                    {metric.change}
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Charts Section */}
          <div className="grid lg:grid-cols-2 gap-8 mb-12">
            {/* Weekly Activity Chart */}
            <div className="premium-card rounded-2xl p-8 border-2 border-cyan-500/20">
              <h2 className="font-display text-2xl font-bold text-white mb-6">Weekly Activity</h2>

              <div className="space-y-6">
                {weeklyData.map((data, idx) => {
                  const convHeight = (data.conversations / maxConversations) * 100;

                  return (
                    <div key={idx} className="space-y-2">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-medium text-black">{data.day}</span>
                        <span className="text-sm text-slate-800">{data.conversations} conversations</span>
                      </div>
                      <div className="w-full h-8 rounded-full bg-slate-800/50 border border-cyan-500/20 overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-cyan-500 to-purple-600 rounded-full transition-all duration-500"
                          style={{width: `${convHeight}%`, animation: `gradient-shift 3s ease-in-out infinite`}}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Performance Summary */}
            <div className="premium-card rounded-2xl p-8 border-2 border-cyan-500/20">
              <h2 className="font-display text-2xl font-bold text-white mb-6">Performance Summary</h2>

              <div className="space-y-6">
                <div className="p-4 rounded-lg bg-slate-800/30 border border-cyan-500/10">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-black font-medium">Avg. Conversation Length</span>
                    <span className="text-cyan-400 font-bold">24 min</span>
                  </div>
                  <p className="text-xs text-slate-800">↑ 5 min from last week</p>
                </div>

                <div className="p-4 rounded-lg bg-slate-800/30 border border-cyan-500/10">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-black font-medium">Events Attended</span>
                    <span className="text-cyan-400 font-bold">3</span>
                  </div>
                  <p className="text-xs text-slate-800">18 unique conversations</p>
                </div>

                <div className="p-4 rounded-lg bg-slate-800/30 border border-cyan-500/10">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-black font-medium">Pending Follow-ups</span>
                    <span className="text-orange-400 font-bold">7</span>
                  </div>
                  <p className="text-xs text-slate-800">2 overdue by 1+ days</p>
                </div>

                <div className="p-4 rounded-lg bg-slate-800/30 border border-cyan-500/10">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-black font-medium">Networking Score</span>
                    <span className="text-green-400 font-bold">8.5/10</span>
                  </div>
                  <p className="text-xs text-slate-800">Based on engagement & follow-ups</p>
                </div>
              </div>
            </div>
          </div>

          {/* Top Connections */}
          <div className="premium-card rounded-2xl p-8 border-2 border-cyan-500/20">
            <h2 className="font-display text-2xl font-bold text-white mb-6">Most Active Conversations</h2>

            <div className="space-y-3">
              {[
                { name: 'Sarah Johnson', conversations: 12, role: 'AI Safety Researcher' },
                { name: 'Michael Chen', conversations: 9, role: 'VC at Sequoia Capital' },
                { name: 'Lisa Rodriguez', conversations: 8, role: 'Product Manager at Google' },
                { name: 'James Wilson', conversations: 7, role: 'Founder at TechStartup' },
                { name: 'Emma Davis', conversations: 6, role: 'Head of AI at OpenAI' },
              ].map((person, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-4 rounded-lg bg-slate-800/30 border border-cyan-500/10 hover:border-cyan-500/30 transition-all"
                  style={{animation: `slide-in-left 0.5s ease-out ${idx * 0.05}s both`}}
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center text-white font-bold">
                      {person.name.charAt(0)}
                    </div>
                    <div>
                      <p className="font-semibold text-white">{person.name}</p>
                      <p className="text-xs text-slate-800">{person.role}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-cyan-400">{person.conversations}</p>
                    <p className="text-xs text-slate-800">conversations</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
