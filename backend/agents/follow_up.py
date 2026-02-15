"""
AG6: Follow-Up Agent - Generates personalized follow-up messages and manages outreach.
Priority: 1 (CRITICAL) - Automates relationship building and follow-ups.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy import select
from .base import ClaudeBaseAgent
from utils.logger import setup_logger
from db.session import AsyncSessionLocal
from db.models import Participant, FollowUpMessage, Conversation, ActionItem

logger = setup_logger(__name__)


class FollowUpAgent(ClaudeBaseAgent):
    """
    Follow-Up Agent - AG6

    Responsibilities:
    1. Lead categorization (hot/warm/cold)
    2. Personalized message generation
    3. LinkedIn connection request drafting
    4. Professional email composition
    5. Optimal timing suggestions
    6. Response tracking and follow-up recommendations

    Priority: 1 (CRITICAL) - Converts conversations into relationships.
    """

    def __init__(self):
        """Initialize Follow-Up Agent."""
        system_prompt = """You are the Follow-Up Agent, an expert at building and maintaining professional relationships.

Your primary responsibilities:
1. Analyze conversations to categorize leads (hot/warm/cold)
2. Generate personalized, authentic follow-up messages
3. Adapt tone and style based on context and relationship stage
4. Create LinkedIn connection requests (300 char limit)
5. Draft professional emails with clear calls-to-action
6. Suggest optimal timing for outreach
7. Recommend next steps based on responses

Message generation principles:
- Personalize by referencing specific conversation details
- Be authentic and avoid generic templates
- Include clear value proposition
- Have a specific call-to-action
- Match the recipient's communication style
- Keep LinkedIn messages under 300 characters
- Use professional but personable tone

Lead categorization criteria:
- HOT: Strong mutual interest, immediate next steps, time-sensitive opportunity
- WARM: Positive interaction, potential fit, follow-up needed
- COLD: Initial contact, exploratory, long-term relationship building

When generating messages:
1. Reference specific topics or action items from conversation
2. Provide value (resources, introductions, insights)
3. Make the next step clear and easy
4. Respect their time and preferences
5. Be genuine and conversational

