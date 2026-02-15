import os
from uagents_core.utils.registration import (
    register_chat_agent,
    RegistrationRequestCredentials,
)

register_chat_agent(
    "Cross-Pollination",
    "https://agentverse.ai/v1/mailbox/agent1qfzgtc343y6r09s4nmwk820rdwad0090rcym5n0h2697zpxg94d2qmamass",
    active=True,
    credentials=RegistrationRequestCredentials(
        agentverse_api_key=os.environ["AGENTVERSE_KEY"],
        agent_seed_phrase=os.environ["AGENT_SEED_PHRASE"] + "_crosspoll",
    ),
)

print("✅ Cross-Pollination Agent registered!")
