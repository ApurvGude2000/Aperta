"""
AG5: Strategic Networking Agent - Aligns conversations with user goals and detects opportunities.
Priority: 3 - Provides strategic guidance during networking.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy import select
from .base import ClaudeBaseAgent
from utils.logger import setup_logger
from db.session import AsyncSessionLocal
from db.models import UserGoal, Opportunity, Conversation, Participant

logger = setup_logger(__name__)


class StrategicNetworkingAgent(ClaudeBaseAgent):
    """
    Strategic Networking Agent - AG5

    Responsibilities:
    1. Parse and track user's networking goals
    2. Real-time conversation analysis against goals
    3. Opportunity detection (buying signals, collaboration, referrals)
    4. Lead priority scoring based on goal alignment
    5. Topic suggestions for conversation
    6. Conversation gap analysis
    7. Strategic value assessment

    Priority: 3 - Strategic guidance for effective networking.
    """

    def __init__(self):
        """Initialize Strategic Networking Agent."""
        system_prompt = """You are the Strategic Networking Agent, an expert at helping people achieve their networking goals.

Your primary responsibilities:
1. Understand the user's networking objectives and priorities
2. Analyze conversations in real-time to identify strategic opportunities
3. Detect signals of interest, collaboration potential, and mutual benefit
4. Score contacts based on alignment with user's goals
5. Suggest relevant topics to discuss
6. Identify gaps in the conversation that should be explored
7. Assess long-term strategic value of relationships

Networking goal types to recognize:
- Job seeking: Looking for employment opportunities
- Fundraising: Seeking investors or capital
- Partnership: Finding business collaborators
- Learning: Gaining knowledge or skills
- Hiring: Recruiting talent
- Sales: Finding customers or clients
- Mentorship: Seeking guidance or offering mentorship
- Career growth: Advancing professional development

Opportunity signals to detect:
- Buying signals: "We're looking for...", "We need...", "Our team struggles with..."
- Collaboration openness: "Let's work together", "We could partner on...", "Interested in..."
- Referral potential: "I know someone who...", "You should meet...", "Let me introduce..."
- Immediate needs: Urgent requirements, time-sensitive opportunities
- Budget authority: Decision-making power, budget mentions
- Warm introduction: "I'll connect you with...", "Here's my colleague's contact..."

When analyzing conversations:
1. Identify how the conversation relates to user's stated goals
2. Score the strategic value (0-100) based on goal alignment
3. Detect opportunity signals and categorize them
4. Suggest topics that advance the user's objectives
5. Note conversation gaps (important topics not yet discussed)
6. Assess the long-term relationship potential

