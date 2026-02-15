import os
from uagents_core.utils.registration import (
    register_chat_agent,
    RegistrationRequestCredentials,
)

register_chat_agent(
    "Context Understanding",
    "https://agentverse.ai/v1/mailbox/agent1q07cx08f6p39emk4p3g6hwzndmstszkpgzjp3765yjz7prewd2hewxc9es5",
    active=True,
    credentials=RegistrationRequestCredentials(
        agentverse_api_key=os.environ["AGENTVERSE_KEY"],
        agent_seed_phrase=os.environ["AGENT_SEED_PHRASE"] + "_context",
    ),
)

print("✅ Context Understanding Agent registered!")
