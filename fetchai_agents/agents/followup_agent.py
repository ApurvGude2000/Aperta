# ABOUTME: Fetch.ai wrapper for FollowUpAgent.
# ABOUTME: Generates personalized follow-up message variants via backend API.

from uagents import Agent, Context
import httpx
import time
from datetime import datetime

from protocols.followup_protocol import FollowUpRequest, FollowUpResponse
from config import config


# Create agent
followup_agent = Agent(
    name="followup_generator",
    seed=config.agent_seed + "_followup" if config.agent_seed else None,
    port=config.agent_port_start + 2,
    mailbox=True,  # Enable Agentverse mailbox
)


@followup_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Follow-Up Generator Agent started")
    ctx.logger.info(f"Listening on port {config.agent_port_start + 2}")
    ctx.logger.info(f"Price: {config.price_followup_generation} FET per request")


@followup_agent.on_message(model=FollowUpRequest)
async def handle_followup_request(ctx: Context, sender: str, msg: FollowUpRequest):
    """Generate follow-up messages for a person met at an event."""
    start_time = time.time()
    ctx.logger.info(f"Received follow-up generation request from {sender}")
    ctx.logger.info(f"Person: {msg.person_name}")

    try:
        # Call existing FastAPI backend
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Try dashboard follow-ups endpoint
            response = await client.post(
                f"{config.backend_api_url}/dashboard/follow-ups",
                json={
                    "person_data": {
                        "name": msg.person_name,
                        "company": msg.person_company,
                        "role": msg.person_role,
                    },
                    "conversation_context": msg.conversation_context,
                    "conversation_id": msg.conversation_id,
                    "tone_preferences": msg.tone_preferences or ["professional", "casual", "enthusiastic"],
                },
            )
            response.raise_for_status()
            data = response.json()

        execution_time = time.time() - start_time

        # Extract variants from response
        variants = data.get("variants", [])
        if not variants and "suggestions" in data:
            # Fallback: convert suggestions to variants
            variants = [
                {
                    "style": "professional",
                    "subject": f"Great meeting you, {msg.person_name}",
                    "message": suggestion.get("message", ""),
                }
                for suggestion in data["suggestions"][:3]
            ]

        await ctx.send(
            sender,
            FollowUpResponse(
                person_name=msg.person_name,
                variants=variants,
                generated_at=datetime.utcnow().isoformat(),
                execution_time=execution_time,
                success=True,
            ),
        )
        ctx.logger.info(f"Generated {len(variants)} follow-up variants in {execution_time:.2f}s")

    except httpx.HTTPError as e:
        execution_time = time.time() - start_time
        ctx.logger.error(f"HTTP error calling backend: {e}")
        await ctx.send(
            sender,
            FollowUpResponse(
                person_name=msg.person_name,
                variants=[],
                generated_at=datetime.utcnow().isoformat(),
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
            FollowUpResponse(
                person_name=msg.person_name,
                variants=[],
                generated_at=datetime.utcnow().isoformat(),
                execution_time=execution_time,
                success=False,
                error=f"Internal error: {str(e)}",
            ),
        )