Be proactive but not pushy - genuine relationships matter most."""

        super().__init__(
            name="strategic_networking",
            description="Aligns conversations with goals and detects opportunities",
            system_prompt=system_prompt,
            priority=3  # Strategic priority
        )

        # Statistics
        self.total_goals_tracked = 0
        self.total_opportunities_detected = 0
        self.total_suggestions_made = 0
        self.total_value_assessments = 0

        logger.info("Strategic Networking Agent initialized")

    async def parse_networking_goals(
        self,
        user_id: str,
        goal_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Parse user's networking goals from text.

        Args:
            user_id: User ID
            goal_text: Description of networking goals
            context: Optional context

        Returns:
            Parsed goals with priorities
        """
        logger.info(f"Parsing networking goals for user {user_id}")

        prompt = f"""Parse these networking goals and structure them for tracking.

User's goals:
{goal_text}

Analyze and extract:
1. Primary goal (main objective)
2. Secondary goals (supporting objectives)
3. Success criteria (how to measure progress)
4. Timeline/urgency
5. Specific preferences or requirements

Respond in JSON:
{{
    "primary_goal": {{
        "type": "job_seeking|fundraising|partnership|learning|hiring|sales|mentorship|career_growth",
        "description": "specific description",
        "priority": "high|medium|low"
    }},
    "secondary_goals": [
        {{"type": "...", "description": "...", "priority": "..."}}
    ],
    "success_criteria": ["criterion1", "criterion2"],
    "timeline": "immediate|1-3 months|3-6 months|long-term",
    "preferences": ["preference1", "preference2"]
}}"""

        try:
            result = await self.execute(
                prompt=prompt,
                context=context,
                max_tokens=1000,
                temperature=0.3
            )

            import json
            goals = json.loads(result['response'])

            # Store goals in database
            await self._store_user_goals(user_id, goals)

            self.total_goals_tracked += 1 + len(goals.get('secondary_goals', []))

            logger.info(f"Parsed {self.total_goals_tracked} goals for user {user_id}")

            return goals

        except Exception as e:
            logger.error(f"Error parsing goals: {e}")
            return {
                'primary_goal': {
                    'type': 'general_networking',
                    'description': goal_text[:200],
                    'priority': 'medium'
                },
                'secondary_goals': [],
                'success_criteria': [],
                'timeline': 'flexible',
                'preferences': []
            }

    async def analyze_conversation_alignment(
        self,
        conversation_id: str,
        conversation_text: str,
        user_goals: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze how well conversation aligns with user's goals.

        Args:
            conversation_id: Conversation ID
            conversation_text: Conversation transcript
            user_goals: User's networking goals
            context: Optional context

        Returns:
            Alignment analysis with score and recommendations
        """
        logger.info(f"Analyzing goal alignment for conversation {conversation_id}")

        primary_goal = user_goals.get('primary_goal', {})

        prompt = f"""Analyze this conversation against the user's networking goals.

User's primary goal:
Type: {primary_goal.get('type', 'unknown')}
Description: {primary_goal.get('description', 'Not specified')}

Conversation excerpt (last 1500 chars):
{conversation_text[-1500:]}

Analyze:
1. Goal alignment score (0-100): How well does this conversation advance the user's goal?
2. Relevance: Which aspects of the conversation are relevant to the goal?
3. Action potential: What specific actions could advance the goal?
4. Relationship value: Strategic value of this connection for the goal?

Respond in JSON:
{{
    "alignment_score": 0-100,
    "relevance": "brief explanation",
    "relevant_aspects": ["aspect1", "aspect2"],
    "action_potential": "high|medium|low",
    "suggested_actions": ["action1", "action2"],
    "relationship_value": "strategic|tactical|exploratory",
    "reasoning": "why this score"
}}"""

        try:
            result = await self.execute(
                prompt=prompt,
                context=context,
                max_tokens=800,
                temperature=0.3
            )

            import json
            analysis = json.loads(result['response'])

            logger.info(
                f"Alignment score: {analysis.get('alignment_score', 0)}/100"
            )

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing alignment: {e}")
            return {
                'alignment_score': 50,
                'relevance': 'Unable to analyze',
                'relevant_aspects': [],
                'action_potential': 'medium',
                'suggested_actions': [],
                'relationship_value': 'exploratory',
                'reasoning': f'Error: {str(e)}'
            }

    async def detect_opportunities(
        self,
        conversation_id: str,
        conversation_text: str,
        user_goals: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Detect networking opportunities in conversation.

        Args:
            conversation_id: Conversation ID
            conversation_text: Conversation transcript
            user_goals: User's goals
            context: Optional context

        Returns:
            Detected opportunities with details
        """
        logger.info(f"Detecting opportunities in conversation {conversation_id}")

        prompt = f"""Detect networking opportunities in this conversation.

User's goal: {user_goals.get('primary_goal', {}).get('description', 'General networking')}

Conversation text (last 1500 chars):
{conversation_text[-1500:]}

Identify:
1. Buying signals (needs, pain points, budget mentions)
2. Collaboration opportunities (partnership, joint projects)
3. Referral potential (introductions, connections)
4. Immediate opportunities (urgent needs, time-sensitive)
5. Long-term potential (strategic relationships)

For each opportunity detected, provide:
- Type (buying_signal|collaboration|referral|immediate|strategic)
- Description
- Confidence (0-100)
- Evidence (specific quote or context)

Respond in JSON:
{{
    "opportunities": [
        {{
            "type": "buying_signal",
            "description": "...",
            "confidence": 85,
            "evidence": "specific quote",
            "urgency": "high|medium|low"
        }}
    ],
    "total_score": 0-100
}}"""

        try:
            result = await self.execute(
                prompt=prompt,
                context=context,
                max_tokens=1000,
                temperature=0.4
            )

            import json
            opportunities = json.loads(result['response'])

            detected_count = len(opportunities.get('opportunities', []))
            self.total_opportunities_detected += detected_count

            # Store opportunities in database
            await self._store_opportunities(
                conversation_id,
                opportunities.get('opportunities', [])
            )

            logger.info(f"Detected {detected_count} opportunities")

            return opportunities

        except Exception as e:
            logger.error(f"Error detecting opportunities: {e}")
            return {
                'opportunities': [],
                'total_score': 0
            }

    async def suggest_topics(
        self,
        conversation_text: str,
        user_goals: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Suggest relevant topics to bring up in conversation.

        Args:
            conversation_text: Current conversation
            user_goals: User's goals
            context: Optional context

        Returns:
            List of suggested topics
        """
        logger.info("Generating topic suggestions")

        prompt = f"""Suggest topics for the user to bring up in this conversation.

User's goal: {user_goals.get('primary_goal', {}).get('description', 'General networking')}

Conversation so far (last 1000 chars):
{conversation_text[-1000:]}

Suggest 3-5 topics that:
1. Advance the user's networking goal
2. Are natural given the conversation flow
3. Provide value to both parties
4. Open doors for future collaboration

Respond with JSON array:
{{
    "suggestions": [
        {{
            "topic": "topic name",
            "why": "brief reason",
            "transition": "how to introduce it naturally"
        }}
    ]
}}"""

        try:
            result = await self.execute(
                prompt=prompt,
                max_tokens=600,
                temperature=0.6
            )

            import json
            suggestions = json.loads(result['response'])
            topics = suggestions.get('suggestions', [])

            self.total_suggestions_made += len(topics)

            logger.info(f"Generated {len(topics)} topic suggestions")

            return topics

        except Exception as e:
            logger.error(f"Error suggesting topics: {e}")
            return []

    async def analyze_conversation_gaps(
        self,
        conversation_text: str,
        user_goals: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Identify important topics not yet discussed.

        Args:
            conversation_text: Conversation transcript
            user_goals: User's goals
            context: Optional context

        Returns:
            List of conversation gaps
        """
        logger.info("Analyzing conversation gaps")

        primary_goal = user_goals.get('primary_goal', {})

        prompt = f"""Identify important topics that haven't been discussed yet.

User's goal: {primary_goal.get('description', 'General networking')}
Goal type: {primary_goal.get('type', 'unknown')}

Conversation so far (last 1000 chars):
{conversation_text[-1000:]}

Based on the user's goal, what important topics are missing?
List 2-4 gaps that, if addressed, would make the conversation more valuable.

Respond with JSON array of gap descriptions:
{{
    "gaps": ["gap1", "gap2", "gap3"]
}}"""

        try:
            result = await self.execute(
                prompt=prompt,
                max_tokens=400,
                temperature=0.4
            )

            import json
            gaps_data = json.loads(result['response'])
            gaps = gaps_data.get('gaps', [])

            logger.info(f"Identified {len(gaps)} conversation gaps")

            return gaps

        except Exception as e:
            logger.error(f"Error analyzing gaps: {e}")
            return []

    async def assess_strategic_value(
        self,
        participant_id: str,
        conversation_text: str,
        user_goals: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Assess the strategic value of a contact.

        Args:
            participant_id: Participant ID
            conversation_text: Conversation transcript
            user_goals: User's goals
            context: Optional context

        Returns:
            Strategic value assessment
        """
        logger.info(f"Assessing strategic value of participant {participant_id}")

        self.total_value_assessments += 1

        prompt = f"""Assess the strategic value of this contact for the user's goals.

User's goal: {user_goals.get('primary_goal', {}).get('description', 'General networking')}

Conversation:
{conversation_text[-1500:]}

Assess:
1. Strategic value score (0-100)
2. Relationship potential (one-time|short-term|long-term)
3. Value drivers (what makes this contact valuable?)
4. Recommended approach (immediate|nurture|explore)

Respond in JSON:
{{
    "strategic_value": 0-100,
    "relationship_potential": "one-time|short-term|long-term",
    "value_drivers": ["driver1", "driver2"],
    "recommended_approach": "immediate|nurture|explore",
    "reasoning": "brief explanation"
}}"""

        try:
            result = await self.execute(
                prompt=prompt,
                max_tokens=500,
                temperature=0.3
            )

            import json
            assessment = json.loads(result['response'])

            logger.info(
                f"Strategic value: {assessment.get('strategic_value', 0)}/100"
            )

            return assessment

        except Exception as e:
            logger.error(f"Error assessing strategic value: {e}")
            return {
                'strategic_value': 50,
                'relationship_potential': 'exploratory',
                'value_drivers': [],
                'recommended_approach': 'explore',
                'reasoning': f'Error: {str(e)}'
            }

    async def _store_user_goals(
        self,
        user_id: str,
        goals: Dict[str, Any]
    ) -> None:
        """Store user goals in database."""
        try:
            async with AsyncSessionLocal() as session:
                # Store primary goal
                primary = goals.get('primary_goal', {})
                if primary:
                    goal = UserGoal(
                        user_id=user_id,
                        goal_type=primary.get('type', 'general_networking'),
                        description=primary.get('description', ''),
                        priority=1,
                        active=True
                    )
                    session.add(goal)

                # Store secondary goals
                for i, secondary in enumerate(goals.get('secondary_goals', [])):
                    goal = UserGoal(
                        user_id=user_id,
                        goal_type=secondary.get('type', 'general_networking'),
                        description=secondary.get('description', ''),
                        priority=i + 2,
                        active=True
                    )
                    session.add(goal)

                await session.commit()
                logger.debug(f"Stored goals for user {user_id}")

        except Exception as e:
            logger.error(f"Error storing goals: {e}")

    async def _store_opportunities(
        self,
        conversation_id: str,
        opportunities: List[Dict[str, Any]]
    ) -> None:
        """Store detected opportunities in database."""
        try:
            async with AsyncSessionLocal() as session:
                for opp in opportunities:
                    opportunity = Opportunity(
                        conversation_id=conversation_id,
                        opportunity_type=opp.get('type', 'unknown'),
                        description=opp.get('description', ''),
                        confidence=opp.get('confidence', 50) / 100.0,
                        status='detected',
                        detected_at=datetime.utcnow()
                    )
                    session.add(opportunity)

                await session.commit()
                logger.debug(f"Stored {len(opportunities)} opportunities")

        except Exception as e:
            logger.error(f"Error storing opportunities: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get Strategic Networking agent statistics."""
        base_stats = super().get_stats()
        base_stats.update({
            'total_goals_tracked': self.total_goals_tracked,
            'total_opportunities_detected': self.total_opportunities_detected,
            'total_suggestions_made': self.total_suggestions_made,
            'total_value_assessments': self.total_value_assessments
        })
        return base_stats
