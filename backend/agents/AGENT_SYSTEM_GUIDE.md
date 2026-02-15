# Aperta Agent System Guide

## 🎯 System Overview

The Aperta agent system follows a three-phase architecture:

### 1. **Data Capture Phase**
- **Privacy Guardian Agent**: Redacts PII before database storage
  - Runs on every transcript chunk (every 3 seconds)
  - Output: Plain text with [PHONE], [EMAIL], etc. redactions

### 2. **Post-Event Processing**
- **Context Understanding Agent**: Extracts structured entities and insights
  - Runs once per conversation after event ends
  - Output: JSON with people, topics, action items, sentiment, etc.

- **Follow-Up Agent**: Generates personalized messages
  - Runs once per person met
  - Output: 3 message variants (Professional, Friendly, Value-First)

- **Cross-Pollination Agent**: Finds introduction opportunities
  - Runs once per event (if 3+ people)
  - Uses Perplexity API for enrichment
  - Output: JSON with introduction suggestions

### 3. **Question-Answering Phase**
- **Query Router**: Decides which agents to call
- **Conversation Retrieval**: Searches conversations
- **Insight Agent**: Analyzes patterns and trends
- **Recommendation Agent**: Suggests next actions
- **Response Composer**: Synthesizes final answer

## 📋 Agent Specifications

### Privacy Guardian Agent
```python
from agents import PrivacyGuardianAgent, redact_pii

agent = PrivacyGuardianAgent()
redacted_text = await agent.redact_transcript("Hi, my email is alice@example.com")
# Output: "Hi, my email is [EMAIL]"

# Or use convenience function
redacted = await redact_pii("Call me at 415-555-1234")
# Output: "Call me at [PHONE]"
```

### Context Understanding Agent
```python
from agents import ContextUnderstandingAgent

agent = ContextUnderstandingAgent()
result = await agent.analyze_conversation({
    "conversation_id": "conv_123",
    "full_transcript": "Speaker 1: Hi I'm Alice...",
    "speaker_labels": ["Speaker 1", "Speaker 2"],
    "duration_minutes": 8,
    "user_goals": ["Find investors"],
    "event_context": {
        "event_name": "TechCrunch Disrupt",
        "event_date": "2026-03-15"
    }
})

# result contains: people, topics, action_items, sentiment, goal_alignment
```

### Follow-Up Agent
```python
from agents import FollowUpAgent

agent = FollowUpAgent()
messages = await agent.generate_messages(
    person_data={
        "name": "Alice Chen",
        "role": "Partner",
        "company": "Acme Ventures"
    },
    context_data={
        "conversation_summary": "Alice is healthcare AI investor...",
        "topics_discussed": ["AI safety", "Series A"],
        "action_items": [{"action": "Send pitch deck", "priority": "high"}],
        "key_interests": ["Healthcare AI"]
    },
    user_context={
        "name": "John Doe",
        "company": "HealthAI Inc",
        "role": "Founder",
        "event": "TechCrunch Disrupt"
    }
)

# messages["variants"] contains 3 message variants
```

### Cross-Pollination Agent
```python
from agents import CrossPollinationAgent

agent = CrossPollinationAgent()
connections = await agent.find_connections(
    people_met=[
        {
            "name": "Alice Chen",
            "role": "Partner",
            "company": "Acme Ventures",
            "interests": ["Healthcare AI"],
            "needs": ["Deal flow"],
            "skills": ["Funding expertise"]
        },
        {
            "name": "Bob Smith",
            "role": "Founder",
            "company": "MediAI",
            "interests": ["Medical imaging"],
            "needs": ["Series A funding"],
            "skills": ["Healthcare AI product"]
        }
    ],
    event_id="event_123"
)

# connections["introductions"] contains introduction suggestions
```

### Q&A System (Question-Answering)
```python
from agents import qa_orchestrator

# Ask a question
result = await qa_orchestrator.answer_question(
    user_question="Who should I follow up with from TechCrunch?",
    user_id="user_123"
)

# result contains:
# - answer: Final composed answer
# - agent_trace: Debugging info
# - execution_time_ms: Performance metric
```

## 🔧 Configuration

Add to your `.env` file:
```bash
# Required
ANTHROPIC_API_KEY=your_anthropic_key

# Optional (for Cross-Pollination Agent)
PERPLEXITY_API_KEY=your_perplexity_key
```

