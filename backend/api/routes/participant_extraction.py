# ABOUTME: API endpoints for extracting participants from conversation transcripts
# ABOUTME: Uses Context Understanding Agent to parse and extract participant information

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
import logging
import re

from db.session import get_db_session
from db.models import Conversation, Participant, Entity
from agents import ContextUnderstandingAgent
from utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/participants", tags=["Participant Extraction"])


class ParticipantInfo(BaseModel):
    """Extracted participant information."""
    name: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    email: Optional[str] = None
    linkedin_url: Optional[str] = None
    topics: List[str] = []


class ExtractionResponse(BaseModel):
    """Response from participant extraction."""
    conversation_id: str
    participants_extracted: int
    participants: List[ParticipantInfo]


@router.post("/extract/{conversation_id}", response_model=ExtractionResponse)
async def extract_participants_from_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db_session)
) -> ExtractionResponse:
    """
    Extract participants from a conversation transcript.

    This analyzes the conversation text and creates participant records
    for each person identified in the conversation.
    """
    try:
        logger.info(f"Extracting participants from conversation {conversation_id}")

        # Fetch conversation
        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        if not conversation.transcript:
            raise HTTPException(status_code=400, detail="Conversation has no transcript")

        # Split transcript into individual conversations
        # The transcript has multiple conversation snippets separated by blank lines
        conversation_snippets = conversation.transcript.split('\n\n')
        conversation_snippets = [s.strip() for s in conversation_snippets if s.strip()]

        logger.info(f"Found {len(conversation_snippets)} conversation snippets")

        participants_extracted = []
        context_agent = ContextUnderstandingAgent()

        for idx, snippet in enumerate(conversation_snippets):
            try:
                # Parse the snippet to extract participant info
                participant_info = await extract_participant_from_snippet(
                    snippet,
                    conversation_id,
                    conversation.event_name or "Unknown Event",
                    idx
                )

                if participant_info:
                    # Create participant record
                    participant = Participant(
                        conversation_id=conversation_id,
                        name=participant_info.get("name", f"Person {idx + 1}"),
                        company=participant_info.get("company"),
                        title=participant_info.get("title"),
                        email=participant_info.get("email"),
                        linkedin_url=participant_info.get("linkedin_url")
                    )
                    db.add(participant)

                    # Create entity records for topics
                    for topic in participant_info.get("topics", []):
                        entity = Entity(
                            conversation_id=conversation_id,
                            entity_type="topic",
                            entity_value=topic
                        )
                        db.add(entity)

                    participants_extracted.append(ParticipantInfo(
                        name=participant.name,
                        company=participant.company,
                        title=participant.title,
                        email=participant.email,
                        linkedin_url=participant.linkedin_url,
                        topics=participant_info.get("topics", [])
                    ))

            except Exception as e:
                logger.warning(f"Failed to extract participant from snippet {idx}: {e}")
                continue

        # Commit all participants
        await db.commit()

        logger.info(f"Extracted {len(participants_extracted)} participants")

        return ExtractionResponse(
            conversation_id=conversation_id,
            participants_extracted=len(participants_extracted),
            participants=participants_extracted
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting participants: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error extracting participants: {str(e)}")


async def extract_participant_from_snippet(
    snippet: str,
    conversation_id: str,
    event_name: str,
    snippet_idx: int
) -> Optional[dict]:
    """
    Extract participant information from a conversation snippet.

    Uses pattern matching and keyword extraction to identify:
    - Company names
    - Job titles/roles
    - Topics discussed
    """

    if not snippet or len(snippet) < 20:
        return None

    participant_info = {
        "name": None,
        "company": None,
        "title": None,
        "topics": []
    }

    # Extract company mentions
    company_patterns = [
        r"work(?:ing)? (?:at|for|with) ([A-Z][A-Za-z\s&]+?)(?:\.|,|'s|$)",
        r"from ([A-Z][A-Za-z\s&]+?) (?:here|today)",
        r"I'm (?:with|from) ([A-Z][A-Za-z\s&]+?)(?:\.|,|$)",
        r"([A-Z][A-Za-z\s&]+?) team",
    ]

    for pattern in company_patterns:
        match = re.search(pattern, snippet)
        if match:
            participant_info["company"] = match.group(1).strip()
            break

    # Extract job titles/roles
    title_patterns = [
        r"I'm (?:a|an|the) ([a-zA-Z\s]+?)(?:\.|,|for|at|with)",
        r"([A-Z][a-z]+ (?:Engineer|Manager|Director|Analyst|Lead|Developer|Designer|Coordinator|Specialist))",
        r"(?:graduating|looking for) ([a-zA-Z\s-]+?) (?:role|position)",
    ]

    for pattern in title_patterns:
        match = re.search(pattern, snippet)
        if match:
            title = match.group(1).strip()
            if len(title) < 50:  # Sanity check
                participant_info["title"] = title
                break

    # Extract topics discussed
    topic_keywords = {
        "Software Engineering": ["software", "API", "codebase", "developer", "engineering", "technical"],
        "Data Science": ["data science", "SQL", "predictive", "analytics"],
        "Marketing": ["marketing", "consumer behavior", "branding"],
        "Finance": ["fintech", "investment", "accounting"],
        "Project Management": ["project coordination", "management"],
        "Infrastructure": ["infrastructure", "construction"],
        "HR": ["HR", "recruiting", "hiring"],
        "Sustainability": ["sustainability", "environmental", "carbon offset"],
        "Design": ["UX", "design", "prototyping", "Figma"],
        "Security": ["security clearance", "government"],
    }

    snippet_lower = snippet.lower()
    for topic, keywords in topic_keywords.items():
        if any(keyword in snippet_lower for keyword in keywords):
            participant_info["topics"].append(topic)

    # If no name extracted, create a placeholder
    if not participant_info["name"]:
        if participant_info["company"]:
            participant_info["name"] = f"{participant_info['company']} Representative"
        elif participant_info["title"]:
            participant_info["name"] = participant_info["title"]
        else:
            participant_info["name"] = f"Attendee {snippet_idx + 1}"

    return participant_info
