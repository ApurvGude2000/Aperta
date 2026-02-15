# ABOUTME: Fetch.ai wrapper for ContextUnderstandingAgent.
# ABOUTME: Extracts entities, topics, and insights from conversation transcripts via backend API.

from uagents import Agent, Context
import httpx
import time
from typing import Optional

from protocols.context_protocol import ContextExtractionRequest, ContextExtractionResponse
from config import config


# Create agent
context_agent = Agent(
    name="context_understanding",
    seed=config.agent_seed + "_context" if config.agent_seed else None,
    port=config.agent_port_start,
    mailbox=True,  # Enable Agentverse mailbox
)


@context_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Context Understanding Agent started")
    ctx.logger.info(f"Listening on port {config.agent_port_start}")
    ctx.logger.info(f"Price: {config.price_context_understanding} FET per request")


@context_agent.on_message(model=ContextExtractionRequest)
async def handle_context_request(ctx: Context, sender: str, msg: ContextExtractionRequest):
    """Extract context and entities from a conversation."""
    start_time = time.time()
    ctx.logger.info(f"Received context extraction request from {sender}")
    ctx.logger.info(f"Conversation ID: {msg.conversation_id}")

    try:
        # Call existing FastAPI backend
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{config.backend_api_url}/conversations/{msg.conversation_id}/analyze",
                json={
                    "transcript": msg.transcript,
                    "speaker_labels": msg.speaker_labels or {},
                    "user_goals": msg.user_goals or [],
                },
            )
            response.raise_for_status()
            data = response.json()

        execution_time = time.time() - start_time

        # Send success response
        await ctx.send(
            sender,
            ContextExtractionResponse(
                conversation_id=msg.conversation_id,
                people=data.get("people", []),
                companies=data.get("companies_mentioned", []),
                topics=data.get("topics_discussed", []),
                action_items=data.get("action_items", []),
                sentiment=data.get("sentiment", "neutral"),
                summary=data.get("conversation_summary", ""),
                execution_time=execution_time,
                success=True,
            ),
        )
        ctx.logger.info(f"Context extraction completed in {execution_time:.2f}s")

    except httpx.HTTPError as e:
        execution_time = time.time() - start_time
        ctx.logger.error(f"HTTP error calling backend: {e}")
        await ctx.send(
            sender,
            ContextExtractionResponse(
                conversation_id=msg.conversation_id,
                people=[],
                companies=[],
                topics=[],
                action_items=[],
                sentiment="unknown",
                summary="",
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
            ContextExtractionResponse(
                conversation_id=msg.conversation_id,
                people=[],
                companies=[],
                topics=[],
                action_items=[],
                sentiment="unknown",
                summary="",
                execution_time=execution_time,
                success=False,
                error=f"Internal error: {str(e)}",
            ),
        )
