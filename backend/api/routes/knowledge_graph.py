"""
Knowledge Graph API for visualizing connections between people.
Analyzes conversations, participants, and entities to build a network graph.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import List, Dict, Optional
from collections import defaultdict
import logging

from db.session import get_db_session
from db.models import Conversation, Participant, Entity, Transcription
from agents import CrossPollinationAgent, ContextUnderstandingAgent
from utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/knowledge-graph", tags=["Knowledge Graph"])


# Response Models
class GraphNode(BaseModel):
    """A node in the knowledge graph (person)."""
    id: str
    name: str
    company: Optional[str] = None
    title: Optional[str] = None
    email: Optional[str] = None
    linkedin_url: Optional[str] = None
    event_count: int = 0  # Number of events they attended
    connection_count: int = 0  # Number of connections
    topics: List[str] = []  # Topics they discussed


class GraphEdge(BaseModel):
    """An edge in the knowledge graph (connection between people)."""
    source: str  # participant_id
    target: str  # participant_id
    weight: float = 1.0  # Strength of connection
    connection_type: str  # "same_event", "same_company", "common_topics"
    context: Optional[str] = None  # Description of connection
    events: List[str] = []  # Event names where they connected


class KnowledgeGraphResponse(BaseModel):
    """Complete knowledge graph."""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    stats: Dict[str, int]


@router.get("/", response_model=KnowledgeGraphResponse)
async def get_knowledge_graph(
    db: AsyncSession = Depends(get_db_session)
) -> KnowledgeGraphResponse:
    """
    Generate knowledge graph from all conversations and participants.

    Returns:
        Knowledge graph with nodes (people) and edges (connections)
    """
    try:
        logger.info("Building knowledge graph...")

        # Fetch all participants with their conversations
        result = await db.execute(
            select(Participant, Conversation)
            .join(Conversation, Participant.conversation_id == Conversation.id)
        )
        participant_conversations = result.all()

        # Build participant index
        participants_dict = {}  # {participant_id: participant_data}
        participant_events = defaultdict(list)  # {participant_id: [event_names]}
        participant_companies = defaultdict(set)  # {company: {participant_ids}}

        for participant, conversation in participant_conversations:
            if participant.id not in participants_dict:
                participants_dict[participant.id] = {
                    "participant": participant,
                    "conversations": []
                }

            participants_dict[participant.id]["conversations"].append(conversation)

            if conversation.event_name:
                participant_events[participant.id].append(conversation.event_name)

            if participant.company:
                participant_companies[participant.company].add(participant.id)

        # Fetch entities for topic analysis
        entities_result = await db.execute(
            select(Entity).where(Entity.entity_type.in_(["topic", "technology", "company"]))
        )
        all_entities = entities_result.scalars().all()

        # Build entity connections
        conversation_entities = defaultdict(list)  # {conversation_id: [entities]}
        for entity in all_entities:
            conversation_entities[entity.conversation_id].append(entity.entity_value)

        # Build nodes
        nodes = []
        for participant_id, data in participants_dict.items():
            participant = data["participant"]
            conversations = data["conversations"]

            # Get topics this person discussed
            topics = []
            for conv in conversations:
                topics.extend(conversation_entities.get(conv.id, []))
            topics = list(set(topics))[:5]  # Top 5 unique topics

            node = GraphNode(
                id=participant_id,
                name=participant.name or "Unknown",
                company=participant.company,
                title=participant.title,
                email=participant.email,
                linkedin_url=participant.linkedin_url,
                event_count=len(conversations),
                connection_count=0,  # Will be updated later
                topics=topics
            )
            nodes.append(node)

        # Build edges
        edges = []
        edges_set = set()  # To avoid duplicates

        # Type 1: Same event connections
        event_participants = defaultdict(list)  # {event_name: [participant_ids]}
        for participant_id, events in participant_events.items():
            for event_name in events:
                event_participants[event_name].append(participant_id)

        for event_name, participant_ids in event_participants.items():
            # Create edges between all participants at same event
            for i, p1_id in enumerate(participant_ids):
                for p2_id in participant_ids[i+1:]:
                    edge_key = tuple(sorted([p1_id, p2_id]))

                    if edge_key not in edges_set:
                        edges_set.add(edge_key)
                        edge = GraphEdge(
                            source=p1_id,
                            target=p2_id,
                            weight=1.0,
                            connection_type="same_event",
                            context=f"Met at {event_name}",
                            events=[event_name]
                        )
                        edges.append(edge)
                    else:
                        # Add event to existing edge
                        for edge in edges:
                            if set([edge.source, edge.target]) == set([p1_id, p2_id]):
                                if event_name not in edge.events:
                                    edge.events.append(event_name)
                                    edge.weight += 0.5  # Increase weight for multiple meetings
                                    edge.context = f"Met at {len(edge.events)} events"
                                break

        # Type 2: Same company connections
        for company, participant_ids in participant_companies.items():
            participant_ids = list(participant_ids)
            if len(participant_ids) > 1:
                for i, p1_id in enumerate(participant_ids):
                    for p2_id in participant_ids[i+1:]:
                        edge_key = tuple(sorted([p1_id, p2_id]))

                        if edge_key not in edges_set:
                            edges_set.add(edge_key)
                            edge = GraphEdge(
                                source=p1_id,
                                target=p2_id,
                                weight=0.8,
                                connection_type="same_company",
                                context=f"Both work at {company}",
                                events=[]
                            )
                            edges.append(edge)

        # Type 3: Common topics connections
        participant_topics = {}  # {participant_id: set(topics)}
        for participant_id, data in participants_dict.items():
            topics = set()
            for conv in data["conversations"]:
                topics.update(conversation_entities.get(conv.id, []))
            participant_topics[participant_id] = topics

        # Find participants with 2+ common topics
        participant_ids = list(participant_topics.keys())
        for i, p1_id in enumerate(participant_ids):
            for p2_id in participant_ids[i+1:]:
                common_topics = participant_topics[p1_id] & participant_topics[p2_id]

                if len(common_topics) >= 2:  # At least 2 common topics
                    edge_key = tuple(sorted([p1_id, p2_id]))

                    if edge_key not in edges_set:
                        edges_set.add(edge_key)
                        topic_list = list(common_topics)[:3]
                        edge = GraphEdge(
                            source=p1_id,
                            target=p2_id,
                            weight=0.6,
                            connection_type="common_topics",
                            context=f"Common interests: {', '.join(topic_list)}",
                            events=[]
                        )
                        edges.append(edge)

        # Update connection counts
        connection_counts = defaultdict(int)
        for edge in edges:
            connection_counts[edge.source] += 1
            connection_counts[edge.target] += 1

        for node in nodes:
            node.connection_count = connection_counts.get(node.id, 0)

        # Build stats
        stats = {
            "total_people": len(nodes),
            "total_connections": len(edges),
            "total_events": len(event_participants),
            "total_companies": len(participant_companies)
        }

        logger.info(f"Knowledge graph built: {stats}")

        return KnowledgeGraphResponse(
            nodes=nodes,
            edges=edges,
            stats=stats
        )

    except Exception as e:
        logger.error(f"Error building knowledge graph: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error building knowledge graph: {str(e)}")
