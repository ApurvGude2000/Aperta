import React, { useState } from 'react';
import { Navigation } from '../components/design-system/Navigation';
import { Sidebar } from '../components/design-system/Sidebar';
import { Button } from '../components/design-system/Button';

export function KnowledgeGraph() {
  const [selectedNode, setSelectedNode] = useState<any>(null);

  const filterOptions = {
    nodes: ['People', 'Companies', 'Topics', 'Events'],
    edges: ['Direct conversation', 'Shared topics', 'Same company', 'Same event'],
  };

  const sampleNode = {
    name: 'Alice Chen',
    company: 'Acme Ventures',
    connections: 12,
    sharedTopics: 5,
    eventsMet: 2,
    recentConversations: [
      { title: 'TechCrunch Disrupt', date: 'Mar 15' },
      { title: 'Stanford AI Conf', date: 'Feb 20' },
    ],
    commonTopics: ['AI Safety', 'Venture Capital', 'Healthcare AI'],
  };

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
            <h1 className="font-display text-5xl font-bold text-white mb-2">Knowledge Graph</h1>
            <p className="text-black text-lg">Explore your networking connections and relationships</p>
          </div>

          {/* Layout: Sidebar + Graph Canvas */}
          <div className="flex gap-8">
            {/* Left Sidebar: Filters */}
            <div className="w-80 flex-shrink-0">
              <div className="premium-card rounded-2xl p-8 border-2 border-cyan-500/20 sticky top-24">
                <h3 className="font-display text-xl font-bold text-white mb-6">Filters</h3>

                <div className="space-y-6">
                  {/* Filter Nodes */}
                  <div>
                    <p className="text-sm font-semibold text-black uppercase mb-3">Node Types</p>
                    <div className="space-y-2">
                      {filterOptions.nodes.map((node) => (
                        <label key={node} className="flex items-center gap-2 cursor-pointer hover:opacity-80 transition-opacity">
                          <input type="checkbox" defaultChecked className="w-4 h-4 rounded border-cyan-500 bg-slate-800" />
                          <span className="text-sm text-black">{node}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Filter Edges */}
                  <div className="pt-4 border-t border-cyan-500/20">
                    <p className="text-sm font-semibold text-black uppercase mb-3">Connections</p>
                    <div className="space-y-2">
                      {filterOptions.edges.slice(0, 2).map((edge) => (
                        <label key={edge} className="flex items-center gap-2 cursor-pointer hover:opacity-80 transition-opacity">
                          <input type="checkbox" defaultChecked className="w-4 h-4 rounded border-cyan-500 bg-slate-800" />
                          <span className="text-sm text-black">{edge}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Time Range */}
                  <div className="pt-4 border-t border-cyan-500/20">
                    <p className="text-sm font-semibold text-black uppercase mb-3">Time Range</p>
                    <select className="w-full px-4 py-2 bg-slate-800/50 border border-cyan-500/30 text-white rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500">
                      <option>Last 30 days</option>
                      <option>Last 60 days</option>
                      <option>Last 90 days</option>
                      <option>All time</option>
                    </select>
                  </div>

                  {/* Search */}
                  <div className="pt-4 border-t border-cyan-500/20">
                    <input
                      type="text"
                      placeholder="Search nodes..."
                      className="w-full px-4 py-2 bg-slate-800/50 border border-cyan-500/30 text-white placeholder-slate-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 backdrop-blur-lg"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Center: Graph Canvas */}
            <div className="flex-1 flex">
              <div className="premium-card rounded-2xl w-full border-2 border-cyan-500/20 bg-gradient-to-br from-slate-800/50 to-slate-900 text-white flex items-center justify-center overflow-hidden">
                <div className="text-center pointer-events-none">
                  <p className="text-8xl mb-4 float-animate">🕸️</p>
                  <p className="text-3xl font-display font-bold mb-2 text-white">Interactive Knowledge Graph</p>
                  <p className="text-lg text-slate-800 mb-6">Zoom • Pan • Click nodes to explore</p>
                  <p className="text-sm text-slate-800">Node interactions will be rendered here</p>
                </div>
              </div>
            </div>

            {/* Right Sidebar: Node Details */}
            {selectedNode && (
              <div className="w-80 flex-shrink-0">
                <div className="premium-card rounded-2xl p-8 border-2 border-cyan-500/20 sticky top-24">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="text-5xl">👩‍💼</div>
                    <div className="flex-1">
                      <h3 className="font-bold text-white text-lg">{sampleNode.name}</h3>
                      <p className="text-sm text-slate-800">{sampleNode.company}</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-3 mb-6 pb-6 border-b border-cyan-500/10">
                    <div className="text-center">
                      <p className="text-xs text-slate-800 uppercase font-semibold mb-1">Connections</p>
                      <p className="font-bold text-cyan-400">{sampleNode.connections}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-slate-800 uppercase font-semibold mb-1">Topics</p>
                      <p className="font-bold text-cyan-400">{sampleNode.sharedTopics}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-slate-800 uppercase font-semibold mb-1">Events</p>
                      <p className="font-bold text-cyan-400">{sampleNode.eventsMet}</p>
                    </div>
                  </div>

                  <div className="mb-6">
                    <p className="text-xs font-semibold text-slate-800 uppercase mb-3">Recent Conversations</p>
                    <div className="space-y-2">
                      {sampleNode.recentConversations.map((conv, idx) => (
                        <div key={idx} className="p-3 bg-slate-800/30 rounded border border-cyan-500/10 hover:border-cyan-500/30 transition-all">
                          <p className="text-sm font-medium text-white">{conv.title}</p>
                          <p className="text-xs text-slate-800">{conv.date}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="mb-6 pb-6 border-b border-cyan-500/10">
                    <p className="text-xs font-semibold text-slate-800 uppercase mb-3">Common Topics</p>
                    <div className="flex flex-wrap gap-2">
                      {sampleNode.commonTopics.map((topic, idx) => (
                        <span key={idx} className="px-3 py-1 bg-cyan-500/10 rounded-full text-xs text-cyan-300 border border-cyan-500/20">
                          {topic}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-3">
                    <Button className="w-full bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 text-white font-bold">
                      View Profile
                    </Button>
                    <Button variant="secondary" className="w-full border-2 border-purple-400 text-purple-300 hover:bg-purple-500/10 font-bold">
                      Generate Follow-up
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
