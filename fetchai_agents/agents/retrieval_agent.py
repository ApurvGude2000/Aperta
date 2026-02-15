# ABOUTME: Fetch.ai wrapper for ConversationRetrievalAgent.
# ABOUTME: Performs semantic search over conversation history via backend API.

from uagents import Agent, Context
import httpx
import time

from protocols.qa_protocol import QARequest, QAResponse
from config import config


# Create agent
retrieval_agent = Agent(
    name="conversation_retrieval",
    seed=config.agent_seed + "_retrieval" if config.agent_seed else None,
    port=config.agent_port_start + 5,
    mailbox=True,  # Enable Agentverse mailbox
)


@retrieval_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Conversation Retrieval Agent started")
    ctx.logger.info(f"Listening on port {config.agent_port_start + 5}")
    ctx.logger.info(f"Price: {config.price_retrieval} FET per request")


@retrieval_agent.on_message(model=QARequest)
async def handle_retrieval_request(ctx: Context, sender: str, msg: QARequest):
    """Retrieve relevant conversations using semantic search."""
    start_time = time.time()
    ctx.logger.info(f"Received retrieval request from {sender}")
    ctx.logger.info(f"Query: {msg.question}")

    try:
        # Call existing FastAPI backend search endpoint
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{config.backend_api_url}/search/conversations",
                json={
                    "query": msg.question,
                    "limit": msg.max_context_conversations,
                    "user_id": msg.user_id or "fetchai_user",
                    "conversation_id": msg.conversation_id,
                },
            )
            response.raise_for_status()
            data = response.json()

        execution_time = time.time() - start_time

        # Extract search results
        results = data.get("results", [])
        conversation_ids = [result.get("conversation_id") for result in results if "conversation_id" in result]

        # Format as answer with search results
        answer_parts = [f"Found {len(results)} relevant conversations:"]
        for i, result in enumerate(results, 1):
            score = result.get("score", 0.0)
            snippet = result.get("snippet", result.get("text", ""))[:200]
            answer_parts.append(f"{i}. [Score: {score:.2f}] {snippet}...")

        final_answer = "\n".join(answer_parts)

        await ctx.send(
            sender,
            QAResponse(
                question=msg.question,
                final_answer=final_answer,
                agents_used=["conversation_retrieval"],
                source_conversations=conversation_ids if conversation_ids else None,
                confidence_score=results[0].get("score") if results else None,
                agent_trace={"retrieval_results": results},
                execution_time=execution_time,
                success=True,
            ),
        )
        ctx.logger.info(f"Retrieved {len(results)} conversations in {execution_time:.2f}s")

    except httpx.HTTPError as e:
        execution_time = time.time() - start_time
        ctx.logger.error(f"HTTP error calling backend: {e}")
        await ctx.send(
            sender,
            QAResponse(
                question=msg.question,
                final_answer="",
                agents_used=["conversation_retrieval"],
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
                agents_used=["conversation_retrieval"],
                execution_time=execution_time,
                success=False,
                error=f"Internal error: {str(e)}",
            ),
        )
