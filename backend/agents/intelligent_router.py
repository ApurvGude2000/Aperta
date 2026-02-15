# ABOUTME: Intelligent router that uses Claude to analyze question intent and route to appropriate agents.
# ABOUTME: Provides intent classification with confidence scoring and agent recommendations.
from typing import Dict, List, Any, Optional, Tuple
from anthropic import AsyncAnthropic
from datetime import datetime
import json
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class IntelligentRouter:
    """
    Routes user queries to appropriate agents based on intent analysis.
    Uses Claude to understand the query intent and recommend agents.
    """

    # Intent to agent mapping
    INTENT_AGENT_MAP = {
        "privacy_check": ["privacy_guardian"],
        "entity_extraction": ["context_understanding"],
        "lead_scoring": ["follow_up"],
        "goal_alignment": ["strategic_networking"],
        "system_monitoring": ["perception"],
        "general_query": ["context_understanding", "strategic_networking"],
    }

    # Intent descriptions for Claude
    INTENT_DESCRIPTIONS = {
        "privacy_check": "Checking for sensitive information, PII, or privacy concerns in data",
        "entity_extraction": "Extracting names, companies, topics, or other entities from text",
        "lead_scoring": "Scoring leads, prioritizing contacts, or generating follow-up actions",
        "goal_alignment": "Aligning networking goals, strategic planning, or relationship building",
        "system_monitoring": "Monitoring system health, performance metrics, or agent status",
        "general_query": "General questions about conversations, contacts, or networking insights"
    }

    def __init__(self, model: str = None):
        """
        Initialize intelligent router.

        Args:
            model: Claude model to use for routing (defaults to settings)
        """
        self.model = model or settings.default_agent_model
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.routing_history: List[Dict[str, Any]] = []

        logger.info(f"Intelligent Router initialized with model: {self.model}")

    async def route_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze query intent and recommend appropriate agents.

        Args:
            query: User query to route
            context: Optional context about the query
            verbose: Whether to print detailed routing information

        Returns:
            Dictionary containing:
                - intent: Primary intent category
                - confidence: Confidence score (0.0-1.0)
                - recommended_agents: List of agent names to use
                - reasoning: Explanation of the routing decision
                - all_intents: All detected intents with scores
        """
        if verbose:
            self._print_routing_header(query)

        start_time = datetime.utcnow()

        try:
            # Analyze intent using Claude
            intent_analysis = await self._analyze_intent(query, context)

            # Get agent recommendations
            routing_result = self._build_routing_result(intent_analysis)

            # Record routing
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self._record_routing(query, routing_result, execution_time)

            if verbose:
                self._print_routing_result(routing_result)

            return routing_result

        except Exception as e:
            logger.error(f"Routing failed: {e}")
            # Fallback to general query routing
            fallback = {
                "intent": "general_query",
                "confidence": 0.5,
                "recommended_agents": self.INTENT_AGENT_MAP["general_query"],
                "reasoning": f"Routing failed, using fallback: {str(e)}",
                "all_intents": {}
            }
            
            # Record fallback routing
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self._record_routing(query, fallback, execution_time)
            
            return fallback

    async def _analyze_intent(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Use Claude to analyze query intent.

        Args:
            query: User query
            context: Optional context

        Returns:
            Intent analysis dictionary
        """
        # Build system prompt
        system_prompt = self._build_intent_analysis_prompt()

        # Build user message
        user_message = f"Query: {query}"
        if context:
            user_message += f"\n\nContext: {json.dumps(context, indent=2)}"

        # Call Claude
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            temperature=0.3,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )

        # Parse response
        response_text = response.content[0].text
        
        try:
            # Try to parse as JSON
            intent_data = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback: extract intent from text
            logger.warning("Failed to parse JSON response, using text extraction")
            intent_data = self._extract_intent_from_text(response_text)

        return intent_data

    def _build_intent_analysis_prompt(self) -> str:
        """Build system prompt for intent analysis."""
        intent_list = "\n".join([
            f"- {intent}: {desc}"
            for intent, desc in self.INTENT_DESCRIPTIONS.items()
        ])

        return f"""You are an intelligent query router for a networking AI system.
Your task is to analyze user queries and determine their intent to route them to the appropriate agents.

Available intents:
{intent_list}

Analyze the query and return a JSON object with the following structure:
{{
    "primary_intent": "intent_name",
    "confidence": 0.95,
    "reasoning": "Brief explanation of why this intent was chosen",
    "all_intents": {{
        "intent_name": 0.95,
        "another_intent": 0.30
    }}
}}

Rules:
- Confidence should be between 0.0 and 1.0
- Include all intents with confidence > 0.2 in all_intents
- Primary intent should be the highest confidence intent
- Reasoning should be concise (1-2 sentences)
- If query involves multiple intents, include them in all_intents with appropriate confidence scores
"""

    def _extract_intent_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract intent information from text response.

        Args:
            text: Response text

        Returns:
            Intent data dictionary
        """
        # Simple fallback extraction
        text_lower = text.lower()
        
        intent_scores = {}
        for intent in self.INTENT_DESCRIPTIONS.keys():
            if intent.replace("_", " ") in text_lower:
                intent_scores[intent] = 0.7

        if not intent_scores:
            intent_scores["general_query"] = 0.5

        primary_intent = max(intent_scores.items(), key=lambda x: x[1])[0]

        return {
            "primary_intent": primary_intent,
            "confidence": intent_scores[primary_intent],
            "reasoning": "Extracted from text response",
            "all_intents": intent_scores
        }

    def _build_routing_result(self, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build final routing result from intent analysis.

        Args:
            intent_analysis: Intent analysis from Claude

        Returns:
            Routing result dictionary
        """
        primary_intent = intent_analysis.get("primary_intent", "general_query")
        confidence = intent_analysis.get("confidence", 0.5)
        reasoning = intent_analysis.get("reasoning", "No reasoning provided")
        all_intents = intent_analysis.get("all_intents", {primary_intent: confidence})

        # Get recommended agents
        recommended_agents = self.INTENT_AGENT_MAP.get(primary_intent, 
                                                       self.INTENT_AGENT_MAP["general_query"])

        # If multiple intents with high confidence, add their agents too
        for intent, score in all_intents.items():
            if intent != primary_intent and score > 0.6:
                additional_agents = self.INTENT_AGENT_MAP.get(intent, [])
                for agent in additional_agents:
                    if agent not in recommended_agents:
                        recommended_agents.append(agent)

        return {
            "intent": primary_intent,
            "confidence": confidence,
            "recommended_agents": recommended_agents,
            "reasoning": reasoning,
            "all_intents": all_intents
        }

    def _record_routing(
        self,
        query: str,
        routing_result: Dict[str, Any],
        execution_time: float
    ):
        """Record routing decision in history."""
        record = {
            "query": query[:100],  # Truncate long queries
            "intent": routing_result["intent"],
            "confidence": routing_result["confidence"],
            "agents": routing_result["recommended_agents"],
            "execution_time": execution_time,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.routing_history.append(record)

        # Keep only last 1000 routings
        if len(self.routing_history) > 1000:
            self.routing_history = self.routing_history[-1000:]

    def _print_routing_header(self, query: str):
        """Print routing analysis header."""
        print("\n" + "="*80)
        print("INTELLIGENT ROUTER - QUERY ANALYSIS")
        print("="*80)
        print(f"Query: {query}")
        print("-"*80)

    def _print_routing_result(self, result: Dict[str, Any]):
        """Print routing result with decision tree."""
        print("\nROUTING DECISION:")
        print(f"  Primary Intent: {result['intent']}")
        print(f"  Confidence: {result['confidence']:.2%}")
        print(f"\nRecommended Agents:")
        for agent in result['recommended_agents']:
            print(f"  - {agent}")
        
        print(f"\nReasoning:")
        print(f"  {result['reasoning']}")
        
        if result['all_intents']:
            print(f"\nAll Detected Intents:")
            sorted_intents = sorted(
                result['all_intents'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            for intent, score in sorted_intents:
                bar_length = int(score * 40)
                bar = "█" * bar_length + "░" * (40 - bar_length)
                print(f"  {intent:20s} {bar} {score:.2%}")
        
        print("="*80 + "\n")

    def get_routing_history(
        self,
        intent: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get routing history.

        Args:
            intent: Optional filter by intent
            limit: Maximum number of records

        Returns:
            List of routing records
        """
        history = self.routing_history

        if intent:
            history = [h for h in history if h["intent"] == intent]

        return history[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """Get router statistics."""
        if not self.routing_history:
            return {
                "total_routings": 0,
                "avg_execution_time": 0.0,
                "avg_confidence": 0.0,
                "intent_distribution": {},
                "available_intents": list(self.INTENT_DESCRIPTIONS.keys())
            }

        intent_counts = {}
        for record in self.routing_history:
            intent = record["intent"]
            intent_counts[intent] = intent_counts.get(intent, 0) + 1

        avg_time = sum(r["execution_time"] for r in self.routing_history) / len(self.routing_history)
        avg_confidence = sum(r["confidence"] for r in self.routing_history) / len(self.routing_history)

        return {
            "total_routings": len(self.routing_history),
            "avg_execution_time": round(avg_time, 3),
            "avg_confidence": round(avg_confidence, 3),
            "intent_distribution": intent_counts,
            "available_intents": list(self.INTENT_DESCRIPTIONS.keys())
        }


# Global router instance
router = IntelligentRouter()
