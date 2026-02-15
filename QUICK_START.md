# Aperta - Quick Start Guide

Get Aperta up and running in 5 minutes.

## Prerequisites

- Python 3.11+ installed
- Node.js 18+ and npm installed
- Anthropic API key (get from https://console.anthropic.com/)

## Step 1: Backend Setup (2 minutes)

```bash
# Navigate to backend
cd /Users/apurvgude/Desktop/Data\ Science\ /NetworkAI/Aperta/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

```

## Step 2: Frontend Setup (2 minutes)

```bash
# Open a new terminal
cd /Users/apurvgude/Desktop/Data\ Science\ /NetworkAI/Aperta/frontend

# Install dependencies
npm install
```

## Step 3: Start Both Servers (1 minute)

**Terminal 1 - Backend:**
```bash
cd /Users/apurvgude/Desktop/Data\ Science\ /NetworkAI/Aperta/backend
source venv/bin/activate
python main.py
```
Backend will run on: http://localhost:8000  
API Docs: http://localhost:8000/docs

**Terminal 2 - Frontend:**
```bash
cd /Users/apurvgude/Desktop/Data\ Science\ /NetworkAI/Aperta/frontend
npm run dev
```
Frontend will run on: http://localhost:5173

## Step 4: Use the Application

1. Open http://localhost:5173 in your browser
2. Go to "Conversations" page
3. Click "New Conversation"
4. Enter a title and paste a conversation transcript
5. Save the conversation
6. Go to "Ask Questions" page
7. Enter your conversation ID and ask a question
8. Watch the AI agents analyze and respond!

## Example Questions to Ask

- "Who are the key people mentioned in this conversation?"
- "What networking opportunities were discussed?"
- "Generate follow-up action items for this conversation"
- "Analyze the sentiment and context of this discussion"
- "Are there any privacy concerns in this transcript?"
- "What strategic networking advice can you provide?"

## Troubleshooting

**Backend won't start:**
- Check if .env file exists with ANTHROPIC_API_KEY
- Verify Python 3.11+ is installed: `python --version`
- Check if port 8000 is available

**Frontend won't start:**
- Verify Node.js 18+ is installed: `node --version`
- Delete node_modules and package-lock.json, then run `npm install` again
- Check if port 5173 is available

**API key error:**
- Verify your Anthropic API key is correct
- Check if there are any spaces in the .env file
- Ensure the key starts with 'sk-ant-'

## API Documentation

Visit http://localhost:8000/docs for interactive API documentation (Swagger UI).

## Project Structure

```
Aperta/
├── backend/          # Python FastAPI backend
│   ├── agents/       # AI agents (8 agents)
│   ├── tools/        # Agent tools (4 tools)
│   ├── api/          # API routes
│   ├── db/           # Database models
│   └── main.py       # Entry point
│
├── frontend/         # React TypeScript frontend
│   └── src/
│       ├── pages/    # 4 pages
│       └── components/ # 2 components
│
├── README.md         # Full documentation
└── PROJECT_STRUCTURE.md  # Detailed structure
```

## What's Next?

- Read the full README.md for detailed documentation
- Check PROJECT_STRUCTURE.md for architecture details
- Read COMPLETION_REPORT.md for feature overview
- Explore the code and agents
- Deploy to production (Render.com for backend, Vercel for frontend)

## Support

For issues or questions, refer to:
- README.md - Comprehensive documentation
- PROJECT_STRUCTURE.md - Architecture details
- COMPLETION_REPORT.md - Feature inventory

---

**Built with Claude by Anthropic**
