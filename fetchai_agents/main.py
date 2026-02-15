# ABOUTME: Main entry point for Fetch.ai Agentverse bureau.
# ABOUTME: Runs all 8 agents in parallel for decentralized agent networking.

from uagents import Bureau
import sys
import logging

from agents import (
    context_agent,
    privacy_agent,
    followup_agent,
    crosspoll_agent,
    qa_router_agent,
    retrieval_agent,
    insight_agent,
    composer_agent,
)
from config import config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Run all Fetch.ai agents in a bureau."""

    # Validate configuration
    if not config.backend_api_url:
        logger.error("BACKEND_API_URL not configured")
        sys.exit(1)

    if config.agent_seed and len(config.agent_seed) < 32:
        logger.warning("AGENT_SEED should be at least 32 characters for security")

    # Create bureau to run all agents
    bureau = Bureau(port=config.agent_port_start - 1)

    # Register all 8 agents
    logger.info("Registering agents with bureau...")

    bureau.add(context_agent)
    logger.info("✓ Context Understanding Agent registered")

    bureau.add(privacy_agent)
    logger.info("✓ Privacy Guardian Agent registered")

    bureau.add(followup_agent)
    logger.info("✓ Follow-Up Generator Agent registered")

    bureau.add(crosspoll_agent)
    logger.info("✓ Cross-Pollination Agent registered")

    bureau.add(qa_router_agent)
    logger.info("✓ Q&A Router Agent registered")

    bureau.add(retrieval_agent)
    logger.info("✓ Conversation Retrieval Agent registered")

    bureau.add(insight_agent)
    logger.info("✓ Insight Analyzer Agent registered")

    bureau.add(composer_agent)
    logger.info("✓ Response Composer Agent registered")

    # Print configuration
    logger.info("\n" + "=" * 60)
    logger.info("Fetch.ai Agentverse Bureau Starting")
    logger.info("=" * 60)
    logger.info(f"Backend API: {config.backend_api_url}")
    logger.info(f"Bureau Port: {config.agent_port_start - 1}")
    logger.info(f"Agent Ports: {config.agent_port_start}-{config.agent_port_start + 7}")
    logger.info(f"Payment Verification: {'Enabled' if config.enable_payment_verification else 'Disabled'}")
    logger.info("\nAgent Pricing (FET tokens):")
    logger.info(f"  - Context Understanding: {config.price_context_understanding}")
    logger.info(f"  - Privacy Redaction: {config.price_privacy_redaction}")
    logger.info(f"  - Follow-Up Generation: {config.price_followup_generation}")
    logger.info(f"  - Cross-Pollination: {config.price_crosspollination}")
    logger.info(f"  - Q&A Routing: {config.price_qa_routing}")
    logger.info(f"  - Retrieval: {config.price_retrieval}")
    logger.info(f"  - Insight Analysis: {config.price_insight}")
    logger.info(f"  - Response Composition: {config.price_response_compose}")
    logger.info("=" * 60)
    logger.info("\n🚀 All agents ready. Starting bureau...\n")

    try:
        # Run the bureau (this blocks until interrupted)
        bureau.run()
    except KeyboardInterrupt:
        logger.info("\n\nShutting down bureau...")
        logger.info("All agents stopped.")
    except Exception as e:
        logger.error(f"Bureau error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