## 📊 Data Flow

### Data Capture Flow
```
Transcript Chunk (every 3s)
    ↓
Privacy Guardian Agent (redacts PII)
    ↓
Save to Local Database (redacted)
    ↓
Upload to Cloud
```

### Post-Event Processing Flow
```
Event Ends
    ↓
Context Understanding Agent (extracts entities)
    ↓
    ├─→ Follow-Up Agent (per person)
    ├─→ Cross-Pollination Agent (if 3+ people)
    └─→ Upload Results to Cloud
```

### Q&A Flow
```
User Question
    ↓
Query Router (decides which agents)
    ↓
Execute Agents (parallel or sequential)
    ├─→ Conversation Retrieval
    ├─→ Insight Agent
    └─→ Recommendation Agent
    ↓
Response Composer (synthesizes answer)
    ↓
Final Answer to User
```

## 🚀 Usage Examples

### Example 1: Process a recorded conversation
```python
from agents import PrivacyGuardianAgent, ContextUnderstandingAgent

# Step 1: Redact PII from transcript chunks
privacy_agent = PrivacyGuardianAgent()
redacted_chunks = []
for chunk in transcript_chunks:
    redacted = await privacy_agent.redact_transcript(chunk["text"])
    redacted_chunks.append(redacted)

# Save to database (redacted)
# ... database save logic ...

# Step 2: After event ends, extract context
context_agent = ContextUnderstandingAgent()
full_transcript = "\n".join(redacted_chunks)
context = await context_agent.analyze_conversation({
    "conversation_id": "conv_123",
    "full_transcript": full_transcript,
    # ... other fields ...
})
```

### Example 2: Generate follow-ups for everyone met
```python
from agents import FollowUpAgent

follow_up_agent = FollowUpAgent()

# For each person extracted by Context Understanding
for person in context["people"]:
    messages = await follow_up_agent.generate_messages(
        person_data=person,
        context_data=context,
        user_context=user_info
    )

    # Store messages for user to review
    # ... database save logic ...
```

### Example 3: Answer user questions
```python
from agents import qa_orchestrator

# User asks a question
answer = await qa_orchestrator.answer_question(
    user_question="What topics come up most in my conversations?",
    user_id="user_123"
)

print(answer["answer"])  # Natural language answer
print(f"Answered in {answer['execution_time_ms']}ms")
```

## 🛠️ Error Handling

All agents include robust error handling:

```python
try:
    result = await agent.execute(...)
except Exception as e:
    logger.error(f"Agent error: {e}")
    # Agents return fallback responses on error
```

Agents will:
- Return fallback responses instead of crashing
- Log errors for debugging
- Preserve original data when redaction fails

## 📈 Performance Considerations

- **Privacy Guardian**: Runs on every chunk, keep prompts minimal
- **Context Understanding**: Runs once per conversation, can be heavier
- **Follow-Up**: Parallel execution recommended for multiple people
- **Q&A**: Router decides parallel vs sequential based on question type

## 🔐 Privacy & Security

- **PII Protection**: Privacy Guardian runs BEFORE database save
- **Redaction Rules**: [PHONE], [EMAIL], [SSN], [CREDIT_CARD], [ADDRESS]
- **Data Kept**: Names, companies, job titles (networking data)
- **Perplexity**: Only uses public information for enrichment

## 📝 Best Practices

1. **Always redact before saving**: Run Privacy Guardian on all transcript chunks
2. **Wait for event completion**: Run Context Understanding after event ends
3. **Batch follow-ups**: Generate all follow-up messages in parallel
4. **Use Q&A for insights**: Let the system route complex questions
5. **Monitor Perplexity usage**: API has rate limits

## 🐛 Troubleshooting

### Agent returns empty/invalid output
- Check Claude API key is valid
- Verify input format matches agent specifications
- Check logs for JSON parsing errors

### Perplexity enrichment fails
- Verify `PERPLEXITY_API_KEY` is set
- Check API rate limits
- Agent will fallback to working without enrichment

### Q&A gives unexpected answers
- Check agent_trace in result for debugging
- Verify conversation data is in database
- Review routing decision in trace

## 📚 Additional Resources

- Agent specifications: See docstrings in each agent file
- System prompts: Check `system_prompt` in agent `__init__` methods
- API documentation: See FastAPI docs at `/docs`

---

**Version**: 2.0.0
**Last Updated**: 2026-02-14
