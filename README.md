# Aperta - AI-Powered Networking Intelligence Platform

Aperta is an advanced AI-powered networking assistant that helps professionals extract actionable insights from conversations, manage relationships intelligently, and optimize their networking strategy using multi-agent orchestration.

## Overview

Aperta uses a sophisticated multi-agent architecture powered by Claude (Anthropic) to analyze conversations, extract entities, protect privacy, and provide strategic networking advice. The system intelligently routes queries to specialized agents and orchestrates their collaboration for comprehensive analysis.

## Architecture

### Multi-Agent System

Aperta employs six specialized AI agents, each focused on a specific aspect of networking intelligence:

1. **Perception Agent** - Extracts entities (people, organizations, locations, dates) and recognizes intents from conversations
2. **Privacy Guardian Agent** - Detects and redacts PII (Personally Identifiable Information) to ensure data privacy
3. **Context Understanding Agent** - Analyzes conversational context, relationships, and emotional tone
4. **Strategic Networking Agent** - Provides actionable networking strategies and relationship insights
5. **Follow-Up Agent** - Generates intelligent follow-up suggestions and action items
6. **Intelligent Router** - Routes queries to the most appropriate agent(s) based on intent analysis

### Orchestrator

The **Agent Orchestrator** coordinates multi-agent workflows, managing:
- Sequential agent execution with dependency management
- Parallel agent execution for independent tasks
- Context sharing between agents
- Result aggregation and synthesis

### Backend Stack

- **Framework**: FastAPI (Python 3.11+)
- **AI/LLM**: Anthropic Claude (claude-opus-4-6)
- **Database**: SQLite with SQLAlchemy (async)
- **Vector Store**: ChromaDB for RAG (Retrieval-Augmented Generation)
- **Logging**: Structured logging with structlog

### Frontend Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router v6
- **HTTP Client**: Axios

## Project Structure

