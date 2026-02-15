# ABOUTME: API endpoint for generating knowledge graph from Slack members using Perplexity research
# ABOUTME: Analyzes connections between Slack channel members and returns strongest connections only

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import re
import httpx
import asyncio
from collections import defaultdict

from agents import CrossPollinationAgent
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/knowledge-graph", tags=["Knowledge Graph"])


class SlackMember(BaseModel):
    """A member from the Slack channel."""
    username: str
    display_name: str
    real_name: str
    company: Optional[str] = None


class SlackGraphNode(BaseModel):
    """A node in the Slack knowledge graph."""
    id: str
    name: str
    company: Optional[str] = None
    research_summary: Optional[str] = None
    connection_count: int = 0


class SlackGraphEdge(BaseModel):
    """An edge in the Slack knowledge graph."""
    source: str
    target: str
    weight: float
    reason: str
    priority: str  # high, medium, low


class SlackKnowledgeGraphResponse(BaseModel):
    """Response for Slack members knowledge graph."""
    nodes: List[SlackGraphNode]
    edges: List[SlackGraphEdge]
    stats: Dict[str, int]


def parse_excel_txt(file_path: str) -> List[SlackMember]:
    """
    Parse excel.txt file to extract Slack member information.

    Format: username\tdisplay_name\treal_name\t...
    Company is extracted from display_name in brackets like [Company]
    """
    members = []

    if not os.path.exists(file_path):
        logger.error(f"excel.txt not found at {file_path}")
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 3:
                continue

            username = parts[0]
            display_name = parts[1]
            real_name = parts[2]

            # Extract company from display_name (format: [Company] Name)
            company = None
            company_match = re.match(r'\[([^\]]+)\]', display_name)
            if company_match:
                company = company_match.group(1)

            members.append(SlackMember(
                username=username,
                display_name=display_name,
                real_name=real_name if real_name else display_name,
                company=company
            ))

    logger.info(f"Parsed {len(members)} Slack members from excel.txt")
    return members


async def research_person_with_perplexity(
    name: str,
    company: Optional[str],
    api_key: str
) -> str:
    """
    Use Perplexity Sonar API to research a person.

    Returns a brief professional summary.
    """
    if not api_key:
        return "No API key configured"

    if not name:
        return "No name provided"

    # Build search query
    query = f"{name}"
    if company:
        query += f" at {company}"

    logger.info(f"Researching: {query}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "sonar",
                    "messages": [
                        {
                            "role": "user",
                            "content": f"Who is {query}? Provide a brief professional summary in 2-3 sentences focusing on their work, expertise, and current role."
                        }
                    ],
                    "max_tokens": 200,
                    "temperature": 0.2,
                    "search_recency_filter": "month"
                },
                timeout=30.0
            )

        if response.status_code == 200:
            data = response.json()
            research = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return research if research else "No information found"
        else:
            logger.warning(f"Perplexity API error: {response.status_code}")
            return f"API error: {response.status_code}"

    except Exception as e:
        logger.error(f"Perplexity API call failed for {name}: {e}")
        return "Research failed"


async def analyze_connections(
    members_with_research: List[Dict],
    agent: CrossPollinationAgent
) -> List[Dict]:
    """
    Use CrossPollinationAgent to find connections between members.

    Returns list of connection suggestions.
    """
    try:
        result = await agent.find_connections(
            people_met=members_with_research,
            event_id="slack_members"
        )

        return result.get("introductions", [])

    except Exception as e:
        logger.error(f"Connection analysis failed: {e}")
        return []


