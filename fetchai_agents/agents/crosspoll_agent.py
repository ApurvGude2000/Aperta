# ABOUTME: Fetch.ai wrapper for CrossPollinationAgent.
# ABOUTME: Suggests strategic introductions between people met at events via backend API.

from uagents import Agent, Context
import httpx
import time

from protocols.crosspoll_protocol import CrossPollinationRequest, CrossPollinationResponse
from config import config


# Create agent
crosspoll_agent = Agent(
    name="cross_pollination",
    seed=config.agent_seed + "_crosspoll" if config.agent_seed else None,
    port=config.agent_port_start + 3,
    mailbox=True,  # Enable Agentverse mailbox
)


@crosspoll_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Cross-Pollination Agent started")
    ctx.logger.info(f"Listening on port {config.agent_port_start + 3}")
    ctx.logger.info(f"Price: {config.price_crosspollination} FET per request")


@crosspoll_agent.on_message(model=CrossPollinationRequest)
async def handle_crosspoll_request(ctx: Context, sender: str, msg: CrossPollinationRequest):
    """Suggest introductions between people met at an event."""
    start_time = time.time()
    ctx.logger.info(f"Received cross-pollination request from {sender}")
    ctx.logger.info(f"Analyzing {len(msg.people_met)} people for introductions")

    try:
        # Call existing FastAPI backend
        async with httpx.AsyncClient(timeout=180.0) as client:
            # Construct request payload
            payload = {
                "people_met": msg.people_met,
                "min_match_score": msg.min_match_score,
            }
            if msg.event_id:
                payload["event_id"] = msg.event_id
            if msg.conversation_ids:
                payload["conversation_ids"] = msg.conversation_ids

            # Try knowledge graph endpoint for cross-pollination
            response = await client.post(
                f"{config.backend_api_url}/knowledge-graph/introductions",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        execution_time = time.time() - start_time

        # Extract introductions from response
        introductions = data.get("introductions", [])
        research_sources = data.get("research_sources", [])

        await ctx.send(
            sender,
            CrossPollinationResponse(
                introductions=introductions,
                total_suggested=len(introductions),
                research_sources=research_sources,
                execution_time=execution_time,
                success=True,
            ),
        )
        ctx.logger.info(f"Generated {len(introductions)} introduction suggestions in {execution_time:.2f}s")

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            # Endpoint doesn't exist yet - return helpful error
            execution_time = time.time() - start_time
            ctx.logger.warning("Cross-pollination endpoint not implemented yet")
            await ctx.send(
                sender,
                CrossPollinationResponse(
                    introductions=[],
                    total_suggested=0,
                    execution_time=execution_time,
                    success=False,
                    error="Cross-pollination feature not yet available in backend",
                ),
            )
        else:
            raise

    except httpx.HTTPError as e:
        execution_time = time.time() - start_time
        ctx.logger.error(f"HTTP error calling backend: {e}")
        await ctx.send(
            sender,
            CrossPollinationResponse(
                introductions=[],
                total_suggested=0,
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
            CrossPollinationResponse(
                introductions=[],
                total_suggested=0,
                execution_time=execution_time,
                success=False,
                error=f"Internal error: {str(e)}",
            ),
        )