```
Aperta/
├── README.md                          # This file
├── .gitignore                         # Git ignore rules
│
├── backend/                           # Python FastAPI backend
│   ├── .env.example                   # Environment variables template
│   ├── requirements.txt               # Python dependencies
│   ├── main.py                        # FastAPI application entry point
│   ├── config.py                      # Application configuration
│   │
│   ├── agents/                        # AI Agent implementations
│   │   ├── __init__.py
│   │   ├── base.py                    # Base agent class
│   │   ├── perception.py              # Entity extraction & intent recognition
│   │   ├── privacy_guardian.py        # PII detection & redaction
│   │   ├── context_understanding.py   # Context & relationship analysis
│   │   ├── strategic_networking.py    # Networking strategy advice
│   │   ├── follow_up.py               # Follow-up suggestions
│   │   ├── orchestrator.py            # Multi-agent orchestration
│   │   └── intelligent_router.py      # Query routing logic
│   │
│   ├── tools/                         # Agent tools & utilities
│   │   ├── __init__.py
│   │   ├── entity_extractor.py        # Named entity recognition
│   │   ├── intent_recognizer.py       # Intent classification
│   │   ├── pii_detector.py            # PII detection
│   │   └── redactor.py                # Text redaction
│   │
│   ├── services/                      # Business logic services
│   │   ├── __init__.py
│   │   └── rag_context.py             # RAG context management
│   │
│   ├── utils/                         # Utility modules
│   │   ├── __init__.py
│   │   ├── logger.py                  # Structured logging
│   │   └── console_logger.py          # Console output formatting
│   │
│   ├── db/                            # Database layer
│   │   ├── __init__.py
│   │   ├── database.py                # Database connection
│   │   ├── models.py                  # SQLAlchemy models
│   │   └── session.py                 # Session management
│   │
│   └── api/                           # API routes
│       ├── __init__.py
│       └── routes/
│           ├── __init__.py
│           ├── qa.py                  # Q&A endpoints
│           └── conversations.py       # Conversation CRUD
│
├── frontend/                          # React TypeScript frontend
│   ├── package.json                   # NPM dependencies
│   ├── vite.config.ts                 # Vite configuration
│   ├── tsconfig.json                  # TypeScript configuration
│   ├── index.html                     # HTML entry point
│   │
│   └── src/
│       ├── main.tsx                   # React entry point
│       ├── App.tsx                    # Main app component
│       │
│       ├── pages/                     # Page components
│       │   ├── AskQuestions.tsx       # Q&A interface
│       │   ├── ConversationList.tsx   # List all conversations
│       │   ├── ConversationDetail.tsx # View conversation details
│       │   └── ConversationForm.tsx   # Create/edit conversation
│       │
│       ├── components/                # Reusable components
│       │   ├── ConversationCard.tsx   # Conversation preview card
│       │   └── ExportDialog.tsx       # Export functionality
│       │
│       ├── api/                       # API client
│       │   └── client.ts              # Axios HTTP client
│       │
│       └── types/                     # TypeScript types
│           └── index.ts               # Type definitions
│
└── sample_transcripts/                # Sample data & prompts
    └── custom_prompt.txt              # Custom system prompts
```

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- Node.js 18+ and npm
- Anthropic API key (get from https://console.anthropic.com/)

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

5. **Initialize database**
   ```bash
   # Database will be created automatically on first run
   # For migrations (if using Alembic):
   alembic upgrade head
   ```

6. **Run the backend server**
   ```bash
   python main.py
   # Or with uvicorn directly:
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   Backend will be available at: `http://localhost:8000`
   API Documentation: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Run the development server**
   ```bash
   npm run dev
   ```

   Frontend will be available at: `http://localhost:5173`

4. **Build for production**
   ```bash
   npm run build
   ```

## API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Root Information
```http
GET /
```
Returns API information and available endpoints.

#### 2. Health Check
```http
GET /health
```
Returns application health status.

#### 3. Ask Question (Q&A)
```http
POST /qa/ask
Content-Type: application/json

{
  "question": "What networking strategies were discussed?",
  "conversation_id": 123,
  "use_rag": true
}
```

Routes the question to appropriate agent(s) and returns analysis.

**Response:**
```json
{
  "answer": "Based on the conversation...",
  "routing_decision": {
    "selected_agents": ["PerceptionAgent", "StrategicNetworkingAgent"],
    "execution_mode": "sequential",
    "reasoning": "..."
  },
  "conversation_id": 123,
  "timestamp": "2024-02-14T16:00:00Z"
}
```

#### 4. Create Conversation
```http
POST /conversations
Content-Type: application/json

{
  "title": "Career Fair Networking",
  "transcript": "Full conversation transcript...",
  "metadata": {
    "date": "2024-02-14",
    "location": "Tech Conference"
  }
}
```

#### 5. List Conversations
```http
GET /conversations?skip=0&limit=20
```

#### 6. Get Conversation
```http
GET /conversations/{conversation_id}
```

#### 7. Update Conversation
```http
PUT /conversations/{conversation_id}
Content-Type: application/json

{
  "title": "Updated Title",
  "transcript": "Updated transcript..."
}
```

#### 8. Delete Conversation
```http
DELETE /conversations/{conversation_id}
```

#### 9. Export Conversation
```http
GET /conversations/{conversation_id}/export?format=json
```

Supported formats: `json`, `txt`, `markdown`

## Agent Descriptions

### Perception Agent
**Purpose**: First-line analysis of conversations to extract structured information.

**Capabilities**:
- Named Entity Recognition (NER): Extracts people, organizations, locations, dates
- Intent Recognition: Identifies user intents (analyze, extract, summarize, etc.)
- Entity relationship mapping

**Use Cases**:
- "Who did I meet at the conference?"
- "Extract all company names mentioned"
- "What dates were discussed?"

### Privacy Guardian Agent
**Purpose**: Ensure data privacy and compliance through PII detection and redaction.

**Capabilities**:
- PII Detection: Email addresses, phone numbers, SSNs, credit cards, addresses
- Selective Redaction: Configurable redaction rules
- Privacy risk assessment
- Audit trail for redactions

**Use Cases**:
- Automatically redact sensitive information before sharing
- Generate privacy reports
- Ensure GDPR/CCPA compliance

### Context Understanding Agent
**Purpose**: Deep contextual analysis of conversations and relationships.

**Capabilities**:
- Conversation flow analysis
- Relationship mapping and dynamics
- Emotional tone detection
- Topic clustering and theme extraction
- Power dynamics and influence analysis

**Use Cases**:
- "What was the overall sentiment of the conversation?"
- "Analyze the relationship between John and Sarah"
- "What are the key themes discussed?"

### Strategic Networking Agent
**Purpose**: Provide actionable networking advice and relationship strategy.

**Capabilities**:
- Network gap analysis
- Strategic relationship recommendations
- Opportunity identification
- Introduction pathways
- Follow-up prioritization
- Long-term relationship strategy

**Use Cases**:
- "How can I leverage this connection?"
- "What's my best path to meet [target person]?"
- "Who should I follow up with first?"

### Follow-Up Agent
**Purpose**: Generate intelligent follow-up actions and reminders.

**Capabilities**:
- Context-aware follow-up suggestions
- Timing recommendations (optimal follow-up windows)
- Personalized message drafts
- Action item extraction
- Commitment tracking

**Use Cases**:
- "Generate follow-up emails for everyone I met"
- "What did I promise to do?"
- "When should I reach out to Sarah?"

### Intelligent Router
**Purpose**: Route queries to the most appropriate agent(s) and orchestrate workflows.

**Capabilities**:
- Intent-based routing
- Multi-agent workflow planning
- Execution mode selection (sequential vs parallel)
- Dependency management
- Result synthesis

**Routing Logic**:
- Single-agent queries → Direct routing
- Complex queries → Multi-agent orchestration
- Ambiguous queries → Clarification requests

## Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude | `sk-ant-...` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite+aiosqlite:///./aperta.db` |
| `CHROMA_PERSIST_DIR` | ChromaDB storage directory | `./chroma_db` |
| `CHROMA_COLLECTION_NAME` | ChromaDB collection name | `aperta_documents` |
| `APP_NAME` | Application name | `Aperta` |
| `DEBUG` | Debug mode | `True` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `DEFAULT_AGENT_MODEL` | Claude model to use | `claude-opus-4-6` |
| `MAX_AGENT_TURNS` | Max conversation turns | `10` |
| `ENABLE_PII_DETECTION` | Enable PII detection | `True` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:5173` |

## Development Workflow

### Running Tests

**Backend**:
```bash
cd backend
pytest
pytest --cov=. --cov-report=html  # With coverage
```

**Frontend**:
```bash
cd frontend
npm test
npm run test:coverage
```

### Code Quality

**Backend** (using ruff):
```bash
ruff check .
ruff format .
```

**Frontend** (using ESLint/Prettier):
```bash
npm run lint
npm run format
```

### Database Migrations

Using Alembic:
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Usage Examples

### Example 1: Analyzing a Networking Conversation

```python
import requests

# Upload conversation
response = requests.post(
    "http://localhost:8000/conversations",
    json={
        "title": "Tech Conference 2024",
        "transcript": "Your conversation transcript here...",
        "metadata": {"date": "2024-02-14", "event": "TechCon"}
    }
)
conversation_id = response.json()["id"]

# Ask strategic question
response = requests.post(
    "http://localhost:8000/qa/ask",
    json={
        "question": "Who should I follow up with and what opportunities were discussed?",
        "conversation_id": conversation_id,
        "use_rag": True
    }
)
print(response.json()["answer"])
```

### Example 2: Entity Extraction

```python
# Ask for entity extraction
response = requests.post(
    "http://localhost:8000/qa/ask",
    json={
        "question": "Extract all people, companies, and dates from the conversation",
        "conversation_id": conversation_id
    }
)
```

### Example 3: Privacy Check

```python
# Check for PII
response = requests.post(
    "http://localhost:8000/qa/ask",
    json={
        "question": "Identify any sensitive personal information in this conversation",
        "conversation_id": conversation_id
    }
)
```

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in environment
- [ ] Use production-grade database (PostgreSQL)
- [ ] Set up proper CORS origins
- [ ] Enable rate limiting
- [ ] Configure logging to file/service
- [ ] Set up monitoring (e.g., Sentry)
- [ ] Use environment variable management (e.g., AWS Secrets Manager)
- [ ] Enable HTTPS
- [ ] Set up backup strategy for database
- [ ] Configure CDN for frontend assets

### Deployment Options

**Backend**:
- Render.com (recommended for FastAPI)
- AWS Elastic Beanstalk
- Google Cloud Run
- Heroku
- Railway.app

**Frontend**:
- Vercel
- Netlify
- Cloudflare Pages
- AWS S3 + CloudFront

**Database**:
- Supabase (PostgreSQL)
- PlanetScale (MySQL)
- AWS RDS
- Render PostgreSQL

## Contributing

This is a production-ready codebase. When contributing:

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Use conventional commits (`feat:`, `fix:`, `docs:`, etc.)
5. Ensure all tests pass before submitting

## License

[Specify your license here]

## Support

For questions or issues, please open an issue in the repository or contact the development team.

---

**Built with Claude by Anthropic**
