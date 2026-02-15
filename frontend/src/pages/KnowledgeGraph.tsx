import React, { useState } from 'react';
import { Navigation } from '../components/design-system/Navigation';
import { Card } from '../components/design-system/Card';
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
    <div className="min-h-screen bg-[#F5F7FA]">
      <Navigation isAuthenticated={true} />

      <main className="max-w-7xl mx-auto p-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="font-display text-3xl font-bold text-[#121417] mb-2">Knowledge Graph</h1>
            <p className="text-[#6B7280]">Explore your networking connections and relationships</p>
          </div>

          {/* Layout: Sidebar + Graph Canvas */}
          <div className="flex gap-8">
            {/* Left Sidebar: Filters */}
            <div className="w-64 flex-shrink-0">
              <Card className="sticky top-24">
                <h3 className="font-bold text-[#121417] mb-4">Filters</h3>

                <div className="space-y-6">
                  {/* Filter Nodes */}
                  <div>
                    <p className="text-sm font-medium text-[#121417] mb-3">Node Types</p>
                    <div className="space-y-2">
                      {filterOptions.nodes.map((node) => (
                        <label key={node} className="flex items-center gap-2 cursor-pointer">
                          <input type="checkbox" defaultChecked className="w-4 h-4" />
                          <span className="text-sm text-[#6B7280]">{node}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Filter Edges */}
                  <div className="pt-4 border-t border-[#E5E7EB]">
                    <p className="text-sm font-medium text-[#121417] mb-3">Connections</p>
                    <div className="space-y-2">
                      {filterOptions.edges.slice(0, 2).map((edge) => (
                        <label key={edge} className="flex items-center gap-2 cursor-pointer">
                          <input type="checkbox" defaultChecked className="w-4 h-4" />
                          <span className="text-sm text-[#6B7280]">{edge}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Time Range */}
                  <div className="pt-4 border-t border-[#E5E7EB]">
                    <p className="text-sm font-medium text-[#121417] mb-3">Time Range</p>
                    <select className="w-full px-3 py-2 border border-[#E5E7EB] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#00C2FF]">
                      <option>Last 30 days</option>
                      <option>Last 60 days</option>
                      <option>Last 90 days</option>
                      <option>All time</option>
                    </select>
                  </div>

                  {/* Search */}
                  <div className="pt-4 border-t border-[#E5E7EB]">
                    <input
                      type="text"
                      placeholder="Search nodes..."
                      className="w-full px-3 py-2 border border-[#E5E7EB] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#00C2FF]"
                    />
                  </div>
                </div>
              </Card>
            </div>

            {/* Center: Graph Canvas */}
            <div className="flex-1 flex">
              <Card className="flex-1 bg-[#121417] text-white flex items-center justify-center">
                <div className="text-center">
                  <p className="text-6xl mb-4">🕸️</p>
                  <p className="text-xl font-bold mb-2">Interactive Knowledge Graph</p>
                  <p className="text-[#9CA3AF] mb-6">Zoom • Pan • Click nodes to explore</p>
                  <p className="text-sm text-[#6B7280]">Node interactions will be rendered here</p>
                </div>
              </Card>
            </div>

            {/* Right Sidebar: Node Details */}
            {selectedNode && (
              <div className="w-80 flex-shrink-0">
                <Card className="sticky top-24">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="text-4xl">👩‍💼</div>
                    <div className="flex-1">
                      <h3 className="font-bold text-[#121417]">{sampleNode.name}</h3>
                      <p className="text-sm text-[#6B7280]">{sampleNode.company}</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-3 mb-6 pb-6 border-b border-[#E5E7EB]">
                    <div className="text-center">
                      <p className="text-xs text-[#6B7280] uppercase mb-1">Connections</p>
                      <p className="font-bold text-[#121417]">{sampleNode.connections}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-[#6B7280] uppercase mb-1">Topics</p>
                      <p className="font-bold text-[#121417]">{sampleNode.sharedTopics}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-[#6B7280] uppercase mb-1">Events</p>
                      <p className="font-bold text-[#121417]">{sampleNode.eventsMet}</p>
                    </div>
                  </div>

                  <div className="mb-6">
                    <p className="text-xs font-medium text-[#6B7280] uppercase mb-3">Recent Conversations</p>
                    <div className="space-y-2">
                      {sampleNode.recentConversations.map((conv, idx) => (
                        <div key={idx} className="p-2 bg-[#F5F7FA] rounded">
                          <p className="text-sm font-medium text-[#121417]">{conv.title}</p>
                          <p className="text-xs text-[#6B7280]">{conv.date}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="mb-6 pb-6 border-b border-[#E5E7EB]">
                    <p className="text-xs font-medium text-[#6B7280] uppercase mb-3">Common Topics</p>
                    <div className="flex flex-wrap gap-2">
                      {sampleNode.commonTopics.map((topic, idx) => (
                        <span key={idx} className="px-2 py-1 bg-[#F5F7FA] rounded text-xs text-[#121417]">
                          {topic}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Button size="sm" className="w-full">
                      View Profile
                    </Button>
                    <Button variant="secondary" size="sm" className="w-full">
                      Generate Follow-up
                    </Button>
                  </div>
                </Card>
              </div>
            )}
          </div>
      </main>
    </div>
  );
}