@router.get("/slack-members", response_model=SlackKnowledgeGraphResponse)
async def get_slack_members_knowledge_graph() -> SlackKnowledgeGraphResponse:
    """
    Generate knowledge graph from Slack members with Perplexity research.

    This endpoint:
    1. Parses excel.txt to get Slack members
    2. Uses Perplexity to research each person (limited batch to avoid rate limits)
    3. Analyzes connections using AI
    4. Returns graph with only STRONG connections
    """
    try:
        logger.info("Building Slack members knowledge graph...")

        # Step 1: Parse excel.txt
        excel_path = os.path.join(os.path.dirname(__file__), "../../excel.txt")
        members = parse_excel_txt(excel_path)

        if not members:
            raise HTTPException(status_code=404, detail="No members found in excel.txt")

        # Process all members (no limit)
        logger.info(f"Processing {len(members)} members")

        # Step 2: Research each person with Perplexity (batch with delays)
        api_key = settings.perplexity_api_key
        members_with_research = []

        if api_key:
            logger.info("Using Perplexity API for member research")
            for i, member in enumerate(members):
                research = await research_person_with_perplexity(
                    name=member.real_name,
                    company=member.company,
                    api_key=api_key
                )

                members_with_research.append({
                    "id": member.username,
                    "name": member.real_name,
                    "company": member.company,
                    "perplexity_research": research
                })

                # Rate limiting: wait between requests
                if i < len(members) - 1:
                    await asyncio.sleep(1)  # 1 second between requests
        else:
            logger.info("No Perplexity API key - using basic member info")
            for member in members:
                # Use basic info without Perplexity research
                research = f"Slack member"
                if member.company:
                    research += f" at {member.company}"

                members_with_research.append({
                    "id": member.username,
                    "name": member.real_name,
                    "company": member.company,
                    "perplexity_research": research
                })

        logger.info(f"Completed research for {len(members_with_research)} members")

        # Step 3: Analyze connections
        agent = CrossPollinationAgent()
        connections = await analyze_connections(members_with_research, agent)

        logger.info(f"Found {len(connections)} potential connections")

        # Step 4: Filter to STRONG and MEDIUM connections (high and medium priority)
        # Sort by priority (high first) and take top 8-10
        priority_order = {"high": 3, "medium": 2, "low": 1}
        sorted_connections = sorted(
            connections,
            key=lambda c: (priority_order.get(c.get("priority", "low"), 0), c.get("score", 0)),
            reverse=True
        )
        strong_connections = sorted_connections[:10]  # Take top 10 connections

        logger.info(f"Selected {len(strong_connections)} top connections")

        # Step 5: Build graph structure
        nodes = []
        edges = []
        connection_counts = defaultdict(int)

        # Create nodes
        for member_data in members_with_research:
            nodes.append(SlackGraphNode(
                id=member_data["id"],
                name=member_data["name"],
                company=member_data.get("company"),
                research_summary=member_data.get("perplexity_research", "")[:200],  # Truncate
                connection_count=0  # Will update below
            ))

        # Create edges from strong connections
        for conn in strong_connections:
            person_a_name = conn.get("person_a", "")
            person_b_name = conn.get("person_b", "")

            # Find member IDs by name (case-insensitive partial match)
            person_a_id = None
            person_b_id = None

            for m in members_with_research:
                if person_a_name.lower() in m["name"].lower() or m["name"].lower() in person_a_name.lower():
                    person_a_id = m["id"]
                if person_b_name.lower() in m["name"].lower() or m["name"].lower() in person_b_name.lower():
                    person_b_id = m["id"]

            if person_a_id and person_b_id:
                # Calculate weight based on priority and score
                priority = conn.get("priority", "high")
                score = conn.get("score", 0.8)  # Default high score

                # Weight: high=5.0, medium=3.0, low=1.0, scaled by score
                priority_weights = {"high": 5.0, "medium": 3.0, "low": 1.0}
                base_weight = priority_weights.get(priority, 3.0)
                weight = base_weight * score

                logger.info(f"Creating edge: {person_a_name} -> {person_b_name} | Priority: {priority} | Weight: {weight:.2f}")

                edges.append(SlackGraphEdge(
                    source=person_a_id,
                    target=person_b_id,
                    weight=weight,
                    reason=conn.get("reason", "Strong professional connection"),
                    priority=priority
                ))

                # Track connection strength, not just count
                connection_counts[person_a_id] += weight
                connection_counts[person_b_id] += weight
            else:
                logger.warning(f"Could not match names: {person_a_name} <-> {person_b_name}")

        # Update connection counts (now connection strength)
        for node in nodes:
            node.connection_count = int(connection_counts.get(node.id, 0))

        # Filter to only nodes with connections and sort by strength
        connected_nodes = [n for n in nodes if n.connection_count > 0]
        connected_nodes.sort(key=lambda n: n.connection_count, reverse=True)

        # Take top nodes to show ~8 edges (approximately 16 nodes for good connectivity)
        top_node_count = min(20, max(10, len(connected_nodes)))
        top_nodes = connected_nodes[:top_node_count]
        top_node_ids = {n.id for n in top_nodes}

        # Filter edges to only include those between top nodes
        filtered_edges = [e for e in edges if e.source in top_node_ids and e.target in top_node_ids]

        stats = {
            "total_members_analyzed": len(members),
            "total_connections": len(filtered_edges),
            "members_with_connections": len(connected_nodes),
            "total_members_displayed": len(top_nodes),
            "showing_top_n": top_node_count
        }

        logger.info(f"Slack knowledge graph built: {stats}")

        return SlackKnowledgeGraphResponse(
            nodes=top_nodes,
            edges=filtered_edges,
            stats=stats
        )

    except HTTPException as he:
        logger.error(f"HTTP Exception: {he.detail}")
        raise
    except Exception as e:
        logger.error(f"Error building Slack knowledge graph: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error building graph: {str(e)}")
