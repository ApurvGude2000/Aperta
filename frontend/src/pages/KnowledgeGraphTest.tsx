// ABOUTME: Temporary test component to debug knowledge graph issues
// ABOUTME: Minimal version without ForceGraph to isolate the problem

import React, { useState, useEffect } from 'react';
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

interface KnowledgeGraphData {
  nodes: GraphNode[];
  edges: any[];
  stats: {
    total_people: number;
    total_connections: number;
    total_events: number;
    total_companies: number;
  };
}

export function KnowledgeGraphTest() {
  const [graphData, setGraphData] = useState<KnowledgeGraphData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
      setGraphData(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching knowledge graph:', err);
      setError(err instanceof Error ? err.message : 'Failed to load knowledge graph');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F5F7FA]">
      <Navigation isAuthenticated={true} />

      <main className="max-w-7xl mx-auto p-8">
        <div className="mb-8">
          <h1 className="font-display text-3xl font-bold text-[#121417] mb-2">Knowledge Graph Test</h1>
          <p className="text-[#6B7280]">Testing basic functionality</p>
        </div>

        <Card>
          {loading && <p>Loading...</p>}
          {error && <p className="text-red-500">Error: {error}</p>}
          {!loading && !error && graphData && (
            <div>
              <h2 className="text-xl font-bold mb-4">Graph Data Retrieved:</h2>
              <pre className="bg-gray-100 p-4 rounded overflow-auto">
                {JSON.stringify(graphData, null, 2)}
              </pre>
              <div className="mt-4">
                <p><strong>Total People:</strong> {graphData.stats.total_people}</p>
                <p><strong>Total Connections:</strong> {graphData.stats.total_connections}</p>
                <p><strong>Total Events:</strong> {graphData.stats.total_events}</p>
              </div>
            </div>
          )}
        </Card>
      </main>
    </div>
  );
}
