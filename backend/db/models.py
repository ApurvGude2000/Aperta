"""
Database models for the NetworkAI application.
"""
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Boolean, Text, JSON, ForeignKey, Enum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

Base = declarative_base()


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())


class ConversationStatusEnum(str, enum.Enum):
    """Conversation status enumeration."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ConsentStatusEnum(str, enum.Enum):
    """Consent status enumeration."""
    UNKNOWN = "unknown"
    GRANTED = "granted"
    DENIED = "denied"
    REVOKED = "revoked"


class LeadPriorityEnum(str, enum.Enum):
    """Lead priority enumeration."""
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"


class MessageStatusEnum(str, enum.Enum):
    """Follow-up message status enumeration."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENT = "sent"
    OPENED = "opened"
    CLICKED = "clicked"
    REPLIED = "replied"
    BOUNCED = "bounced"


class Conversation(Base):
    """Main conversation record."""
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=True)
    status = Column(String, default=ConversationStatusEnum.ACTIVE.value)
    transcript = Column(Text, nullable=True)
    recording_url = Column(String, nullable=True)
    location = Column(String, nullable=True)
    event_name = Column(String, nullable=True)

    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    participants = relationship("Participant", back_populates="conversation", cascade="all, delete-orphan")
    entities = relationship("Entity", back_populates="conversation", cascade="all, delete-orphan")
    action_items = relationship("ActionItem", back_populates="conversation", cascade="all, delete-orphan")
    privacy_logs = relationship("PrivacyAuditLog", back_populates="conversation", cascade="all, delete-orphan")


class Participant(Base):
    """Conversation participants."""
    __tablename__ = "participants"

    id = Column(String, primary_key=True, default=generate_uuid)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    company = Column(String, nullable=True)
    title = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    consent_status = Column(String, default=ConsentStatusEnum.UNKNOWN.value)
    consent_timestamp = Column(DateTime, nullable=True)

    lead_priority = Column(String, nullable=True)
    lead_score = Column(Float, default=0.0)

    extra_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", back_populates="participants")
    follow_ups = relationship("FollowUpMessage", back_populates="participant", cascade="all, delete-orphan")


class Entity(Base):
    """Extracted entities from conversations."""
    __tablename__ = "entities"

    id = Column(String, primary_key=True, default=generate_uuid)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    entity_type = Column(String, nullable=False)  # person, company, topic, technology, etc.
    entity_value = Column(String, nullable=False)
    canonical_id = Column(String, nullable=True)  # For entity resolution
    confidence = Column(Float, default=1.0)

    context = Column(Text, nullable=True)  # Surrounding text
    extra_data = Column(JSON, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", back_populates="entities")


class ActionItem(Base):
    """Action items and commitments from conversations."""
    __tablename__ = "action_items"

    id = Column(String, primary_key=True, default=generate_uuid)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)

    description = Column(Text, nullable=False)
    responsible_party = Column(String, nullable=True)  # Who should do it
    due_date = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)

    extra_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", back_populates="action_items")


class PrivacyAuditLog(Base):
    """Audit log for privacy-related actions."""
    __tablename__ = "privacy_audit_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=True)

    action = Column(String, nullable=False)  # detect, redact, pause, resume, delete
    entity_type = Column(String, nullable=True)  # PII type if applicable
    details = Column(JSON, default=dict)

    agent_decision = Column(Boolean, default=False)  # True if autonomous agent decision
    user_triggered = Column(Boolean, default=False)

    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    conversation = relationship("Conversation", back_populates="privacy_logs")


class FollowUpMessage(Base):
    """Follow-up messages generated for contacts."""
    __tablename__ = "follow_up_messages"

    id = Column(String, primary_key=True, default=generate_uuid)
    participant_id = Column(String, ForeignKey("participants.id"), nullable=False)

    message_type = Column(String, nullable=False)  # email, linkedin, sms
    subject = Column(String, nullable=True)  # For emails
    body = Column(Text, nullable=False)
    tone = Column(String, nullable=True)  # professional, casual, enthusiastic

    status = Column(String, default=MessageStatusEnum.DRAFT.value)

    scheduled_send_time = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    opened_at = Column(DateTime, nullable=True)
    replied_at = Column(DateTime, nullable=True)

    extra_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    participant = relationship("Participant", back_populates="follow_ups")


class UserGoal(Base):
    """User networking goals."""
    __tablename__ = "user_goals"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)

    goal_type = Column(String, nullable=False)  # job_seeking, fundraising, partnership, etc.
    description = Column(Text, nullable=False)
    priority = Column(Integer, default=5)  # 1-10 scale

    active = Column(Boolean, default=True)
    extra_data = Column(JSON, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Opportunity(Base):
    """Detected opportunities from conversations."""
    __tablename__ = "opportunities"

    id = Column(String, primary_key=True, default=generate_uuid)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    participant_id = Column(String, ForeignKey("participants.id"), nullable=True)

    opportunity_type = Column(String, nullable=False)  # buying_signal, collaboration, referral, etc.
    description = Column(Text, nullable=False)
    confidence = Column(Float, default=0.5)

    related_goal_id = Column(String, ForeignKey("user_goals.id"), nullable=True)

    extra_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)


class QASession(Base):
    """Q&A session tracking."""
    __tablename__ = "qa_sessions"

    id = Column(String, primary_key=True, default=generate_uuid)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=True)
    user_id = Column(String, nullable=False, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    interactions = relationship("QAInteraction", back_populates="session", cascade="all, delete-orphan")


class QAInteraction(Base):
    """Individual Q&A interaction within a session."""
    __tablename__ = "qa_interactions"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("qa_sessions.id"), nullable=False)
    
    question = Column(Text, nullable=False)
    routed_agents = Column(JSON, default=list)  # List of agent names that were invoked
    responses = Column(JSON, default=dict)  # Dict mapping agent names to their responses
    final_answer = Column(Text, nullable=True)
    execution_time = Column(Float, nullable=True)  # Time in seconds
    
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    session = relationship("QASession", back_populates="interactions")
