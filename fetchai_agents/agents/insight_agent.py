# ABOUTME: Fetch.ai wrapper for InsightAgent.
# ABOUTME: Analyzes patterns and trends across conversation history via backend API.

from uagents import Agent, Context
import httpx
import time

from protocols.qa_protocol import QARequest, QAResponse
from config import config


# Create agent
insight_agent = Agent(
    name="insight_analyzer",
    seed=config.agent_seed + "_insight" if config.agent_seed else None,
    port=config.agent_port_start + 6,
    mailbox=True,  # Enable Agentverse mailbox
)


@insight_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Insight Analyzer Agent started")
    ctx.logger.info(f"Listening on port {config.agent_port_start + 6}")
    ctx.logger.info(f"Price: {config.price_insight} FET per request")


@insight_agent.on_message(model=QARequest)
async def handle_insight_request(ctx: Context, sender: str, msg: QARequest):
    """Analyze patterns and trends across conversations."""
    start_time = time.time()
    ctx.logger.info(f"Received insight analysis request from {sender}")
    ctx.logger.info(f"Query: {msg.question}")

    try:
        # Call existing FastAPI backend dashboard metrics endpoint
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Get dashboard metrics for insights
            response = await client.get(
                f"{config.backend_api_url}/dashboard/metrics",
                params={"user_id": msg.user_id or "fetchai_user"},
            )
            response.raise_for_status()
            data = response.json()

        execution_time = time.time() - start_time

        # Format insights as answer
        answer_parts = ["**Conversation Insights:**"]

        if "total_conversations" in data:
            answer_parts.append(f"- Total conversations: {data['total_conversations']}")

        if "total_people_met" in data:
            answer_parts.append(f"- People met: {data['total_people_met']}")

        if "top_topics" in data:
            topics = data["top_topics"][:5]
            answer_parts.append(f"- Top topics: {', '.join(topics)}")

        if "companies_mentioned" in data:
            companies = data["companies_mentioned"][:5]
            answer_parts.append(f"- Companies discussed: {', '.join(companies)}")

        if "sentiment_distribution" in data:
            sentiment = data["sentiment_distribution"]
            answer_parts.append(f"- Sentiment: {sentiment}")

        if "action_items_pending" in data:
            answer_parts.append(f"- Pending action items: {data['action_items_pending']}")

        final_answer = "\n".join(answer_parts)

        await ctx.send(
            sender,
            QAResponse(
                question=msg.question,
                final_answer=final_answer,
                agents_used=["insight_analyzer"],
                agent_trace={"metrics": data},
                execution_time=execution_time,
                success=True,
            ),
        )
        ctx.logger.info(f"Insight analysis completed in {execution_time:.2f}s")

    except httpx.HTTPError as e:
        execution_time = time.time() - start_time
        ctx.logger.error(f"HTTP error calling backend: {e}")
        await ctx.send(
            sender,
            QAResponse(
                question=msg.question,
                final_answer="",
                agents_used=["insight_analyzer"],
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
                agents_used=["insight_analyzer"],
                execution_time=execution_time,
                success=False,
                error=f"Internal error: {str(e)}",
            ),
        )
