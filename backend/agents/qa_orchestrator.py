"""
Q&A Orchestrator - Manages the question-answering pipeline with multiple agents.
Handles routing, parallel/sequential execution, and response composition.
Data fetching (GCS transcripts) happens here; agents only do reasoning via Claude.
"""
from typing import Dict, List, Any, Optional
import asyncio
import time
from utils.logger import setup_logger

# Import agents
from .query_router import QueryRouterAgent
from .conversation_retrieval import ConversationRetrievalAgent
from .insight import InsightAgent
from .follow_up import FollowUpAgent
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
            "followup": FollowUpAgent(),
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
            print(f"\n{'='*60}")
            print(f"[QA_ORCHESTRATOR] Processing question: '{user_question}'")
            print(f"[QA_ORCHESTRATOR] User ID: {user_id}")
            print(f"[QA_ORCHESTRATOR] Available agents: {list(self.agents.keys())}")
            print(f"{'='*60}")
            logger.info(f"Processing question: {user_question}")

            # Fetch conversation/event data from GCS (source of truth)
            print(f"\n[QA_ORCHESTRATOR] === FETCHING DATA FROM GCS ===")
            conversation_data = self._fetch_transcripts_from_gcs()
            print(f"[QA_ORCHESTRATOR] Fetched {len(conversation_data)} transcripts from GCS")

            # Step 1: Route query
            print(f"\n[QA_ORCHESTRATOR] === STEP 1: Routing query ===")
            logger.info("Step 1: Routing query")
            routing = await self.agents["query_router"].route(user_question)
            print(f"[QA_ORCHESTRATOR] Routing result: {routing}")
            logger.info(f"Routing decision: {routing}")

            # Check if routed agents actually exist in our agents dict
            missing_agents = [a for a in routing.get("agents_needed", []) if a not in self.agents]
            if missing_agents:
                print(f"[QA_ORCHESTRATOR] WARNING: Routed agents NOT in orchestrator: {missing_agents}")
                print(f"[QA_ORCHESTRATOR] Available agents: {list(self.agents.keys())}")
                logger.warning(f"Routed agents not found: {missing_agents}")

            # Step 2: Execute routed agents
            print(f"\n[QA_ORCHESTRATOR] === STEP 2: Executing routed agents ===")
            print(f"[QA_ORCHESTRATOR] Agents to execute: {routing['agents_needed']}")
            print(f"[QA_ORCHESTRATOR] Execution mode: {routing['execution_mode']}")
            logger.info("Step 2: Executing routed agents")
            agent_results = {}

            if routing["execution_mode"] == "parallel":
                agent_results = await self._execute_parallel(
                    routing["agents_needed"],
                    user_question,
                    user_id,
                    conversation_data=conversation_data
                )
            else:
                agent_results = await self._execute_sequential(
                    routing["agents_needed"],
                    user_question,
                    user_id,
                    conversation_data=conversation_data
                )

            print(f"\n[QA_ORCHESTRATOR] Agent results summary:")
            for agent_name, result in agent_results.items():
                has_error = "error" in result
                result_keys = list(result.keys()) if isinstance(result, dict) else type(result).__name__
                print(f"  - {agent_name}: keys={result_keys}, has_error={has_error}")
                if has_error:
                    print(f"    ERROR: {result.get('error', 'unknown')}")

            # Step 3: Compose final answer
            print(f"\n[QA_ORCHESTRATOR] === STEP 3: Composing final response ===")
            logger.info("Step 3: Composing final response")
            final_answer = await self.agents["response_composer"].compose(
                user_question=user_question,
                agent_outputs=agent_results
            )

            execution_time = (time.time() - start_time) * 1000

            print(f"\n[QA_ORCHESTRATOR] === DONE ===")
            print(f"[QA_ORCHESTRATOR] Final answer length: {len(final_answer)} chars")
            print(f"[QA_ORCHESTRATOR] Final answer preview: {final_answer[:200]}...")
            print(f"[QA_ORCHESTRATOR] Execution time: {execution_time:.2f}ms")
            print(f"{'='*60}\n")

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
            execution_time = (time.time() - start_time) * 1000
            print(f"\n[QA_ORCHESTRATOR] !!! ORCHESTRATION FAILED !!!")
            print(f"[QA_ORCHESTRATOR] Error type: {type(e).__name__}")
            print(f"[QA_ORCHESTRATOR] Error: {e}")
            import traceback
            traceback.print_exc()
            logger.error(f"Orchestration failed: {e}", exc_info=True)

            return {
                "answer": "I encountered an error processing your question. Please try rephrasing it.",
                "error": str(e),
                "execution_time_ms": round(execution_time, 2)
            }

    def _fetch_transcripts_from_gcs(self) -> List[Dict[str, Any]]:
        """
        Fetch all transcript/event data from GCS (source of truth).
        GCS transcripts/ folder is where event data lives - added from web app and mobile app.
        Agents receive this data as context - they never touch GCS or any storage directly.

        Returns:
            List of conversation dicts with transcripts
        """
        from services.transcript_storage import transcript_storage

        try:
            # List all transcripts from GCS
            transcripts_meta = transcript_storage.list_transcripts()
            print(f"  [FETCH_GCS] Found {len(transcripts_meta)} transcripts in GCS")

            conv_data = []
            for meta in transcripts_meta:
                transcript_id = meta.get("id", "")

                # Skip empty/test files
                if meta.get("size", 0) < 50:
                    print(f"  [FETCH_GCS]   - '{meta.get('title', '')}': skipping (too small, {meta.get('size', 0)} bytes)")
                    continue

                # Fetch full transcript content
                content = transcript_storage.get_transcript_content(transcript_id)

                if not content:
                    print(f"  [FETCH_GCS]   - '{meta.get('title', '')}': skipping (no content)")
                    continue

                conv_dict = {
                    "id": transcript_id,
                    "title": meta.get("title", transcript_id),
                    "transcript": content,
                    "created_at": meta.get("created_at", ""),
                }
                conv_data.append(conv_dict)
                print(f"  [FETCH_GCS]   - '{conv_dict['title']}': {len(content)} chars")

            return conv_data

        except Exception as e:
            print(f"  [FETCH_GCS] ERROR fetching transcripts: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            logger.error(f"Error fetching transcripts from GCS: {e}")
            return []

    async def _execute_parallel(
        self,
        agent_names: List[str],
        question: str,
        user_id: str,
        conversation_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Execute multiple agents in parallel.

        Args:
            agent_names: List of agent names to execute
            question: User question
            user_id: User identifier
            conversation_data: Conversation data from DB to pass to agents

        Returns:
            Dict mapping agent names to their results
        """
        results = {}

        # Create tasks for all agents
        tasks = []
        for agent_name in agent_names:
            if agent_name in self.agents:
                task = self._execute_agent(agent_name, question, user_id,
                                           conversation_data=conversation_data)
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
        user_id: str,
        conversation_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Execute agents sequentially, passing results forward.

        Args:
            agent_names: List of agent names to execute
            question: User question
            user_id: User identifier
            conversation_data: Conversation data from DB to pass to agents

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
                    previous_results=context,
                    conversation_data=conversation_data
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
        previous_results: Optional[Dict[str, Any]] = None,
        conversation_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Execute a single agent.

        Args:
            agent_name: Name of agent to execute
            question: User question
            user_id: User identifier
            previous_results: Results from previous agents (for sequential mode)
            conversation_data: Conversation data from DB

        Returns:
            Agent result dict
        """
        print(f"\n  [EXECUTE_AGENT] Attempting to execute: '{agent_name}'")

        if agent_name not in self.agents:
            print(f"  [EXECUTE_AGENT] ERROR: Agent '{agent_name}' NOT FOUND in agents dict")
            print(f"  [EXECUTE_AGENT] Available agents: {list(self.agents.keys())}")
            logger.error(f"Agent '{agent_name}' not found")
            return {"error": f"Agent '{agent_name}' not found"}

        agent = self.agents[agent_name]
        print(f"  [EXECUTE_AGENT] Agent type: {type(agent).__name__}")

        try:
            # Build kwargs based on what the agent accepts
            kwargs = {
                "user_question": question,
                "user_id": user_id,
            }

            # Pass conversation data to agents that need it
            if agent_name == "conversation_retrieval":
                kwargs["conversation_data"] = conversation_data
            elif agent_name == "insight":
                kwargs["conversation_data"] = conversation_data
            elif agent_name == "followup":
                kwargs["conversation_data"] = conversation_data
            elif agent_name == "recommendation":
                kwargs["context_from_other_agents"] = previous_results
                kwargs["conversation_data"] = conversation_data

            print(f"  [EXECUTE_AGENT] Calling {agent_name}.execute() with keys: {list(kwargs.keys())}")
            result = await agent.execute(**kwargs)

            print(f"  [EXECUTE_AGENT] {agent_name} returned successfully")
            print(f"  [EXECUTE_AGENT] Result keys: {list(result.keys()) if isinstance(result, dict) else type(result).__name__}")
            if isinstance(result, dict) and "error" in result:
                print(f"  [EXECUTE_AGENT] {agent_name} result contains error: {result['error']}")

            return result

        except TypeError as e:
            print(f"  [EXECUTE_AGENT] TypeError calling {agent_name}: {e}")
            print(f"  [EXECUTE_AGENT] This usually means the agent's execute() has different parameter names")
            import traceback
            traceback.print_exc()
            logger.error(f"Agent {agent_name} execution error: {e}")
            return {"error": str(e)}
        except Exception as e:
            print(f"  [EXECUTE_AGENT] EXCEPTION in {agent_name}: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
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
