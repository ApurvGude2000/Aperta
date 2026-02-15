# ABOUTME: Fetch.ai wrapper for QueryRouterAgent.
# ABOUTME: Routes questions to appropriate Q&A agents via backend orchestrator.

from uagents import Agent, Context
import httpx
import time

from protocols.qa_protocol import QARequest, QAResponse
from config import config


# Create agent
qa_router_agent = Agent(
    name="qa_router",
    seed=config.agent_seed + "_qa_router" if config.agent_seed else None,
    port=config.agent_port_start + 4,
    mailbox=True,  # Enable Agentverse mailbox
)


@qa_router_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Q&A Router Agent started")
    ctx.logger.info(f"Listening on port {config.agent_port_start + 4}")
    ctx.logger.info(f"Price: {config.price_qa_routing} FET per request")


@qa_router_agent.on_message(model=QARequest)
async def handle_qa_request(ctx: Context, sender: str, msg: QARequest):
    """Route and answer questions about conversation history."""
    start_time = time.time()
    ctx.logger.info(f"Received Q&A request from {sender}")
    ctx.logger.info(f"Question: {msg.question}")

    try:
        # Call existing FastAPI backend Q&A endpoint
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

        # Extract response data
        final_answer = data.get("final_answer", "")
        agents_used = data.get("routed_agents", [])
        agent_trace = data.get("agent_trace")

        # Try to extract source conversations from trace or response
        source_conversations = []
        if agent_trace and isinstance(agent_trace, dict):
            # Look for conversation references in trace
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
        ctx.logger.info(f"Q&A completed in {execution_time:.2f}s")
        ctx.logger.info(f"Agents used: {agents_used}")

    except httpx.HTTPError as e:
        execution_time = time.time() - start_time
        ctx.logger.error(f"HTTP error calling backend: {e}")
        await ctx.send(
            sender,
            QAResponse(
                question=msg.question,
                final_answer="",
                agents_used=[],
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
                agents_used=[],
                execution_time=execution_time,
                success=False,
                error=f"Internal error: {str(e)}",
            ),
        )
