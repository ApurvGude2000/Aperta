import React, { useState, useEffect, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { Navigation } from '../components/design-system/Navigation';
import { Card } from '../components/design-system/Card';
import { Button } from '../components/design-system/Button';

interface GraphNode {
  id: string;
  name: string;
  company?: string;
  title?: string;
  email?: string;
  linkedin_url?: string;
  event_count: number;
  connection_count: number;
  topics: string[];
}

interface GraphEdge {
  source: string;
  target: string;
  weight: number;
  connection_type: string;
  context?: string;
  events: string[];
}

interface KnowledgeGraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  stats: {
    total_people: number;
    total_connections: number;
    total_events: number;
    total_companies: number;
  };
}

export function KnowledgeGraph() {
  const [graphData, setGraphData] = useState<{ nodes: GraphNode[]; links: GraphEdge[] } | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const fgRef = useRef<any>();

  useEffect(() => {
    fetchGraphData();
  }, []);

  const fetchGraphData = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/knowledge-graph/');
      if (!response.ok) {
        throw new Error(`Failed to fetch graph data: ${response.statusText}`);
      }
      const data: KnowledgeGraphData = await response.json();

      // Transform edges to links for ForceGraph2D
      setGraphData({
        nodes: data.nodes,
        links: data.edges
      });
      setError(null);
    } catch (err) {
      console.error('Error fetching knowledge graph:', err);
      setError(err instanceof Error ? err.message : 'Failed to load knowledge graph');
    } finally {
      setLoading(false);
    }
  };

  const filterOptions = {
    nodes: ['People', 'Companies', 'Topics', 'Events'],
    edges: ['Direct conversation', 'Shared topics', 'Same company', 'Same event'],
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
              <Card className="flex-1 bg-[#121417] text-white relative overflow-hidden p-0">
                {loading && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                      <p className="text-6xl mb-4">🕸️</p>
                      <p className="text-xl font-bold mb-2">Loading Knowledge Graph...</p>
                    </div>
                  </div>
                )}
                {error && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                      <p className="text-6xl mb-4">⚠️</p>
                      <p className="text-xl font-bold mb-2 text-red-400">Error Loading Graph</p>
                      <p className="text-sm text-[#9CA3AF] mb-4">{error}</p>
                      <Button onClick={fetchGraphData}>Retry</Button>
                    </div>
                  </div>
                )}
                {!loading && !error && graphData && graphData.nodes.length === 0 && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                      <p className="text-6xl mb-4">📊</p>
                      <p className="text-xl font-bold mb-2">No Data Yet</p>
                      <p className="text-sm text-[#9CA3AF] mb-4">
                        Start by adding conversations and participants to see your network graph.
                      </p>
                    </div>
                  </div>
                )}
                {!loading && !error && graphData && graphData.nodes.length > 0 && (
                  <ForceGraph2D
                    ref={fgRef}
                    graphData={graphData}
                    nodeLabel={(node: any) => `${node.name}${node.company ? ` (${node.company})` : ''}`}
                    nodeAutoColorBy="company"
                    nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
                      const label = node.name;
                      const fontSize = 12 / globalScale;
                      ctx.font = `${fontSize}px Sans-Serif`;
                      const textWidth = ctx.measureText(label).width;
                      const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.4);

                      // Draw circle
                      ctx.beginPath();
                      ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI, false);
                      ctx.fillStyle = node.company ? '#00C2FF' : '#6B7280';
                      ctx.fill();

                      // Draw label
                      ctx.textAlign = 'center';
                      ctx.textBaseline = 'middle';
                      ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
                      ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - 10 - bckgDimensions[1] / 2, bckgDimensions[0], bckgDimensions[1]);
                      ctx.fillStyle = '#121417';
                      ctx.fillText(label, node.x, node.y - 10);
                    }}
                    linkLabel={(link: any) => link.context || ''}
                    linkColor={(link: any) => {
                      switch (link.connection_type) {
                        case 'same_event': return '#00C2FF';
                        case 'same_company': return '#10B981';
                        case 'common_topics': return '#F59E0B';
                        default: return '#6B7280';
                      }
                    }}
                    linkWidth={(link: any) => Math.sqrt(link.weight) * 2}
                    linkDirectionalParticles={2}
                    linkDirectionalParticleWidth={(link: any) => link.weight * 2}
                    onNodeClick={(node: any) => setSelectedNode(node as GraphNode)}
                    backgroundColor="#121417"
                    width={800}
                    height={600}
                  />
                )}
              </Card>
            </div>

            {/* Right Sidebar: Node Details */}
            {selectedNode && (
              <div className="w-80 flex-shrink-0">
                <Card className="sticky top-24">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="text-4xl">👤</div>
                    <div className="flex-1">
                      <h3 className="font-bold text-[#121417]">{selectedNode.name}</h3>
                      {selectedNode.company && (
                        <p className="text-sm text-[#6B7280]">{selectedNode.company}</p>
                      )}
                      {selectedNode.title && (
                        <p className="text-xs text-[#9CA3AF]">{selectedNode.title}</p>
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3 mb-6 pb-6 border-b border-[#E5E7EB]">
                    <div className="text-center">
                      <p className="text-xs text-[#6B7280] uppercase mb-1">Connections</p>
                      <p className="font-bold text-[#121417]">{selectedNode.connection_count}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-[#6B7280] uppercase mb-1">Events</p>
                      <p className="font-bold text-[#121417]">{selectedNode.event_count}</p>
                    </div>
                  </div>

                  {selectedNode.email && (
                    <div className="mb-6 pb-6 border-b border-[#E5E7EB]">
                      <p className="text-xs font-medium text-[#6B7280] uppercase mb-2">Contact</p>
                      <p className="text-sm text-[#121417] break-all">{selectedNode.email}</p>
                    </div>
                  )}

                  {selectedNode.topics && selectedNode.topics.length > 0 && (
                    <div className="mb-6 pb-6 border-b border-[#E5E7EB]">
                      <p className="text-xs font-medium text-[#6B7280] uppercase mb-3">Topics Discussed</p>
                      <div className="flex flex-wrap gap-2">
                        {selectedNode.topics.map((topic, idx) => (
                          <span key={idx} className="px-2 py-1 bg-[#F5F7FA] rounded text-xs text-[#121417]">
                            {topic}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="space-y-2">
                    {selectedNode.linkedin_url && (
                      <Button
                        size="sm"
                        className="w-full"
                        onClick={() => window.open(selectedNode.linkedin_url, '_blank')}
                      >
                        View LinkedIn Profile
                      </Button>
                    )}
                    <Button
                      variant="secondary"
                      size="sm"
                      className="w-full"
                      onClick={() => setSelectedNode(null)}
                    >
                      Close
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
