import os
from uagents_core.utils.registration import (
    register_chat_agent,
    RegistrationRequestCredentials,
)

register_chat_agent(
    "Response Composer",
    "https://agentverse.ai/v1/mailbox/agent1qw9jumnzq53gfxxqavafyvwacuxjehflap27mw97dhsthwr8y3tf6rl00p9",
    active=True,
    credentials=RegistrationRequestCredentials(
        agentverse_api_key=os.environ["AGENTVERSE_KEY"],
        agent_seed_phrase=os.environ["AGENT_SEED_PHRASE"] + "_composer",
    ),
)

print("✅ Response Composer Agent registered!")
