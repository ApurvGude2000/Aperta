import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Navigation } from '../components/design-system/Navigation';
import { Sidebar } from '../components/design-system/Sidebar';
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
      completed: true,
      color: 'from-cyan-500 to-blue-500',
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
      completed: true,
      color: 'from-purple-500 to-pink-500',
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
      completed: true,
      color: 'from-orange-400 to-pink-500',
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
        <Sidebar isOpen={sidebarOpen} />

        <main className="flex-1 p-8">
          {/* Header with sticky animation */}
          <div className="mb-8 sticky-section">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="font-display text-5xl font-bold text-white mb-2">Events</h1>
                <p className="text-gray-200 text-lg">Manage your networking events</p>
              </div>
              <Button className="bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 text-white font-bold shadow-lg shadow-cyan-500/50 transform hover:scale-110">
                + Create New Event
              </Button>
            </div>
          </div>

          {/* Controls */}
          <div className="flex flex-col md:flex-row items-center gap-4 mb-8">
            <input
              type="text"
              placeholder="Search events..."
              className="flex-1 px-4 py-3 rounded-lg bg-slate-800/50 border border-cyan-500/30 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 backdrop-blur-lg transition-all"
            />
            <div className="flex gap-2 border border-cyan-500/30 rounded-lg p-1 bg-slate-800/50 backdrop-blur-lg">
              {['list', 'grid', 'timeline'].map((mode) => (
                <button
                  key={mode}
                  onClick={() => setViewMode(mode as any)}
                  className={`
                    px-3 py-2 rounded text-sm font-medium transition-all transform
                    ${viewMode === mode
                      ? 'bg-gradient-to-r from-cyan-500 to-purple-600 text-white shadow-lg shadow-cyan-500/50 scale-105'
                      : 'text-gray-200 hover:text-cyan-400'}
                  `}
                >
                  {mode === 'list' && '☰'}
                  {mode === 'grid' && '⊞'}
                  {mode === 'timeline' && '⊥'}
                </button>
              ))}
            </div>
            <select className="px-4 py-3 bg-slate-800/50 border border-cyan-500/30 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 backdrop-blur-lg">
              <option className="bg-slate-800">All Events</option>
              <option className="bg-slate-800">Upcoming</option>
              <option className="bg-slate-800">Past</option>
            </select>
          </div>

          {/* Events List View */}
          {viewMode === 'list' && (
            <div className="space-y-4">
              {events.map((event, idx) => (
                <Link to={`/events/${event.id}`} key={event.id}>
                  <div
                    className="group relative premium-card rounded-2xl p-8 border-2 border-cyan-500/10 h-full hover:border-cyan-500/30 hover:shadow-2xl hover:shadow-cyan-500/20 cursor-pointer"
                    style={{animation: `slide-in-left 0.8s ease-out ${idx * 0.1}s both`}}
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/5 to-purple-500/5 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>

                    <div className="relative">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h3 className="font-display text-2xl font-bold text-white group-hover:text-transparent group-hover:bg-gradient-to-r group-hover:from-cyan-400 group-hover:to-purple-400 group-hover:bg-clip-text transition-all">
                            {event.title}
                          </h3>
                          <p className="text-sm text-gray-400 mt-1">
                            {event.date} • {event.duration} • {event.location}
                          </p>
                        </div>
                        <div className="flex gap-2">
                          <span className="px-4 py-2 rounded-full bg-green-500/20 text-green-300 text-xs font-bold border border-green-500/30">
                            ✓ Completed
                          </span>
                        </div>
                      </div>

                      <div className="flex gap-8 py-4 border-t border-cyan-500/10 my-4">
                        <div>
                          <p className="text-xs text-gray-400 uppercase font-semibold mb-1">People</p>
                          <p className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                            {event.people}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-400 uppercase font-semibold mb-1">Conversations</p>
                          <p className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                            {event.conversations}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-400 uppercase font-semibold mb-1">Follow-ups</p>
                          <p className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                            {event.followups}
                          </p>
                        </div>
                        <div className="ml-auto">
                          <Button variant="secondary" className="border-2 border-purple-400 text-purple-300 hover:bg-purple-500/10 font-bold">
                            View Details →
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}

          {/* Events Grid View */}
          {viewMode === 'grid' && (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              {events.map((event, idx) => (
                <Link to={`/events/${event.id}`} key={event.id}>
                  <div
                    className="group relative premium-card rounded-2xl p-8 border-2 border-cyan-500/10 h-full flex flex-col hover:border-cyan-500/30 hover:shadow-2xl hover:shadow-cyan-500/20 cursor-pointer"
                    style={{animation: `slide-in-left 0.8s ease-out ${idx * 0.1}s both`}}
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/5 to-purple-500/5 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>

                    <div className="relative flex-1">
                      <div className={`w-16 h-16 rounded-full bg-gradient-to-br ${event.color} flex items-center justify-center text-2xl mb-4 shadow-lg transform group-hover:scale-125 transition-transform`}>
                        📅
                      </div>
                      <h3 className="font-display text-xl font-bold text-white mb-2 group-hover:text-transparent group-hover:bg-gradient-to-r group-hover:from-cyan-400 group-hover:to-purple-400 group-hover:bg-clip-text transition-all">
                        {event.title}
                      </h3>
                      <p className="text-xs text-gray-400 mb-4">{event.date}</p>

                      <div className="space-y-2 mb-4 text-sm text-gray-200">
                        <p>📍 {event.location}</p>
                        <p>⏱ {event.duration}</p>
                      </div>

                      <div className="grid grid-cols-3 gap-4 py-4 border-t border-cyan-500/10">
                        <div>
                          <p className="text-xs text-gray-400 font-semibold">People</p>
                          <p className="font-bold text-cyan-400">{event.people}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-400 font-semibold">Chats</p>
                          <p className="font-bold text-cyan-400">{event.conversations}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-400 font-semibold">Follow-ups</p>
                          <p className="font-bold text-cyan-400">{event.followups}</p>
                        </div>
                      </div>
                    </div>

                    <Button variant="secondary" className="w-full mt-4 border-2 border-purple-400 text-purple-300 hover:bg-purple-500/10 font-bold">
                      View Event →
                    </Button>
                  </div>
                </Link>
              ))}
            </div>
          )}

          {/* Timeline View */}
          {viewMode === 'timeline' && (
            <div className="relative">
              {/* Timeline line */}
              <div className="hidden md:block absolute left-1/2 top-0 bottom-0 w-1 bg-gradient-to-b from-cyan-500 via-purple-500 to-pink-500 opacity-30 transform -translate-x-1/2"></div>

              <div className="space-y-12">
                {events.map((event, idx) => (
                  <Link to={`/events/${event.id}`} key={event.id}>
                    <div
                      className={`relative md:flex ${idx % 2 === 0 ? 'md:flex-row' : 'md:flex-row-reverse'}`}
                      style={{animation: `bounce-in 0.8s ease-out ${idx * 0.15}s both`}}
                    >
                      {/* Timeline dot */}
                      <div className="hidden md:flex absolute left-1/2 top-8 w-6 h-6 bg-gradient-to-br from-cyan-500 to-purple-600 rounded-full transform -translate-x-1/2 shadow-lg shadow-cyan-500/50 border-4 border-slate-900 z-10"></div>

                      {/* Event card */}
                      <div className={`md:w-1/2 ${idx % 2 === 0 ? 'md:pr-8' : 'md:pl-8'}`}>
                        <div className="group premium-card rounded-2xl p-8 border-2 border-cyan-500/10 h-full hover:border-cyan-500/30 hover:shadow-2xl hover:shadow-cyan-500/20 cursor-pointer">
                          <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/5 to-purple-500/5 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>

                          <div className="relative">
                            <h3 className="font-display text-xl font-bold text-white group-hover:text-transparent group-hover:bg-gradient-to-r group-hover:from-cyan-400 group-hover:to-purple-400 group-hover:bg-clip-text transition-all mb-2">
                              {event.title}
                            </h3>
                            <p className="text-sm text-gray-400 mb-3">{event.date} • {event.duration}</p>
                            <p className="text-sm text-gray-200 mb-4">📍 {event.location}</p>

                            <div className="flex gap-6 py-3 border-t border-cyan-500/10">
                              <div>
                                <p className="text-xs text-gray-400 font-semibold">People</p>
                                <p className="font-bold text-cyan-400">{event.people}</p>
                              </div>
                              <div>
                                <p className="text-xs text-gray-400 font-semibold">Conversations</p>
                                <p className="font-bold text-cyan-400">{event.conversations}</p>
                              </div>
                              <div>
                                <p className="text-xs text-gray-400 font-semibold">Follow-ups</p>
                                <p className="font-bold text-cyan-400">{event.followups}</p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
