import os
from uagents_core.utils.registration import (
    register_chat_agent,
    RegistrationRequestCredentials,
)

register_chat_agent(
    "Privacy Guardian",
    "https://agentverse.ai/v1/mailbox/agent1qt048623a6echgk33ry5n7ta84ggnvwarfmf5dkv6ptxdpvl2zxqg8yn780",
    active=True,
    credentials=RegistrationRequestCredentials(
        agentverse_api_key=os.environ["AGENTVERSE_KEY"],
        agent_seed_phrase=os.environ["AGENT_SEED_PHRASE"] + "_privacy",
    ),
)

print("✅ Privacy Guardian Agent registered!")
