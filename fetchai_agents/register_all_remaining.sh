#!/bin/bash
# Register remaining 7 agents to Agentverse

cd "$(dirname "$0")"
source venv/bin/activate
source .env
export AGENTVERSE_KEY AGENT_SEED_PHRASE

echo "🚀 Registering remaining 7 agents..."
echo "===================================="

echo ""
echo "2/8: Privacy Guardian..."
python register_privacy.py

echo ""
echo "3/8: Follow-Up Generator..."
python register_followup.py

echo ""
echo "4/8: Cross-Pollination..."
python register_crosspoll.py

echo ""
echo "5/8: Q&A Router..."
python register_qa_router.py

echo ""
echo "6/8: Conversation Retrieval..."
python register_retrieval.py

echo ""
echo "7/8: Insight Analyzer..."
python register_insight.py

echo ""
echo "8/8: Response Composer..."
python register_composer.py

echo ""
echo "===================================="
echo "✅ All agents registered!"
echo "View them at: https://agentverse.ai/agents"
