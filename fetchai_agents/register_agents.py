#!/usr/bin/env python3
# ABOUTME: Script to register all 8 agents on Agentverse using REST API.
# ABOUTME: Automates agent registration instead of manual UI clicks.

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials from environment
AGENTVERSE_KEY = os.getenv("AGENTVERSE_KEY") or os.getenv("FETCHAI_API_KEY")
AGENT_SEED = os.getenv("AGENT_SEED")

if not AGENTVERSE_KEY or not AGENT_SEED:
    print("❌ Error: AGENTVERSE_KEY and AGENT_SEED must be set in .env")
    print("   Add these to your .env file:")
    print("   AGENTVERSE_KEY=your_api_key")
    print("   AGENT_SEED=your_seed_phrase")
    exit(1)

# Agent configurations
agents = [
    {
        "name": "Context Understanding",
        "address": "agent1q07cx08f6p39emk4p3g6hwzndmstszkpgzjp3765yjz7prewd2hewxc9es5",
        "seed_suffix": "_context",
    },
    {
        "name": "Privacy Guardian",
        "address": "agent1qt048623a6echgk33ry5n7ta84ggnvwarfmf5dkv6ptxdpvl2zxqg8yn780",
        "seed_suffix": "_privacy",
    },
    {
        "name": "Follow-Up Generator",
        "address": "agent1qg6qg835gx0erkkk7hgw4hpk349ytcfuuykpkjauezlymewnqzjqkqtschk",
        "seed_suffix": "_followup",
    },
    {
        "name": "Cross-Pollination",
        "address": "agent1qfzgtc343y6r09s4nmwk820rdwad0090rcym5n0h2697zpxg94d2qmamass",
        "seed_suffix": "_crosspoll",
    },
    {
        "name": "Q&A Router",
        "address": "agent1q0ku46ymqw0y6venzndygfue4an3fd6kv9t55lpmgz3gadwdxnsautkjqdm",
        "seed_suffix": "_qa_router",
    },
    {
        "name": "Conversation Retrieval",
        "address": "agent1qd8fcxr8s6uld5ly5rddyay798nq0w3u2m58a0xenh5hjae7tvww7hxm5nl",
        "seed_suffix": "_retrieval",
    },
    {
        "name": "Insight Analyzer",
        "address": "agent1q2q5q6yjpuptcqz3atrr6qwldcmjxlwwzemqu2shlays72fd4uqxuxrqnvk",
        "seed_suffix": "_insight",
    },
    {
        "name": "Response Composer",
        "address": "agent1qw9jumnzq53gfxxqavafyvwacuxjehflap27mw97dhsthwr8y3tf6rl00p9",
        "seed_suffix": "_composer",
    },
]

print("=" * 60)
print("Registering Agents on Agentverse")
print("=" * 60)

AGENTVERSE_API_URL = "https://agentverse.ai/v1/agents"

headers = {
    "Authorization": f"Bearer {AGENTVERSE_KEY}",
    "Content-Type": "application/json",
}

success_count = 0
for agent in agents:
    print(f"\n📝 Registering: {agent['name']}")
    print(f"   Address: {agent['address'][:20]}...")

    try:
        mailbox_url = f"https://agentverse.ai/v1/mailbox/{agent['address']}"

        payload = {
            "name": agent['name'],
            "address": agent['address'],
            "endpoint": mailbox_url,
            "type": "python",
        }

        response = requests.post(
            AGENTVERSE_API_URL,
            json=payload,
            headers=headers,
            timeout=30,
        )

        if response.status_code in [200, 201]:
            print(f"   ✅ Successfully registered!")
            success_count += 1
        elif response.status_code == 409:
            print(f"   ⚠️  Already registered (skipping)")
            success_count += 1
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"   ❌ Failed: {e}")

print("\n" + "=" * 60)
print(f"Registration Complete: {success_count}/{len(agents)} agents registered")
print("=" * 60)

if success_count == len(agents):
    print("\n🎉 All agents registered successfully!")
    print("   View them at: https://agentverse.ai/agents")
else:
    print(f"\n⚠️  {len(agents) - success_count} agent(s) failed to register")
    print("   Check errors above and try again")
