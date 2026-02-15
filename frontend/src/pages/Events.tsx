import React, { useState } from 'react';
import { Navigation } from '../components/design-system/Navigation';
import { Sidebar } from '../components/design-system/Sidebar';
import { Card } from '../components/design-system/Card';
import { Button } from '../components/design-system/Button';

export function Events() {
  const [viewMode, setViewMode] = useState<'list' | 'grid' | 'timeline'>('list');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const events = [
    {
      id: 1,
      title: 'TechCrunch Disrupt',
      date: 'March 15, 2024',
      duration: '3h 24m',
      location: 'San Francisco',
      people: 6,
      conversations: 12,
      followups: 5,
      summary: 'Productive networking event focused on AI safety and Series A funding',
      completed: true,
    },
    {
      id: 2,
      title: 'YC Demo Day',
      date: 'March 10, 2024',
      duration: '5h 12m',
      location: 'Mountain View',
      people: 8,
      conversations: 15,
      followups: 3,
      summary: 'Met with potential investors and founder community',
      completed: true,
    },
    {
      id: 3,
      title: 'Stanford AI Conference',
      date: 'February 28, 2024',
      duration: '2h 45m',
      location: 'Palo Alto',
      people: 4,
      conversations: 7,
      followups: 2,
      summary: 'Discussed latest developments in AI safety',
      completed: true,
    },
  ];

  return (
    <div className="min-h-screen bg-[#F5F7FA]">
      <Navigation isAuthenticated={true} />

      <div className="flex">
        <Sidebar isOpen={sidebarOpen} />

        <main className="flex-1 p-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="font-display text-3xl font-bold text-[#121417] mb-2">Events</h1>
              <p className="text-[#6B7280]">Manage your networking events</p>
            </div>
            <Button>+ Create New Event</Button>
          </div>

          {/* Controls */}
          <div className="flex items-center gap-4 mb-8">
            <input
              type="text"
              placeholder="Search events..."
              className="flex-1 px-4 py-2 rounded-lg border border-[#E5E7EB] focus:outline-none focus:ring-2 focus:ring-[#00C2FF]"
            />
            <div className="flex gap-2 border border-[#E5E7EB] rounded-lg p-1">
              {['list', 'grid', 'timeline'].map((mode) => (
                <button
                  key={mode}
                  onClick={() => setViewMode(mode as any)}
                  className={`
                    px-3 py-2 rounded text-sm font-medium transition-colors
                    ${viewMode === mode ? 'bg-[#1F3C88] text-white' : 'text-[#6B7280]'}
                  `}
                >
                  {mode === 'list' && '☰'}
                  {mode === 'grid' && '⊞'}
                  {mode === 'timeline' && '⊥'}
                </button>
              ))}
            </div>
            <select className="px-4 py-2 border border-[#E5E7EB] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#00C2FF]">
              <option>All Events</option>
              <option>Upcoming</option>
              <option>Past</option>
            </select>
          </div>

          {/* Events List/Grid */}
          {viewMode === 'list' && (
            <div className="space-y-4">
              {events.map((event) => (
                <Card key={event.id} hoverable className="cursor-pointer">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="font-bold text-lg text-[#121417]">{event.title}</h3>
                      <p className="text-sm text-[#6B7280] mt-1">
                        {event.date} • {event.duration} • {event.location}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <span className="px-3 py-1 rounded-full bg-[#10B981]/10 text-[#10B981] text-xs font-medium">
                        ✓ Completed
                      </span>
                    </div>
                  </div>

                  <p className="text-sm text-[#6B7280] mb-4">{event.summary}</p>

                  <div className="flex gap-8 py-4 border-t border-b border-[#E5E7EB] my-4">
                    <div>
                      <p className="text-xs text-[#6B7280] uppercase mb-1">People</p>
                      <p className="text-lg font-bold text-[#121417]">{event.people}</p>
                    </div>
                    <div>
                      <p className="text-xs text-[#6B7280] uppercase mb-1">Conversations</p>
                      <p className="text-lg font-bold text-[#121417]">{event.conversations}</p>
                    </div>
                    <div>
                      <p className="text-xs text-[#6B7280] uppercase mb-1">Follow-ups</p>
                      <p className="text-lg font-bold text-[#121417]">{event.followups}</p>
                    </div>
                    <div className="ml-auto">
                      <Button variant="secondary" size="sm">
                        View Details →
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}

          {viewMode === 'grid' && (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {events.map((event) => (
                <Card key={event.id} hoverable className="flex flex-col">
                  <div className="flex-1">
                    <h3 className="font-bold text-lg text-[#121417] mb-2">{event.title}</h3>
                    <p className="text-xs text-[#6B7280] mb-4">{event.date}</p>

                    <div className="space-y-2 mb-4">
                      <p className="text-sm text-[#6B7280]">📍 {event.location}</p>
                      <p className="text-sm text-[#6B7280]">⏱ {event.duration}</p>
                    </div>

                    <div className="grid grid-cols-3 gap-4 py-4 border-t border-[#E5E7EB]">
                      <div>
                        <p className="text-xs text-[#6B7280]">People</p>
                        <p className="font-bold text-[#121417]">{event.people}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#6B7280]">Chats</p>
                        <p className="font-bold text-[#121417]">{event.conversations}</p>
                      </div>
                      <div>
                        <p className="text-xs text-[#6B7280]">Follow-ups</p>
                        <p className="font-bold text-[#121417]">{event.followups}</p>
                      </div>
                    </div>
                  </div>

                  <Button variant="secondary" size="sm" className="w-full mt-4">
                    View Event
                  </Button>
                </Card>
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