Always aim to strengthen relationships authentically."""

        super().__init__(
            name="follow_up",
            description="Generates personalized follow-up messages and manages outreach",
            system_prompt=system_prompt,
            priority=1  # Critical priority
        )

        # Statistics
        self.total_messages_generated = 0
        self.total_leads_categorized = 0
        self.hot_leads = 0
        self.warm_leads = 0
        self.cold_leads = 0

        logger.info("Follow-Up Agent initialized")

    async def categorize_lead(
        self,
        participant_id: str,
        conversation_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Categorize a lead as hot/warm/cold.

        Args:
            participant_id: ID of the participant
            conversation_text: Conversation transcript
            context: Optional context (action items, sentiment, etc.)

        Returns:
            Lead categorization with score and reasoning
        """
        logger.info(f"Categorizing lead: {participant_id}")

        # Use Claude to analyze the lead
        prompt = f"""Analyze this conversation to categorize the lead.

Conversation excerpt (last 1000 chars):
{conversation_text[-1000:]}

Context:
{context if context else 'No additional context'}

Categorize this lead as:
- HOT: Strong interest, immediate action items, time-sensitive, high engagement
- WARM: Positive interaction, some interest, potential fit, follow-up recommended
- COLD: Initial contact, exploratory, no immediate action

Respond in JSON:
{{
    "category": "hot|warm|cold",
    "score": 0-100,
    "reasoning": "why this categorization",
    "engagement_level": "high|medium|low",
    "time_sensitivity": "urgent|soon|flexible",
    "recommended_action": "specific next step"
}}"""

        try:
            result = await self.execute(
                prompt=prompt,
                context=context,
                max_tokens=500,
                temperature=0.3
            )

            # Parse response
            import json
            try:
                categorization = json.loads(result['response'])
            except:
                # Default categorization
                categorization = {
                    'category': 'warm',
                    'score': 50,
                    'reasoning': 'Default categorization',
                    'engagement_level': 'medium',
                    'time_sensitivity': 'flexible',
                    'recommended_action': 'Send follow-up email'
                }

            # Update statistics
            self.total_leads_categorized += 1
            if categorization['category'] == 'hot':
                self.hot_leads += 1
            elif categorization['category'] == 'warm':
                self.warm_leads += 1
            else:
                self.cold_leads += 1

            # Store in database
            await self._update_participant_lead_status(
                participant_id,
                categorization['category'],
                categorization['score']
            )

            logger.info(
                f"Lead categorized: {categorization['category'].upper()} "
                f"(score: {categorization['score']})"
            )

            return categorization

        except Exception as e:
            logger.error(f"Error categorizing lead: {e}")
            return {
                'category': 'warm',
                'score': 50,
                'reasoning': f'Error: {str(e)}',
                'engagement_level': 'medium',
                'time_sensitivity': 'flexible',
                'recommended_action': 'Manual review needed'
            }

    async def generate_follow_up_messages(
        self,
        participant_id: str,
        conversation_text: str,
        message_types: List[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate multiple follow-up message variants.

        Args:
            participant_id: ID of the participant
            conversation_text: Conversation transcript
            message_types: Types to generate ['linkedin', 'email', 'casual']
            context: Optional context

        Returns:
            Generated messages with variants
        """
        logger.info(f"Generating follow-up messages for participant {participant_id}")

        if message_types is None:
            message_types = ['linkedin', 'email']

        messages = {}

        # Get participant details
        participant = await self._get_participant(participant_id)
        if not participant:
            logger.error(f"Participant {participant_id} not found")
            return {}

        # Generate each message type
        for msg_type in message_types:
            if msg_type == 'linkedin':
                messages['linkedin'] = await self._generate_linkedin_message(
                    participant, conversation_text, context
                )
            elif msg_type == 'email':
                messages['email'] = await self._generate_email_message(
                    participant, conversation_text, context
                )
            elif msg_type == 'casual':
                messages['casual'] = await self._generate_casual_message(
                    participant, conversation_text, context
                )

        # Store in database
        for msg_type, message_data in messages.items():
            await self._store_follow_up_message(
                participant_id,
                msg_type,
                message_data
            )

        self.total_messages_generated += len(messages)

        return {
            'participant_id': participant_id,
            'participant_name': participant.name if participant else 'Unknown',
            'messages': messages,
            'generated_at': datetime.utcnow().isoformat()
        }

    async def _generate_linkedin_message(
        self,
        participant: Any,
        conversation_text: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate LinkedIn connection request message (300 char limit)."""

        prompt = f"""Generate a LinkedIn connection request message for {participant.name or 'this person'}.

Conversation context (last 500 chars):
{conversation_text[-500:]}

Additional context: {context if context else 'None'}

Requirements:
- Maximum 300 characters (strict limit)
- Reference something specific from our conversation
- Friendly and professional tone
- Clear why you want to connect

Generate 3 variants: formal, balanced, casual

Respond in JSON:
{{
    "formal": "message text",
    "balanced": "message text",
    "casual": "message text",
    "recommended": "formal|balanced|casual"
}}"""

        try:
            result = await self.execute(
                prompt=prompt,
                max_tokens=400,
                temperature=0.7
            )

            import json
            messages = json.loads(result['response'])

            # Ensure length limit
            for variant in ['formal', 'balanced', 'casual']:
                if variant in messages and len(messages[variant]) > 300:
                    messages[variant] = messages[variant][:297] + '...'

            return messages

        except Exception as e:
            logger.error(f"Error generating LinkedIn message: {e}")
            return {
                'formal': f"Hi {participant.name}, great meeting you! Let's connect.",
                'balanced': f"Hi {participant.name}, enjoyed our conversation. Would love to stay in touch!",
                'casual': f"Hey {participant.name}, cool chatting with you! Let's connect!",
                'recommended': 'balanced'
            }

    async def _generate_email_message(
        self,
        participant: Any,
        conversation_text: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate professional email follow-up."""

        # Extract action items if available
        action_items_text = ""
        if context and 'action_items' in context:
            action_items_text = "\n".join([
                f"- {item.get('description', '')}"
                for item in context['action_items'][:3]
            ])

        prompt = f"""Generate a follow-up email for {participant.name or 'this person'} at {participant.company or 'their company'}.

Conversation highlights:
{conversation_text[-1000:]}

Action items we discussed:
{action_items_text if action_items_text else 'No specific action items'}

Generate a professional email with:
- Engaging subject line
- Personalized greeting
- Reference to our conversation
- Clear next steps or call-to-action
- Professional closing

Respond in JSON:
{{
    "subject": "subject line",
    "body": "email body with \\n\\n for paragraphs",
    "tone": "professional|friendly|enthusiastic"
}}"""

        try:
            result = await self.execute(
                prompt=prompt,
                max_tokens=600,
                temperature=0.7
            )

            import json
            email_data = json.loads(result['response'])

            return email_data

        except Exception as e:
            logger.error(f"Error generating email: {e}")
            return {
                'subject': f"Great meeting you, {participant.name}!",
                'body': f"Hi {participant.name},\n\nIt was great meeting you today. Looking forward to staying in touch!\n\nBest regards",
                'tone': 'professional'
            }

    async def _generate_casual_message(
        self,
        participant: Any,
        conversation_text: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate casual follow-up message (text/chat style)."""

        prompt = f"""Generate a casual follow-up message for {participant.name or 'this person'}.

Conversation context:
{conversation_text[-500:]}

Generate a short, friendly message (2-3 sentences) that:
- Feels natural and conversational
- References our conversation
- Suggests staying in touch

Respond with just the message text."""

        try:
            result = await self.execute(
                prompt=prompt,
                max_tokens=200,
                temperature=0.8
            )

            return {
                'message': result['response'].strip(),
                'style': 'casual'
            }

        except Exception as e:
            logger.error(f"Error generating casual message: {e}")
            return {
                'message': f"Hey {participant.name}! Great talking with you. Let's keep in touch!",
                'style': 'casual'
            }

    async def suggest_optimal_timing(
        self,
        participant_id: str,
        message_type: str = 'email'
    ) -> Dict[str, Any]:
        """
        Suggest optimal time to send follow-up.

        Args:
            participant_id: ID of participant
            message_type: Type of message

        Returns:
            Timing recommendation
        """
        # Basic heuristics (can be enhanced with ML)
        now = datetime.utcnow()

        # Best times by message type
        if message_type == 'linkedin':
            # LinkedIn: weekday mornings
            recommended_time = now + timedelta(days=1)
            recommended_time = recommended_time.replace(hour=9, minute=0)

        elif message_type == 'email':
            # Email: Tuesday-Thursday, 10am-2pm
            recommended_time = now + timedelta(days=1)
            while recommended_time.weekday() > 3:  # Skip Fri/Sat/Sun
                recommended_time += timedelta(days=1)
            recommended_time = recommended_time.replace(hour=10, minute=0)

        else:
            # Default: next business day morning
            recommended_time = now + timedelta(days=1)
            recommended_time = recommended_time.replace(hour=9, minute=0)

        return {
            'recommended_time': recommended_time.isoformat(),
            'urgency': 'normal',
            'reasoning': f'Optimal time for {message_type} based on engagement patterns',
            'send_within': '24-48 hours'
        }

    async def _get_participant(self, participant_id: str) -> Optional[Any]:
        """Get participant from database."""
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(Participant).where(Participant.id == participant_id)
                )
                return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting participant: {e}")
            return None

    async def _update_participant_lead_status(
        self,
        participant_id: str,
        category: str,
        score: float
    ) -> None:
        """Update participant's lead status in database."""
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(Participant).where(Participant.id == participant_id)
                )
                participant = result.scalar_one_or_none()

                if participant:
                    participant.lead_priority = category
                    participant.lead_score = score
                    await session.commit()

        except Exception as e:
            logger.error(f"Error updating lead status: {e}")

    async def _store_follow_up_message(
        self,
        participant_id: str,
        message_type: str,
        message_data: Dict[str, Any]
    ) -> None:
        """Store generated follow-up message in database."""
        try:
            async with AsyncSessionLocal() as session:
                follow_up = FollowUpMessage(
                    participant_id=participant_id,
                    message_type=message_type,
                    content=str(message_data),  # Store as JSON string
                    status='draft',
                    generated_at=datetime.utcnow()
                )
                session.add(follow_up)
                await session.commit()

        except Exception as e:
            logger.error(f"Error storing follow-up message: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get Follow-Up agent statistics."""
        base_stats = super().get_stats()
        base_stats.update({
            'total_messages_generated': self.total_messages_generated,
            'total_leads_categorized': self.total_leads_categorized,
            'hot_leads': self.hot_leads,
            'warm_leads': self.warm_leads,
            'cold_leads': self.cold_leads
        })
        return base_stats
