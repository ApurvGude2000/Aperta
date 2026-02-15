# ABOUTME: Fetch.ai wrapper for ResponseComposerAgent.
# ABOUTME: Synthesizes final answers from multiple agent outputs via backend orchestrator.

from uagents import Agent, Context
import httpx
import time

from protocols.qa_protocol import QARequest, QAResponse
from config import config


# Create agent
composer_agent = Agent(
    name="response_composer",
    seed=config.agent_seed + "_composer" if config.agent_seed else None,
    port=config.agent_port_start + 7,
    mailbox=True,  # Enable Agentverse mailbox
)


@composer_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Response Composer Agent started")
    ctx.logger.info(f"Listening on port {config.agent_port_start + 7}")
    ctx.logger.info(f"Price: {config.price_response_compose} FET per request")


@composer_agent.on_message(model=QARequest)
async def handle_compose_request(ctx: Context, sender: str, msg: QARequest):
    """Compose final answer by orchestrating multiple agents."""
    start_time = time.time()
    ctx.logger.info(f"Received response composition request from {sender}")
    ctx.logger.info(f"Question: {msg.question}")

    try:
        # Call existing FastAPI backend Q&A endpoint (full orchestration)
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                f"{config.backend_api_url}/qa/ask",
                json={
                    "question": msg.question,
                    "conversation_id": msg.conversation_id,
                    "use_rag": msg.use_rag,
                    "user_id": msg.user_id or "fetchai_user",
                },
            )
            response.raise_for_status()
            data = response.json()

        execution_time = time.time() - start_time

        # Extract composed response
        final_answer = data.get("final_answer", "")
        agents_used = data.get("routed_agents", ["response_composer"])
        agent_trace = data.get("agent_trace", {})

        # Add composer to agents list if not present
        if "response_composer" not in agents_used:
            agents_used.append("response_composer")

        # Extract source conversations
        source_conversations = []
        if agent_trace and isinstance(agent_trace, dict):
            for agent_name, agent_data in agent_trace.items():
                if isinstance(agent_data, dict) and "conversations" in agent_data:
                    source_conversations.extend(agent_data["conversations"])

        await ctx.send(
            sender,
            QAResponse(
                question=msg.question,
                final_answer=final_answer,
                agents_used=agents_used,
                source_conversations=source_conversations if source_conversations else None,
                confidence_score=data.get("confidence_score"),
                agent_trace=agent_trace,
                execution_time=execution_time,
                success=True,
            ),
        )
        ctx.logger.info(f"Response composition completed in {execution_time:.2f}s")
        ctx.logger.info(f"Orchestrated agents: {agents_used}")

    except httpx.HTTPError as e:
        execution_time = time.time() - start_time
        ctx.logger.error(f"HTTP error calling backend: {e}")
        await ctx.send(
            sender,
            QAResponse(
                question=msg.question,
                final_answer="",
                agents_used=["response_composer"],
                execution_time=execution_time,
                success=False,
                error=f"Backend API error: {str(e)}",
            ),
        )

    except Exception as e:
        execution_time = time.time() - start_time
        ctx.logger.error(f"Unexpected error: {e}")
        await ctx.send(
            sender,
            QAResponse(
                question=msg.question,
                final_answer="",
                agents_used=["response_composer"],
                execution_time=execution_time,
                success=False,
                error=f"Internal error: {str(e)}",
            ),
        )
