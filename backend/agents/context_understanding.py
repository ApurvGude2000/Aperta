"""
AG4: Context Understanding Agent - Extracts and understands conversation context.
Priority: 1 (CRITICAL) - Core intelligence for semantic understanding.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy import select
from .base import ClaudeBaseAgent
from tools.entity_extractor import EntityExtractor
from tools.intent_recognizer import IntentRecognizer
from utils.logger import setup_logger
from db.session import AsyncSessionLocal
from db.models import Entity as EntityModel, ActionItem, Conversation

logger = setup_logger(__name__)


class ContextUnderstandingAgent(ClaudeBaseAgent):
    """
    Context Understanding Agent - AG4

    Responsibilities:
    1. Entity extraction (people, companies, topics, technologies)
    2. Entity resolution and disambiguation
    3. Intent recognition
    4. Action item extraction
    5. Conversation context tracking
    6. Clarification request generation

    Priority: 1 (CRITICAL) - Provides core semantic understanding.
    """

    def __init__(self):
        """Initialize Context Understanding Agent."""
        system_prompt = """You are the Context Understanding Agent, responsible for deep semantic analysis of conversations.

Your primary responsibilities:
1. Extract and structure information from conversations (entities, topics, commitments)
2. Understand the user's networking goals and intentions
3. Identify action items with responsible parties and deadlines
4. Resolve ambiguities and disambiguate entity references
5. Track conversation flow and context
6. Generate clarifying questions when information is incomplete

Entity types to extract:
- People: Full names, titles, roles
- Companies: Organization names
- Topics: Discussion subjects and themes
- Technologies: Tools, platforms, programming languages
- Action Items: Commitments, promises, follow-ups
- Dates: Deadlines and time references

When analyzing conversations:
1. Extract ALL relevant entities with confidence scores
2. Identify relationships between entities
3. Recognize the primary intent and secondary intents
4. Find action items with WHO, WHAT, WHEN details
5. Note any ambiguities that need clarification
6. Provide structured JSON output

