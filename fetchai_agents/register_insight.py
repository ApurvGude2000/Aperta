import os
from uagents_core.utils.registration import (
    register_chat_agent,
    RegistrationRequestCredentials,
)

register_chat_agent(
    "Insight Analyzer",
    "https://agentverse.ai/v1/mailbox/agent1q2q5q6yjpuptcqz3atrr6qwldcmjxlwwzemqu2shlays72fd4uqxuxrqnvk",
    active=True,
    credentials=RegistrationRequestCredentials(
        agentverse_api_key=os.environ["AGENTVERSE_KEY"],
        agent_seed_phrase=os.environ["AGENT_SEED_PHRASE"] + "_insight",
    ),
)

print("✅ Insight Analyzer Agent registered!")
