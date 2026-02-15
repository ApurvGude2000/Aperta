# ABOUTME: API endpoints for extracting participants from conversation transcripts
# ABOUTME: Uses Context Understanding Agent to parse and extract participant information

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional, Dict
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
    name: str
    company: Optional[str] = None
    title: Optional[str] = None
    email: Optional[str] = None
    linkedin_url: Optional[str] = None
    topics: List[str] = []
    role: str  # "recruiter" or "candidate"


class ExtractionResponse(BaseModel):
    """Response from participant extraction."""
    conversation_id: str
    participants_extracted: int
    participants: List[ParticipantInfo]
    conversations_parsed: int


@router.post("/extract/{conversation_id}", response_model=ExtractionResponse)
async def extract_participants_from_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db_session)
) -> ExtractionResponse:
    """
    Extract participants from a conversation transcript.

    Properly parses conversation structure to identify unique individuals,
    not individual lines.
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

        # Parse the transcript into conversation exchanges
        # Each exchange is a dialogue between recruiter and candidate
        exchanges = parse_conversation_exchanges(conversation.transcript)

        logger.info(f"Parsed {len(exchanges)} conversation exchanges")

        # Extract participants from each exchange
        participants_dict: Dict[str, ParticipantInfo] = {}  # Key: unique identifier

        for exchange in exchanges:
            # Analyze the exchange to extract both people
            candidate_info, recruiter_info = analyze_exchange(exchange)

            if candidate_info:
                # Create unique key based on role and identifiable info
                key = f"candidate_{candidate_info.get('title', '')}_{candidate_info.get('company', '')}"
                if key not in participants_dict:
                    participants_dict[key] = candidate_info
                else:
                    # Merge topics
                    existing = participants_dict[key]
                    existing["topics"] = list(set(existing.get("topics", []) + candidate_info.get("topics", [])))

            if recruiter_info:
                key = f"recruiter_{recruiter_info.get('company', '')}_{recruiter_info.get('title', '')}"
                if key not in participants_dict:
                    participants_dict[key] = recruiter_info
                else:
                    # Merge topics
                    existing = participants_dict[key]
                    existing["topics"] = list(set(existing.get("topics", []) + recruiter_info.get("topics", [])))

        # Create participant records in database
        participants_list = []
        for idx, (key, info) in enumerate(participants_dict.items(), 1):
            participant = Participant(
                conversation_id=conversation_id,
                name=info.get("name", f"Person {idx}"),
                company=info.get("company"),
                title=info.get("title"),
                email=info.get("email"),
                linkedin_url=info.get("linkedin_url")
            )
            db.add(participant)

            # Create entity records for topics
            for topic in info.get("topics", []):
                entity = Entity(
                    conversation_id=conversation_id,
                    entity_type="topic",
                    entity_value=topic
                )
                db.add(entity)

            participants_list.append(ParticipantInfo(
                name=participant.name,
                company=participant.company,
                title=participant.title,
                email=participant.email,
                linkedin_url=participant.linkedin_url,
                topics=info.get("topics", []),
                role=info.get("role", "unknown")
            ))

        await db.commit()

        logger.info(f"Successfully extracted {len(participants_list)} unique participants")

        return ExtractionResponse(
            conversation_id=conversation_id,
            participants_extracted=len(participants_list),
            participants=participants_list,
            conversations_parsed=len(exchanges)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting participants: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error extracting participants: {str(e)}")


def parse_conversation_exchanges(transcript: str) -> List[str]:
    """
    Parse transcript into individual conversation exchanges.
    Each exchange is separated by double newlines.
    """
    # Split by double newlines (conversation boundaries)
    exchanges = transcript.split('\n\n')
    exchanges = [e.strip() for e in exchanges if e.strip() and len(e.strip()) > 30]
    return exchanges


def analyze_exchange(exchange: str) -> tuple:
    """
    Analyze a conversation exchange to extract candidate and recruiter information.

    Returns: (candidate_info, recruiter_info)
    """
    lines = [line.strip().strip('"') for line in exchange.split('\n') if line.strip()]

    candidate_info = {
        "name": "Job Candidate",
        "role": "candidate",
        "company": None,
        "title": None,
        "topics": []
    }

    recruiter_info = {
        "name": "Company Recruiter",
        "role": "recruiter",
        "company": None,
        "title": None,
        "topics": []
    }

    # Analyze the full exchange text
    exchange_lower = exchange.lower()

    # Extract candidate information (lines 2, 4, 6... typically candidate)
    candidate_lines = []
    recruiter_lines = []

    for i, line in enumerate(lines):
        if i % 2 == 0:
            recruiter_lines.append(line)
        else:
            candidate_lines.append(line)

    candidate_text = ' '.join(candidate_lines)
    recruiter_text = ' '.join(recruiter_lines)

    # Extract candidate info
    candidate_info = extract_person_info(candidate_text, "candidate")

    # Extract recruiter info
    recruiter_info = extract_person_info(recruiter_text, "recruiter")

    # Extract topics from full exchange
    topics = extract_topics(exchange_lower)
    candidate_info["topics"] = topics
    recruiter_info["topics"] = topics

    return candidate_info, recruiter_info


def extract_person_info(text: str, role: str) -> dict:
    """Extract person information from text."""
    info = {
        "role": role,
        "name": "Job Candidate" if role == "candidate" else "Company Recruiter",
        "company": None,
        "title": None,
        "topics": []
    }

    # Extract company
    company_patterns = [
        r"work(?:ing)? (?:at|for|with) ([A-Z][A-Za-z\s&]+?)(?:\.|,|'s|\?|$)",
        r"I'm (?:with|from) ([A-Z][A-Za-z\s&]+?)(?:\.|,|\?|$)",
        r"([A-Z][A-Za-z\s&]+?) (?:team|company|firm)",
    ]

    for pattern in company_patterns:
        match = re.search(pattern, text)
        if match:
            company = match.group(1).strip()
            if len(company) < 40 and company not in ["HR", "Engineering", "Marketing"]:
                info["company"] = company
                if role == "recruiter":
                    info["name"] = f"{company} Representative"
                break

    # Extract job titles
    title_patterns = [
        r"I'm (?:a|an|the) ([a-zA-Z\s]+?)(?:\.|,|for|at|with|\?)",
        r"([A-Z][a-z]+ (?:Engineer|Manager|Director|Analyst|Lead|Developer|Designer|Coordinator|Specialist|Intern))",
        r"(?:graduating|looking for) ([a-zA-Z\s-]+?) (?:role|position)",
        r"I'm (?:the )?([A-Z][a-z]+ [A-Z][a-z]+) for",
    ]

    for pattern in title_patterns:
        match = re.search(pattern, text)
        if match:
            title = match.group(1).strip()
            if len(title) < 50 and title not in ["Hi", "Hello", "Great", "Perfect"]:
                info["title"] = title
                if role == "candidate" and not info.get("name"):
                    info["name"] = f"Candidate ({title})"
                break

    return info


def extract_topics(text: str) -> List[str]:
    """Extract discussion topics from conversation text."""
    topic_keywords = {
        "Software Engineering": ["software", "API", "codebase", "developer", "engineering", "technical", "coding", "programming"],
        "Data Science": ["data science", "SQL", "predictive", "analytics", "data"],
        "Marketing": ["marketing", "consumer behavior", "branding"],
        "Finance": ["fintech", "investment", "accounting", "financial"],
        "Project Management": ["project coordination", "management", "coordinator"],
        "Infrastructure": ["infrastructure", "construction"],
        "HR & Recruiting": ["HR", "recruiting", "hiring", "talent"],
        "Sustainability": ["sustainability", "environmental", "carbon offset"],
        "Design & UX": ["UX", "design", "prototyping", "Figma", "user experience"],
        "Security & Government": ["security clearance", "government", "national"],
        "Operations": ["operations", "supply chain", "logistics", "vendor"],
    }

    topics = []
    for topic, keywords in topic_keywords.items():
        if any(keyword in text for keyword in keywords):
            topics.append(topic)

    return topics[:3]  # Max 3 topics per exchange
