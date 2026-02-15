import React, { useState } from 'react';
import { Navigation } from '../components/design-system/Navigation';
import { Sidebar } from '../components/design-system/Sidebar';
import { Card } from '../components/design-system/Card';
import { Button } from '../components/design-system/Button';

export function Dashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const metrics = [
    { icon: '👥', label: 'People Met', value: 42, trend: '+12 this week' },
    { icon: '💬', label: 'Conversations', value: 18, trend: '+5 this week' },
    { icon: '✅', label: 'Follow-ups Sent', value: 15, trend: '+3 this week' },
    { icon: '🤝', label: 'Active Connections', value: 34, trend: '+8 this month' },
  ];

  const activityFeed = [
    {
      icon: '📅',
      title: 'TechCrunch Disrupt',
      subtitle: 'March 15, 2024',
      description: 'Met 6 people',
      time: '2 hours ago',
    },
    {
      icon: '📧',
      title: 'Follow-up sent to Alice Chen',
      time: '2 hours ago',
    },
    {
      icon: '🤝',
      title: 'Introduction suggestion',
      subtitle: 'Connect Alice & Bob',
      time: '4 hours ago',
    },
    {
      icon: '📊',
      title: 'New analytics available',
      subtitle: 'YC Demo Day insights',
      time: '1 day ago',
    },
  ];

  return (
    <div className="min-h-screen bg-[#F5F7FA]">
      <Navigation isAuthenticated={true} />

      <div className="flex">
        <Sidebar isOpen={sidebarOpen} />

        <main className="flex-1 p-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="font-display text-3xl font-bold text-[#121417] mb-2">Dashboard</h1>
            <p className="text-[#6B7280]">Welcome back! Here's your networking overview.</p>
          </div>

          {/* Metrics Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {metrics.map((metric, idx) => (
              <Card key={idx}>
                <div className="flex items-start justify-between mb-4">
                  <div className="text-4xl">{metric.icon}</div>
                </div>
                <div className="text-3xl font-bold text-[#121417] mb-2">{metric.value}</div>
                <div className="text-sm text-[#6B7280] mb-2">{metric.label}</div>
                <div className="text-xs text-[#10B981] font-medium">{metric.trend}</div>
              </Card>
            ))}
          </div>

          {/* Activity Feed and AI Assistant */}
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Activity Feed */}
            <div className="lg:col-span-2">
              <Card className="p-0">
                <div className="p-6 border-b border-[#E5E7EB]">
                  <div className="flex items-center justify-between">
                    <h2 className="font-bold text-lg text-[#121417]">Recent Activity</h2>
                    <div className="flex gap-4">
                      <select className="text-sm px-3 py-1 border border-[#E5E7EB] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#00C2FF]">
                        <option>All</option>
                        <option>Events</option>
                        <option>Follow-ups</option>
                      </select>
                      <select className="text-sm px-3 py-1 border border-[#E5E7EB] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#00C2FF]">
                        <option>Newest</option>
                        <option>Oldest</option>
                      </select>
                    </div>
                  </div>
                </div>

                <div className="divide-y divide-[#E5E7EB]">
                  {activityFeed.map((item, idx) => (
                    <div
                      key={idx}
                      className="p-6 hover:bg-[#F5F7FA] transition-colors cursor-pointer"
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
                    </div>
                  ))}
                </div>
              </Card>
            </div>

            {/* AI Assistant Sidebar */}
            <div>
              <Card className="sticky top-24">
                <div className="mb-6">
                  <div className="flex items-center gap-2 mb-4">
                    <div className="text-2xl">🤖</div>
                    <h2 className="font-bold text-[#121417]">Ask Agent-Echo</h2>
                  </div>
                  <p className="text-xs text-[#6B7280]">Ask me anything about your conversations</p>
                </div>

                <div className="space-y-3 mb-6">
                  <p className="text-xs font-medium text-[#6B7280] uppercase">Suggested questions:</p>
                  {[
                    'Who should I follow up with?',
                    'What trends am I seeing?',
                    'Show my top connections',
                  ].map((q, idx) => (
                    <button
                      key={idx}
                      className="w-full text-left text-sm p-3 rounded-lg bg-[#F5F7FA] hover:bg-[#E5E7EB] text-[#121417] transition-colors"
                    >
                      • {q}
                    </button>
                  ))}
                </div>

                <div className="space-y-2">
                  <input
                    type="text"
                    placeholder="Type a question..."
                    className="w-full px-4 py-2 rounded-lg border border-[#E5E7EB] focus:outline-none focus:ring-2 focus:ring-[#00C2FF] text-sm"
                  />
                  <Button size="sm" className="w-full">
                    Ask
                  </Button>
                </div>
              </Card>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
