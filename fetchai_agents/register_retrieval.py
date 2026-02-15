import os
from uagents_core.utils.registration import (
    register_chat_agent,
    RegistrationRequestCredentials,
)

register_chat_agent(
    "Conversation Retrieval",
    "https://agentverse.ai/v1/mailbox/agent1qd8fcxr8s6uld5ly5rddyay798nq0w3u2m58a0xenh5hjae7tvww7hxm5nl",
    active=True,
    credentials=RegistrationRequestCredentials(
        agentverse_api_key=os.environ["AGENTVERSE_KEY"],
        agent_seed_phrase=os.environ["AGENT_SEED_PHRASE"] + "_retrieval",
    ),
)

print("✅ Conversation Retrieval Agent registered!")
