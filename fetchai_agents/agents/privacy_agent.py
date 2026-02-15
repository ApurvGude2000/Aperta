# ABOUTME: Fetch.ai wrapper for PrivacyGuardianAgent.
# ABOUTME: Redacts PII (emails, phones, addresses) from transcripts via backend API.

from uagents import Agent, Context
import httpx
import time
import re

from protocols.privacy_protocol import PrivacyRedactionRequest, PrivacyRedactionResponse
from config import config


# Create agent
privacy_agent = Agent(
    name="privacy_guardian",
    seed=config.agent_seed + "_privacy" if config.agent_seed else None,
    port=config.agent_port_start + 1,
    mailbox=True,  # Enable Agentverse mailbox
)


@privacy_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Privacy Guardian Agent started")
    ctx.logger.info(f"Listening on port {config.agent_port_start + 1}")
    ctx.logger.info(f"Price: {config.price_privacy_redaction} FET per request")


def redact_pii_local(
    text: str, redact_names: bool, redact_emails: bool, redact_phones: bool, redact_addresses: bool
) -> tuple[str, dict]:
    """
    Local PII redaction (fallback if backend endpoint doesn't exist).
    Returns (redacted_text, redaction_counts).
    """
    redacted = text
    counts = {}

    if redact_emails:
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        emails = re.findall(email_pattern, redacted)
        redacted = re.sub(email_pattern, "[EMAIL_REDACTED]", redacted)
        counts["email"] = len(emails)

    if redact_phones:
        phone_pattern = r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"
        phones = re.findall(phone_pattern, redacted)
        redacted = re.sub(phone_pattern, "[PHONE_REDACTED]", redacted)
        counts["phone"] = len(phones)

    if redact_addresses:
        # Simple address pattern (can be improved)
        address_pattern = r"\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd)\b"
        addresses = re.findall(address_pattern, redacted)
        redacted = re.sub(address_pattern, "[ADDRESS_REDACTED]", redacted)
        counts["address"] = len(addresses)

    return redacted, counts


@privacy_agent.on_message(model=PrivacyRedactionRequest)
async def handle_privacy_request(ctx: Context, sender: str, msg: PrivacyRedactionRequest):
    """Redact PII from a transcript."""
    start_time = time.time()
    ctx.logger.info(f"Received privacy redaction request from {sender}")

    try:
        # Try backend API first (if endpoint exists)
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{config.backend_api_url}/audio/redact",
                    json={
                        "transcript": msg.transcript,
                        "redact_names": msg.redact_names,
                        "redact_emails": msg.redact_emails,
                        "redact_phones": msg.redact_phones,
                        "redact_addresses": msg.redact_addresses,
                    },
                )
                response.raise_for_status()
                data = response.json()

                execution_time = time.time() - start_time
                await ctx.send(
                    sender,
                    PrivacyRedactionResponse(
                        redacted_text=data["redacted_text"],
                        redactions_made=data.get("redactions_made", 0),
                        redaction_types=data.get("redaction_types", {}),
                        execution_time=execution_time,
                        success=True,
                    ),
                )
                ctx.logger.info(f"Privacy redaction completed via backend in {execution_time:.2f}s")
                return

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                ctx.logger.warning("Backend redaction endpoint not found, using local fallback")
            else:
                raise

        # Fallback to local redaction
        redacted_text, redaction_counts = redact_pii_local(
            msg.transcript,
            msg.redact_names,
            msg.redact_emails,
            msg.redact_phones,
            msg.redact_addresses,
        )

        execution_time = time.time() - start_time
        total_redactions = sum(redaction_counts.values())

        await ctx.send(
            sender,
            PrivacyRedactionResponse(
                redacted_text=redacted_text,
                redactions_made=total_redactions,
                redaction_types=redaction_counts,
                execution_time=execution_time,
                success=True,
            ),
        )
        ctx.logger.info(f"Privacy redaction completed locally in {execution_time:.2f}s")
        ctx.logger.info(f"Redactions: {redaction_counts}")

    except Exception as e:
        execution_time = time.time() - start_time
        ctx.logger.error(f"Error during redaction: {e}")
        await ctx.send(
            sender,
            PrivacyRedactionResponse(
                redacted_text=msg.transcript,
                redactions_made=0,
                redaction_types={},
                execution_time=execution_time,
                success=False,
                error=f"Redaction failed: {str(e)}",
            ),
        )
