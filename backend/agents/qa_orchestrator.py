"""
Q&A Orchestrator - Manages the question-answering pipeline with multiple agents.
Handles routing, parallel/sequential execution, and response composition.
"""
from typing import Dict, List, Any, Optional
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.logger import setup_logger

# Import agents
from .query_router import QueryRouterAgent
from .conversation_retrieval import ConversationRetrievalAgent
from .insight import InsightAgent
from .recommendation import RecommendationAgent
from .response_composer import ResponseComposerAgent

logger = setup_logger(__name__)


class QAOrchestrator:
    """
    Q&A Orchestrator - Coordinates multi-agent question-answering system.

    Flow:
    1. Query Router decides which agents to call
    2. Execute agents (parallel or sequential)
    3. Response Composer synthesizes results
    """

    def __init__(self):
        """Initialize Q&A Orchestrator."""
        logger.info("Initializing Q&A Orchestrator")

        # Initialize all agents
        self.agents = {
            "query_router": QueryRouterAgent(),
            "conversation_retrieval": ConversationRetrievalAgent(),
            "insight": InsightAgent(),
            "recommendation": RecommendationAgent(),
            "response_composer": ResponseComposerAgent()
        }

        logger.info(f"Q&A Orchestrator initialized with {len(self.agents)} agents")

    async def answer_question(self, user_question: str, user_id: str) -> Dict[str, Any]:
        """
        Main entry point for Q&A system.

        Args:
            user_question: User's natural language question
            user_id: User identifier for data access

        Returns:
            {
                "answer": "Final composed answer",
                "agent_trace": {...},  # For debugging
                "execution_time_ms": 1234
            }
        """
        start_time = time.time()

        try:
            logger.info(f"Processing question: {user_question}")

            # Step 1: Route query
            logger.info("Step 1: Routing query")
            routing = await self.agents["query_router"].route(user_question)
            logger.info(f"Routing decision: {routing}")

            # Step 2: Execute routed agents
            logger.info("Step 2: Executing routed agents")
            agent_results = {}

            if routing["execution_mode"] == "parallel":
                agent_results = await self._execute_parallel(
                    routing["agents_needed"],
                    user_question,
                    user_id
                )
            else:
                agent_results = await self._execute_sequential(
                    routing["agents_needed"],
                    user_question,
                    user_id
                )

            # Step 3: Compose final answer
            logger.info("Step 3: Composing final response")
            final_answer = await self.agents["response_composer"].compose(
                user_question=user_question,
                agent_outputs=agent_results
            )

            execution_time = (time.time() - start_time) * 1000

            result = {
                "answer": final_answer,
                "agent_trace": {
                    "routing": routing,
                    "agent_results": agent_results
                },
                "execution_time_ms": round(execution_time, 2)
            }

            logger.info(f"Question answered in {execution_time:.2f}ms")

            return result

        except Exception as e:
            logger.error(f"Orchestration failed: {e}", exc_info=True)
            execution_time = (time.time() - start_time) * 1000

            return {
                "answer": "I encountered an error processing your question. Please try rephrasing it.",
                "error": str(e),
                "execution_time_ms": round(execution_time, 2)
            }

    async def _execute_parallel(
        self,
        agent_names: List[str],
        question: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Execute multiple agents in parallel.

        Args:
            agent_names: List of agent names to execute
            question: User question
            user_id: User identifier

        Returns:
            Dict mapping agent names to their results
        """
        results = {}

        # Create tasks for all agents
        tasks = []
        for agent_name in agent_names:
            if agent_name in self.agents:
                task = self._execute_agent(agent_name, question, user_id)
                tasks.append((agent_name, task))

        # Execute all tasks in parallel
        all_tasks = [task for _, task in tasks]
        agent_names_list = [name for name, _ in tasks]

        try:
            completed_results = await asyncio.gather(*all_tasks, return_exceptions=True)

            # Collect results
            for agent_name, result in zip(agent_names_list, completed_results):
                if isinstance(result, Exception):
                    logger.error(f"Agent {agent_name} failed: {result}")
                    results[agent_name] = {"error": str(result)}
                else:
                    results[agent_name] = result

        except Exception as e:
            logger.error(f"Parallel execution failed: {e}")
            for agent_name in agent_names_list:
                results[agent_name] = {"error": "Execution failed"}

        return results

    async def _execute_sequential(
        self,
        agent_names: List[str],
        question: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Execute agents sequentially, passing results forward.

        Args:
            agent_names: List of agent names to execute
            question: User question
            user_id: User identifier

        Returns:
            Dict mapping agent names to their results
        """
        results = {}
        context = {}

        for agent_name in agent_names:
            try:
                logger.info(f"Executing agent: {agent_name}")

                # Execute agent with previous results as context
                result = await self._execute_agent(
                    agent_name,
                    question,
                    user_id,
                    previous_results=context
                )

                results[agent_name] = result
                context[agent_name] = result  # Pass to next agent

            except Exception as e:
                logger.error(f"Agent {agent_name} failed: {e}")
                results[agent_name] = {"error": str(e)}

        return results

    async def _execute_agent(
        self,
        agent_name: str,
        question: str,
        user_id: str,
        previous_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a single agent.

        Args:
            agent_name: Name of agent to execute
            question: User question
            user_id: User identifier
            previous_results: Results from previous agents

        Returns:
            Agent result dict
        """
        if agent_name not in self.agents:
            logger.error(f"Agent '{agent_name}' not found")
            return {"error": f"Agent '{agent_name}' not found"}

        agent = self.agents[agent_name]

        try:
            # Execute agent
            result = await agent.execute(
                user_question=question,
                user_id=user_id,
                context_from_other_agents=previous_results
            )

            return result

        except Exception as e:
            logger.error(f"Agent {agent_name} execution error: {e}")
            return {"error": str(e)}

    def get_available_agents(self) -> List[str]:
        """Get list of available agent names."""
        return list(self.agents.keys())

    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics."""
        return {
            "total_agents": len(self.agents),
            "available_agents": self.get_available_agents(),
            "orchestrator_type": "Q&A Orchestrator"
        }


# Global Q&A orchestrator instance
qa_orchestrator = QAOrchestrator()