Be thorough but accurate - only extract entities you're confident about."""

        super().__init__(
            name="context_understanding",
            description="Extracts entities, intent, and action items from conversations",
            system_prompt=system_prompt,
            priority=1  # Critical priority
        )

        # Initialize analysis tools
        self.entity_extractor = EntityExtractor()
        self.intent_recognizer = IntentRecognizer()

        # Statistics
        self.total_entities_extracted = 0
        self.total_action_items_found = 0
        self.total_clarifications_requested = 0

        logger.info("Context Understanding Agent initialized")

    async def analyze_conversation(
        self,
        text: str,
        conversation_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive conversation analysis.

        Args:
            text: Conversation text to analyze
            conversation_id: ID of the conversation
            context: Optional additional context

        Returns:
            Analysis results with entities, intent, and action items
        """
        logger.info(f"Analyzing conversation {conversation_id} ({len(text)} chars)")

        # Step 1: Extract entities using pattern-based extraction
        entities = self.entity_extractor.extract_all(text, context)
        self.total_entities_extracted += len(entities)

        # Step 2: Recognize intent
        intents = self.intent_recognizer.recognize(text, context)

        # Step 3: Use Claude for deeper semantic analysis
        claude_analysis = await self._analyze_with_claude(
            text, entities, intents, context
        )

        # Step 4: Merge and resolve entities
        all_entities = self._merge_entities(entities, claude_analysis.get('entities', []))
        resolved_entities = self.entity_extractor.resolve_entities(all_entities)

        # Step 5: Extract action items
        action_items = await self._extract_action_items(
            text, claude_analysis, conversation_id
        )
        self.total_action_items_found += len(action_items)

        # Step 6: Generate clarifications if needed
        clarifications = self._generate_clarifications(
            all_entities, action_items, claude_analysis
        )
        if clarifications:
            self.total_clarifications_requested += len(clarifications)

        # Step 7: Store in database
        await self._store_entities(conversation_id, all_entities)
        await self._store_action_items(conversation_id, action_items)

        result = {
            'conversation_id': conversation_id,
            'entities': {
                'total': len(all_entities),
                'by_type': self.entity_extractor.get_statistics(all_entities)['by_type'],
                'resolved': {k: len(v) for k, v in resolved_entities.items()},
                'details': self.entity_extractor.to_json(all_entities)
            },
            'intent': {
                'primary': intents[0].intent_type.value if intents else 'unknown',
                'confidence': intents[0].confidence if intents else 0.0,
                'all_intents': self.intent_recognizer.to_json(intents)
            },
            'action_items': action_items,
            'clarifications': clarifications,
            'context_summary': claude_analysis.get('summary', ''),
            'key_topics': claude_analysis.get('topics', []),
            'timestamp': datetime.utcnow().isoformat()
        }

        logger.info(
            f"Analysis complete: {len(all_entities)} entities, "
            f"{len(action_items)} action items"
        )

        return result

    async def extract_entities_only(
        self,
        text: str,
        entity_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Extract only entities without full analysis.

        Args:
            text: Text to analyze
            entity_types: Specific entity types to extract (None = all)

        Returns:
            Extracted entities
        """
        entities = self.entity_extractor.extract_all(text)

        # Filter by type if specified
        if entity_types:
            entities = [e for e in entities if e.entity_type in entity_types]

        return {
            'entities': self.entity_extractor.to_json(entities),
            'statistics': self.entity_extractor.get_statistics(entities)
        }

    async def recognize_intent_only(
        self,
        text: str
    ) -> Dict[str, Any]:
        """
        Recognize intent without full analysis.

        Args:
            text: Text to analyze

        Returns:
            Recognized intents
        """
        return self.intent_recognizer.get_intent_summary(text)

    async def _analyze_with_claude(
        self,
        text: str,
        entities: List,
        intents: List,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Use Claude for semantic analysis and validation."""

        # Build analysis prompt
        prompt = f"""Analyze this conversation for context and meaning.

Conversation text (first 2000 chars):
{text[:2000]}

Already detected:
- {len(entities)} entities
- Primary intent: {intents[0].intent_type.value if intents else 'unknown'}

Please provide:
1. Key topics discussed (3-5 main topics)
2. Any additional entities missed by pattern matching
3. A brief summary (2-3 sentences) of the conversation
4. Relationships between people/companies mentioned
5. Any ambiguities that need clarification

Respond in JSON format:
{{
    "topics": ["topic1", "topic2", "topic3"],
    "entities": [
        {{"type": "person", "value": "Name", "confidence": 0.9}},
        {{"type": "company", "value": "Company", "confidence": 0.85}}
    ],
    "summary": "Brief summary of the conversation",
    "relationships": [
        {{"person": "Name", "company": "Company", "role": "Engineer"}}
    ],
    "ambiguities": ["What exactly is...", "When should..."]
}}"""

        try:
            # Execute with Claude
            result = await self.execute(
                prompt=prompt,
                context=context,
                max_tokens=2000,
                temperature=0.3  # Lower temperature for factual extraction
            )

            # Parse JSON response
            import json
            try:
                analysis = json.loads(result['response'])
            except:
                # If JSON parsing fails, extract key info
                analysis = {
                    'topics': [],
                    'entities': [],
                    'summary': result['response'][:200],
                    'relationships': [],
                    'ambiguities': []
                }

            return analysis

        except Exception as e:
            logger.error(f"Error in Claude context analysis: {e}")
            return {
                'topics': [],
                'entities': [],
                'summary': '',
                'relationships': [],
                'ambiguities': []
            }

    def _merge_entities(
        self,
        pattern_entities: List,
        claude_entities: List[Dict[str, Any]]
    ) -> List:
        """Merge entities from pattern matching and Claude analysis."""
        # Start with pattern entities
        merged = list(pattern_entities)

        # Add Claude entities that aren't duplicates
        for claude_entity in claude_entities:
            # Check if already exists
            is_duplicate = False
            for existing in merged:
                if (existing.entity_type == claude_entity.get('type') and
                    existing.entity_value.lower() == claude_entity.get('value', '').lower()):
                    is_duplicate = True
                    break

            if not is_duplicate:
                # Convert Claude entity to Entity object
                from tools.entity_extractor import Entity
                merged.append(Entity(
                    entity_type=claude_entity.get('type', 'unknown'),
                    entity_value=claude_entity.get('value', ''),
                    confidence=claude_entity.get('confidence', 0.7),
                    context='Extracted by Claude AI',
                    metadata={'source': 'claude'},
                    start_pos=0,
                    end_pos=0
                ))

        return merged

    async def _extract_action_items(
        self,
        text: str,
        claude_analysis: Dict[str, Any],
        conversation_id: str
    ) -> List[Dict[str, Any]]:
        """Extract action items with details."""
        action_items = []

        # Get action items from entity extractor
        entities = self.entity_extractor.extract_all(text)
        action_entities = [e for e in entities if e.entity_type == 'action_item']

        # Also check for action items in Claude analysis
        claude_actions = claude_analysis.get('action_items', [])

        # Process action items
        for action in action_entities:
            action_items.append({
                'description': action.entity_value,
                'responsible_party': None,  # TODO: Extract from context
                'due_date': None,  # TODO: Extract from surrounding text
                'confidence': action.confidence,
                'source': 'pattern_extraction'
            })

        return action_items

    async def _store_entities(
        self,
        conversation_id: str,
        entities: List
    ) -> None:
        """Store extracted entities in database."""
        try:
            async with AsyncSessionLocal() as session:
                for entity in entities:
                    db_entity = EntityModel(
                        conversation_id=conversation_id,
                        entity_type=entity.entity_type,
                        entity_value=entity.entity_value,
                        confidence=entity.confidence,
                        context=entity.context,
                        extra_data=entity.metadata
                    )
                    session.add(db_entity)

                await session.commit()
                logger.debug(f"Stored {len(entities)} entities for conversation {conversation_id}")

        except Exception as e:
            logger.error(f"Failed to store entities: {e}")

    async def _store_action_items(
        self,
        conversation_id: str,
        action_items: List[Dict[str, Any]]
    ) -> None:
        """Store action items in database."""
        try:
            async with AsyncSessionLocal() as session:
                for item in action_items:
                    db_action = ActionItem(
                        conversation_id=conversation_id,
                        description=item['description'],
                        responsible_party=item.get('responsible_party'),
                        due_date=item.get('due_date'),
                        completed=False
                    )
                    session.add(db_action)

                await session.commit()
                logger.debug(f"Stored {len(action_items)} action items")

        except Exception as e:
            logger.error(f"Failed to store action items: {e}")

    def _generate_clarifications(
        self,
        entities: List,
        action_items: List[Dict[str, Any]],
        claude_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate clarification questions for ambiguous information."""
        clarifications = []

        # Check for action items without deadlines
        incomplete_actions = [a for a in action_items if not a.get('due_date')]
        if incomplete_actions:
            clarifications.append(
                f"When should these {len(incomplete_actions)} action item(s) be completed?"
            )

        # Check for people without company affiliation
        people = [e for e in entities if e.entity_type == 'person']
        companies = [e for e in entities if e.entity_type == 'company']
        if people and not companies:
            clarifications.append(
                "Which companies or organizations are these people affiliated with?"
            )

        # Add Claude's ambiguities
        clarifications.extend(claude_analysis.get('ambiguities', []))

        return clarifications[:5]  # Limit to 5 clarifications

    def get_stats(self) -> Dict[str, Any]:
        """Get Context Understanding agent statistics."""
        base_stats = super().get_stats()
        base_stats.update({
            'total_entities_extracted': self.total_entities_extracted,
            'total_action_items_found': self.total_action_items_found,
            'total_clarifications_requested': self.total_clarifications_requested
        })
        return base_stats
