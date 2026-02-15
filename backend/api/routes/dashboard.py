"""
Dashboard API endpoints for metrics and analytics.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from db.session import get_db_session
from db.models import Conversation, Participant, Entity, ActionItem, FollowUpMessage
from services.transcript_storage import transcript_storage
from utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# Response models
class MetricResponse(BaseModel):
    """Dashboard metric response."""
    label: str
    value: int
    trend: str
    icon: str


class ActivityItem(BaseModel):
    """Activity feed item."""
    id: str
    icon: str
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    time: str
    link: str
    type: str


class FollowUpSuggestion(BaseModel):
    """Follow-up suggestion for a person."""
    id: str
    name: str
    company: Optional[str] = None
    email: Optional[str] = None
    last_interaction: str
    reason: str
    priority: str  # 'hot', 'warm', 'cold'


class DashboardMetrics(BaseModel):
    """Complete dashboard metrics."""
    metrics: List[MetricResponse]
    recent_activity: List[ActivityItem]


class FollowUpSuggestions(BaseModel):
    """Follow-up suggestions response."""
    suggestions: List[FollowUpSuggestion]


@router.get("/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    db: AsyncSession = Depends(get_db_session)
) -> DashboardMetrics:
    """
    Get dashboard metrics from database and GCS transcripts.

    Returns:
        Dashboard metrics including counts and recent activity
    """
    try:
        # Get transcripts from GCS (representing events)
        transcripts = transcript_storage.list_transcripts()
        total_events = len(transcripts)

        # Get recent events (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_transcripts = []
        for t in transcripts:
            if t.get('created_at'):
                try:
                    created_at = datetime.fromisoformat(t['created_at'])
                    # Remove timezone info for comparison
                    if created_at.tzinfo:
                        created_at = created_at.replace(tzinfo=None)
                    if created_at > week_ago:
                        recent_transcripts.append(t)
                except:
                    continue
        recent_events = len(recent_transcripts)

        # Get participants count from database
        result = await db.execute(
            select(func.count(distinct(Participant.id)))
        )
        total_participants = result.scalar() or 0

        # Get recent participants (last 7 days)
        result = await db.execute(
            select(func.count(distinct(Participant.id)))
            .where(Participant.created_at >= week_ago)
        )
        recent_participants = result.scalar() or 0

        # Get follow-up messages count
        result = await db.execute(
            select(func.count(FollowUpMessage.id))
        )
        total_followups = result.scalar() or 0

        # Get recent follow-ups (last 7 days)
        result = await db.execute(
            select(func.count(FollowUpMessage.id))
            .where(FollowUpMessage.created_at >= week_ago)
        )
        recent_followups = result.scalar() or 0

        # Get unique participants with emails (active connections)
        result = await db.execute(
            select(func.count(distinct(Participant.email)))
            .where(Participant.email.isnot(None))
        )
        active_connections = result.scalar() or 0

        # Build metrics
        metrics = [
            MetricResponse(
                label="Events Attended",
                value=total_events,
                trend=f"+{recent_events} this week" if recent_events > 0 else "No new events",
                icon="📅"
            ),
            MetricResponse(
                label="People Met",
                value=total_participants,
                trend=f"+{recent_participants} this week" if recent_participants > 0 else "No new people",
                icon="👥"
            ),
            MetricResponse(
                label="Follow-ups Sent",
                value=total_followups,
                trend=f"+{recent_followups} this week" if recent_followups > 0 else "No recent follow-ups",
                icon="✅"
            ),
            MetricResponse(
                label="Active Connections",
                value=active_connections,
                trend=f"{active_connections} with emails",
                icon="🤝"
            )
        ]

        # Build recent activity feed
        activity = []

        # Add recent events from GCS
        for transcript in recent_transcripts[:3]:  # Top 3 recent events
            title = transcript.get('title', transcript.get('file_name', 'Untitled Event'))
            if transcript.get('created_at'):
                created_at = datetime.fromisoformat(transcript['created_at'])
                if created_at.tzinfo:
                    created_at = created_at.replace(tzinfo=None)
            else:
                created_at = datetime.utcnow()
            time_ago = _format_time_ago(created_at)

            activity.append(ActivityItem(
                id=transcript['id'],
                icon="📅",
                title=title.replace('.txt', '').replace('_', ' '),
                subtitle=created_at.strftime('%B %d, %Y'),
                description=f"View transcript",
                time=time_ago,
                link=f"/conversations/{transcript['id']}",
                type="event"
            ))

        # Add recent follow-ups from database
        result = await db.execute(
            select(FollowUpMessage)
            .order_by(FollowUpMessage.created_at.desc())
            .limit(2)
        )
        followup_messages = result.scalars().all()

        for msg in followup_messages:
            time_ago = _format_time_ago(msg.created_at)
            recipient = msg.recipient_name or msg.recipient_email or "Unknown"

            activity.append(ActivityItem(
                id=msg.id,
                icon="📧",
                title=f"Follow-up sent to {recipient}",
                subtitle=None,
                description=None,
                time=time_ago,
                link=f"/conversations/{msg.conversation_id}",
                type="followup"
            ))

        # Sort activity by most recent
        activity.sort(key=lambda x: x.time)

        return DashboardMetrics(
            metrics=metrics,
            recent_activity=activity[:6]  # Top 6 items
        )

    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get dashboard metrics: {str(e)}"
        )


@router.get("/follow-ups", response_model=FollowUpSuggestions)
async def get_follow_up_suggestions(
    db: AsyncSession = Depends(get_db_session),
    limit: int = 3
) -> FollowUpSuggestions:
    """
    Get AI-suggested follow-ups based on recent interactions.

    Args:
        db: Database session
        limit: Number of suggestions to return

    Returns:
        List of follow-up suggestions
    """
    try:
        # Get recent participants who haven't been followed up with
        result = await db.execute(
            select(Participant)
            .order_by(Participant.created_at.desc())
            .limit(limit * 2)  # Get more to filter
        )
        participants = result.scalars().all()

        suggestions = []
        for participant in participants:
            if len(suggestions) >= limit:
                break

            # Determine priority based on lead_score
            priority = participant.lead_priority or 'warm'
            if not participant.lead_priority:
                if participant.lead_score >= 8.0:
                    priority = 'hot'
                elif participant.lead_score >= 5.0:
                    priority = 'warm'
                else:
                    priority = 'cold'

            # Generate reason for follow-up
            reasons = {
                'hot': f"High-priority lead from recent conversation",
                'warm': f"Expressed interest, good time to follow up",
                'cold': f"Keep the connection warm"
            }

            time_ago = _format_time_ago(participant.created_at)

            suggestions.append(FollowUpSuggestion(
                id=participant.id,
                name=participant.name or "Unknown Contact",
                company=participant.company,
                email=participant.email,
                last_interaction=time_ago,
                reason=reasons.get(priority, "Stay in touch"),
                priority=priority
            ))

        # If no participants in DB, return sample suggestions
        if not suggestions:
            suggestions = [
                FollowUpSuggestion(
                    id="sample-1",
                    name="Upload transcripts to see suggestions",
                    company=None,
                    email=None,
                    last_interaction="",
                    reason="Process conversations to get AI-powered follow-up suggestions",
                    priority="warm"
                )
            ]

        return FollowUpSuggestions(suggestions=suggestions)

    except Exception as e:
        logger.error(f"Error getting follow-up suggestions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get follow-up suggestions: {str(e)}"
        )


def _format_time_ago(dt: datetime) -> str:
    """Format datetime as 'X time ago' string."""
    now = datetime.utcnow()
    diff = now - dt

    if diff.days > 0:
        if diff.days == 1:
            return "1 day ago"
        elif diff.days < 7:
            return f"{diff.days} days ago"
        elif diff.days < 30:
            weeks = diff.days // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        else:
            months = diff.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"

    hours = diff.seconds // 3600
    if hours > 0:
        return f"{hours} hour{'s' if hours > 1 else ''} ago"

    minutes = diff.seconds // 60
    if minutes > 0:
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"

    return "just now"
