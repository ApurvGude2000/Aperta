import React, { useState, useEffect, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { Navigation } from '../components/design-system/Navigation';
import { Card } from '../components/design-system/Card';
import { Button } from '../components/design-system/Button';
import { api } from '../api/client';

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
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const [selectedEvent, setSelectedEvent] = useState<string>('all');
  const [events, setEvents] = useState<any[]>([]);
  const [graphType, setGraphType] = useState<'events' | 'slack'>('events');
  const fgRef = useRef<any>();
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Get container dimensions for ForceGraph size
    const updateDimensions = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        setDimensions({ width: rect.width, height: rect.height });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  useEffect(() => {
    // Fetch events on mount
    fetchEvents();
  }, []);

  useEffect(() => {
    // Fetch data when component mounts, event changes, or graph type changes
    fetchGraphData();
  }, [selectedEvent, graphType]);

  const fetchEvents = async () => {
    try {
      const conversations = await api.getConversations();
      setEvents(conversations || []);
    } catch (error) {
      console.error('Error fetching events:', error);
      setEvents([]);
    }
  };

  const fetchGraphData = async () => {
    try {
      setLoading(true);

      // Determine which endpoint to call based on graph type
      const endpoint = graphType === 'slack'
        ? 'http://localhost:8000/knowledge-graph/slack-members'
        : 'http://localhost:8000/knowledge-graph/';

      const response = await fetch(endpoint);
      if (!response.ok) {
        throw new Error(`Failed to fetch graph data: ${response.statusText}`);
      }
      const data: KnowledgeGraphData = await response.json();

      // Position nodes based on graph type
      const nodes = data.nodes.map((node, i) => {
        const angle = (i / data.nodes.length) * 2 * Math.PI;

        if (graphType === 'slack') {
          // Random scatter for Slack graph with wide spacing
          const baseRadius = 800; // Increased from 500
          const randomAngle = angle + (Math.random() - 0.5) * 1.5;
          const randomRadius = baseRadius * (0.5 + Math.random() * 1.0); // 50%-150% spread
          const x = Math.cos(randomAngle) * randomRadius;
          const y = Math.sin(randomAngle) * randomRadius;

          // Fix positions to prevent force simulation movement
          return { ...node, x, y, fx: x, fy: y };
        } else {
          // Fixed circle for Events graph
          const radius = 700;
          const x = Math.cos(angle) * radius;
          const y = Math.sin(angle) * radius;

          return { ...node, x, y, fx: x, fy: y };
        }
      });

      // Filter edges based on graph type
      let strongLinks = data.edges;

      if (graphType === 'events') {
        // Events graph: filter to top 40% strongest
        const allWeights = data.edges.map((e: GraphEdge) => e.weight);
        if (allWeights.length > 0) {
          const maxWeight = Math.max(...allWeights);
          const minWeight = Math.min(...allWeights);
          const threshold = minWeight + (maxWeight - minWeight) * 0.6;
          strongLinks = data.edges.filter((edge: GraphEdge) => edge.weight >= threshold);
        }
      }
      // Slack graph: show all edges (already filtered by backend)

      setGraphData({
        nodes: nodes,
        links: strongLinks
      });
      setError(null);

      // Auto-fit to show all nodes after graph loads
      setTimeout(() => {
        if (fgRef.current) {
          fgRef.current.zoomToFit(400, 100);
        }
      }, 1000);
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

            {/* Graph Type Selector */}
            <div className="mt-6 flex items-center gap-6">
              {/* Graph Type Toggle */}
              <div className="flex items-center gap-3">
                <label className="text-sm font-medium text-[#121417]">Graph Type:</label>
                <div className="flex bg-gray-100 rounded-lg p-1">
                  <button
                    onClick={() => setGraphType('events')}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                      graphType === 'events'
                        ? 'bg-white text-[#1F3C88] shadow-sm'
                        : 'text-[#6B7280] hover:text-[#121417]'
                    }`}
                  >
                    Events
                  </button>
                  <button
                    onClick={() => setGraphType('slack')}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                      graphType === 'slack'
                        ? 'bg-white text-[#1F3C88] shadow-sm'
                        : 'text-[#6B7280] hover:text-[#121417]'
                    }`}
                  >
                    Slack Members
                  </button>
                </div>
              </div>

              {/* Event Selector (only show for Events graph) */}
              {graphType === 'events' && (
                <div className="flex items-center gap-3">
                  <label className="text-sm font-medium text-[#121417]">Event:</label>
                  <select
                    value={selectedEvent}
                    onChange={(e) => setSelectedEvent(e.target.value)}
                    className="px-4 py-2 border border-[#E5E7EB] rounded-lg text-sm font-medium focus:outline-none focus:ring-2 focus:ring-[#00C2FF] bg-white"
                  >
                    <option value="all">All Events</option>
                    {events.map((event) => (
                      <option key={event.id} value={event.id}>
                        {event.title?.replace('.txt', '').replace(/_/g, ' ') || 'Untitled Event'}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <span className="text-sm text-[#9CA3AF]">
                Showing {graphData?.nodes?.length || 0} nodes, {graphData?.edges?.length || 0} connections
              </span>
            </div>
          </div>

          {/* Layout: Graph Canvas (full width, no sidebar for now) */}
          <div className="flex gap-8">
            {/* Left Sidebar: Filters - HIDDEN FOR NOW */}
            <div className="w-64 flex-shrink-0" style={{ display: 'none' }}>
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

            {/* Center: Graph Canvas - FULL WIDTH */}
            <div ref={containerRef} className="flex-1 flex" style={{ minHeight: 'calc(100vh - 250px)', width: '100%' }}>
              <Card className="flex-1 bg-gradient-to-br from-gray-50 to-gray-100 relative overflow-hidden p-0 border border-gray-200">
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
                {!loading && !error && graphData && graphData.nodes.length > 0 && (() => {
                  // Find the node with the most conversations (that's "You")
                  const maxEvents = Math.max(...graphData.nodes.map((n: any) => n.event_count));
                  const youNodeId = graphData.nodes.find((n: any) => n.event_count === maxEvents)?.id;

                  return (
                  <ForceGraph2D
                    ref={fgRef}
                    graphData={graphData}
                    nodeLabel={(node: any) => {
                      const isYou = node.id === youNodeId;
                      let label = isYou ? 'You' : (node.name || 'Unknown');
                      if (node.company) label += ` (${node.company})`;
                      if (node.title) label += ` - ${node.title}`;

                      // For Slack graph, add research summary
                      if (graphType === 'slack' && node.research_summary) {
                        label += `\n\n${node.research_summary}`;
                      }

                      return label;
                    }}
                    nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
                      // Identify if this is "You"
                      const isYou = node.id === youNodeId;
                      const label = isYou ? 'You' : (node.name || 'Unknown');

                      // Adjust size based on graph type
                      const fontSize = graphType === 'slack' ? 12 / globalScale : 22 / globalScale;
                      const nodeSize = graphType === 'slack' ? 35 : 85; // Smaller for Slack graph

                      // Generate varied colors based on node ID
                      const nodeHash = node.id.split('').reduce((acc: number, char: string) => acc + char.charCodeAt(0), 0);
                      const hueVariation = (nodeHash % 180); // 0-180 variation for wider range

                      // Different colors for "You" vs others
                      let accentColor, bgColor;
                      if (isYou) {
                        accentColor = '#F59E0B'; // Gold/amber for "You"
                        bgColor = '#FEF3C7'; // Light amber background
                      } else {
                        // Varied colors: blue, cyan, purple, pink, etc
                        const hue = 180 + hueVariation; // 180-360 (cyan, blue, purple, pink)
                        accentColor = `hsl(${hue}, 75%, 55%)`;
                        bgColor = '#FFFFFF';
                      }

                      // Draw shadow
                      ctx.shadowColor = 'rgba(0, 0, 0, 0.15)';
                      ctx.shadowBlur = 12;
                      ctx.shadowOffsetX = 0;
                      ctx.shadowOffsetY = 4;

                      // Draw main circle
                      ctx.beginPath();
                      ctx.arc(node.x, node.y, nodeSize, 0, 2 * Math.PI, false);
                      ctx.fillStyle = bgColor;
                      ctx.fill();

                      // Reset shadow
                      ctx.shadowColor = 'transparent';
                      ctx.shadowBlur = 0;

                      // Draw subtle outline
                      ctx.strokeStyle = '#E5E7EB';
                      ctx.lineWidth = 2;
                      ctx.stroke();

                      // Draw inner accent circle with varied color
                      ctx.beginPath();
                      ctx.arc(node.x, node.y, nodeSize - 8, 0, 2 * Math.PI, false);
                      ctx.strokeStyle = accentColor;
                      ctx.lineWidth = isYou ? 3.5 : 2.5; // Thicker for "You"
                      ctx.stroke();

                      // Draw label with shadow
                      ctx.font = `700 ${fontSize}px -apple-system, system-ui, sans-serif`;
                      ctx.textAlign = 'center';
                      ctx.textBaseline = 'middle';

                      const labelY = node.y + nodeSize + 25;
                      const textWidth = ctx.measureText(label).width;
                      const padding = 12;
                      const labelHeight = fontSize + 12;

                      // Label shadow
                      ctx.shadowColor = 'rgba(0, 0, 0, 0.1)';
                      ctx.shadowBlur = 8;
                      ctx.shadowOffsetY = 2;

                      // Label background with subtle border
                      ctx.fillStyle = '#FFFFFF';
                      ctx.fillRect(
                        node.x - textWidth / 2 - padding,
                        labelY - labelHeight / 2,
                        textWidth + padding * 2,
                        labelHeight
                      );

                      ctx.strokeStyle = '#E5E7EB';
                      ctx.lineWidth = 1;
                      ctx.strokeRect(
                        node.x - textWidth / 2 - padding,
                        labelY - labelHeight / 2,
                        textWidth + padding * 2,
                        labelHeight
                      );

                      // Reset shadow for text
                      ctx.shadowColor = 'transparent';

                      // Label text
                      ctx.fillStyle = '#1F2937';
                      ctx.fillText(label, node.x, labelY);
                    }}
                    linkLabel={(link: any) => {
                      if (graphType === 'slack') {
                        // Slack graph: show detailed connection reason
                        const priority = link.priority || 'medium';
                        const priorityIcon = priority === 'high' ? '⭐' : priority === 'medium' ? '✨' : '💫';
                        const reason = link.reason || 'Professional connection';
                        const weight = link.weight?.toFixed(1) || '0.0';

                        return `${priorityIcon} ${priority.toUpperCase()} Priority\n\n${reason}\n\nStrength: ${weight}`;
                      } else {
                        // Events graph: original format
                        const type = link.connection_type === 'same_event' ? '🎯 Same Event' :
                                     link.connection_type === 'same_company' ? '🏢 Same Company' :
                                     '💡 Common Topics';
                        const context = link.context || 'Connected';

                        // Vary description based on connection strength
                        let strengthDesc = '';
                        if (link.weight > 4.5) {
                          strengthDesc = '⭐ Very Strong Connection';
                        } else if (link.weight > 4.0) {
                          strengthDesc = '🔥 Strong Connection';
                        } else if (link.weight > 3.5) {
                          strengthDesc = '✨ Moderate Connection';
                        } else {
                          strengthDesc = '💫 Light Connection';
                        }

                        return `${type}\n${context}\n${strengthDesc} (${link.weight.toFixed(1)})`;
                      }
                    }}
                    linkColor={(link: any) => {
                      // Color intensity based on weight
                      const baseColor = link.connection_type === 'same_company' ?
                        { r: 16, g: 185, b: 129 } : // Green for company
                        { r: 59, g: 130, b: 246 }; // Blue for topics

                      const alpha = Math.min(0.3 + (link.weight * 0.2), 0.9);
                      return `rgba(${baseColor.r}, ${baseColor.g}, ${baseColor.b}, ${alpha})`;
                    }}
                    linkWidth={(link: any) => {
                      // THIN lines with dramatic variation
                      // Weight 3.1 = 1px (barely visible)
                      // Weight 3.5 = 2px
                      // Weight 4.0 = 3px
                      // Weight 4.5 = 4px
                      // Weight 5.0 = 5px (thickest)
                      const minWeight = 3.1;
                      const maxWeight = 5.0;
                      const normalized = (link.weight - minWeight) / (maxWeight - minWeight);
                      return Math.max(0.5, Math.min(normalized * 5, 6));
                    }}
                    linkDirectionalParticles={(link: any) => {
                      // More particles for stronger connections
                      return link.weight > 2 ? 4 : 2;
                    }}
                    linkDirectionalParticleWidth={(link: any) => Math.min(link.weight * 1.5, 4)}
                    linkDirectionalParticleSpeed={0.004}
                    onNodeClick={(node: any) => setSelectedNode(node as GraphNode)}
                    onNodeDrag={(node: any) => {
                      // Fix node position while dragging
                      node.fx = node.x;
                      node.fy = node.y;
                    }}
                    onNodeDragEnd={(node: any) => {
                      // Keep node fixed where user dropped it
                      node.fx = node.x;
                      node.fy = node.y;
                    }}
                    backgroundColor="transparent"
                    width={dimensions.width}
                    height={dimensions.height}
                    zoom={0.35}
                    minZoom={0.3}
                    maxZoom={2.5}
                    d3AlphaDecay={0.005}
                    d3VelocityDecay={0.1}
                    d3ForceConfig={{
                      charge: {
                        strength: graphType === 'slack' ? -5000 : -3000, // Stronger repulsion for Slack
                        distanceMax: graphType === 'slack' ? 3000 : 2000
                      },
                      link: {
                        distance: graphType === 'slack' ? 600 : 400, // More spacing for Slack
                        strength: 0.1
                      },
                      center: {
                        strength: 0.5 // Moderate centering to keep graph in view
                      }
                    }}
                    cooldownTime={10000}
                    warmupTicks={300}
                    nodeRelSize={15}
                    linkHoverPrecision={15}
                    enableNodeDrag={true}
                    enableZoomInteraction={true}
                    enablePanInteraction={true}
                  />
                  );
                })()}
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
