import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Navigation } from '../components/design-system/Navigation';
import { Card } from '../components/design-system/Card';
import { Button } from '../components/design-system/Button';
import { api } from '../api/client';

export function Events() {
  const [viewMode, setViewMode] = useState<'list' | 'grid' | 'timeline'>('list');
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      const conversations = await api.getConversations();

      // Transform conversations to event format
      const transformedEvents = conversations.map((conv: any) => ({
        id: conv.id,
        title: conv.title?.replace('.txt', '').replace(/_/g, ' ') || 'Untitled Event',
        date: new Date(conv.started_at).toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        }),
        location: conv.location || 'Unknown',
        people: conv.participant_count || 0,
        completed: conv.status === 'completed',
        event_name: conv.event_name,
      }));

      setEvents(transformedEvents);
    } catch (error) {
      console.error('Error fetching events:', error);
      setEvents([]);
    } finally {
      setLoading(false);
    }
  };

  const filteredEvents = events.filter(event =>
    event.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    event.location?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-[#F5F7FA]">
      <Navigation isAuthenticated={true} />

      <main className="max-w-7xl mx-auto p-8">
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
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
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
          {loading ? (
            <div className="text-center py-12">
              <p className="text-[#6B7280]">Loading events...</p>
            </div>
          ) : filteredEvents.length === 0 ? (
            <Card className="text-center py-12">
              <p className="text-[#6B7280] mb-2">No events found</p>
              <p className="text-sm text-[#9CA3AF]">
                {searchQuery ? 'Try a different search term' : 'Upload a transcript to create your first event'}
              </p>
            </Card>
          ) : viewMode === 'list' && (
            <div className="space-y-4">
              {filteredEvents.map((event) => (
                <Link key={event.id} to={`/events/${event.id}`}>
                  <Card hoverable className="cursor-pointer">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h3 className="font-bold text-lg text-[#121417]">{event.title}</h3>
                        <p className="text-sm text-[#6B7280] mt-1">
                          {event.date}{event.location && event.location !== 'Unknown' ? ` • ${event.location}` : ''}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        {event.completed && (
                          <span className="px-3 py-1 rounded-full bg-[#10B981]/10 text-[#10B981] text-xs font-medium">
                            ✓ Completed
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="flex gap-8 py-4 border-t border-[#E5E7EB] mt-4">
                      <div>
                        <p className="text-xs text-[#6B7280] uppercase mb-1">People</p>
                        <p className="text-lg font-bold text-[#121417]">{event.people}</p>
                      </div>
                      <div className="ml-auto">
                        <Button variant="secondary" size="sm">
                          View Transcript →
                        </Button>
                      </div>
                    </div>
                  </Card>
                </Link>
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
  );
}
