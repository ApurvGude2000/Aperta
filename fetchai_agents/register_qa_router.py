import os
from uagents_core.utils.registration import (
    register_chat_agent,
    RegistrationRequestCredentials,
)

register_chat_agent(
    "Q&A Router",
    "https://agentverse.ai/v1/mailbox/agent1q0ku46ymqw0y6venzndygfue4an3fd6kv9t55lpmgz3gadwdxnsautkjqdm",
    active=True,
    credentials=RegistrationRequestCredentials(
        agentverse_api_key=os.environ["AGENTVERSE_KEY"],
        agent_seed_phrase=os.environ["AGENT_SEED_PHRASE"] + "_qa_router",
    ),
)

print("✅ Q&A Router Agent registered!")
