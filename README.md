# 💰 Financial Document Analyzer

A production-ready AI-powered financial document analysis system built with **CrewAI**, **FastAPI**, **Redis**, **Celery**, and **SQLite**. Upload any financial PDF and get comprehensive investment insights, risk assessments, and recommendations from a team of specialized AI agents.

---

## 🚀 Features

- 📄 **PDF Upload & Analysis** — Upload any financial PDF via REST API
- 🤖 **Multi-Agent AI Pipeline** — 4 specialized CrewAI agents collaborate on analysis
- ⚡ **Async Job Queue** — Redis + Celery handles concurrent requests without blocking
- 🗄️ **Database Persistence** — SQLite stores all jobs, results, and history
- 📊 **Job Status Tracking** — Real-time status updates (pending → processing → completed)
- 🔍 **Web Search Integration** — Agents fetch live market data via SerperDev
- 🧹 **Auto File Cleanup** — Uploaded PDFs deleted after processing

---

## 🏗️ Architecture

```
User uploads PDF
      ↓
FastAPI → saves job to SQLite → returns job_id instantly
      ↓
Redis Queue → stores task
      ↓
Celery Worker → runs CrewAI agents → saves result to SQLite
      ↓
User polls /status/{job_id} → gets completed analysis
```

---

## 🤖 AI Agents

| Agent | Role | Responsibility |
|-------|------|----------------|
| `financial_analyst` | Senior Financial Analyst | Reads PDF and extracts financial insights |
| `verifier` | Financial Document Verifier | Verifies document is a valid financial report |
| `investment_advisor` | Certified Investment Advisor | Provides investment recommendations |
| `risk_assessor` | Risk Assessment Specialist | Conducts balanced risk analysis using VaR, Sharpe Ratio |

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| [CrewAI](https://crewai.com) | Multi-agent AI framework |
| [FastAPI](https://fastapi.tiangolo.com) | REST API server |
| [Celery](https://docs.celeryq.dev) | Distributed task queue |
| [Redis](https://redis.io) | Message broker |
| [SQLite + SQLAlchemy](https://www.sqlalchemy.org) | Database |
| [Groq LLM](https://groq.com) | LLM provider (llama-3.3-70b-versatile) |
| [LangChain Community](https://python.langchain.com) | PDF loading |
| [SerperDev](https://serper.dev) | Web search tool |

---

## 📁 Project Structure

```
financial-document-analyzer/
├── .env                    ← API keys
├── main.py                 ← FastAPI server + endpoints
├── agents.py               ← 4 AI agent definitions
├── task.py                 ← 4 analysis task definitions
├── tools.py                ← 3 BaseTool classes
├── celery_worker.py        ← Celery task configuration
├── database.py             ← SQLite database models
├── requirements.txt        ← Python dependencies
└── data/                   ← Temporary PDF storage (auto-created)
```

---

## ⚙️ Installation

### Prerequisites
- Python 3.11+
- WSL2 with Ubuntu (for Redis on Windows)
- Node.js (optional, for docs generation)

### Step 1 — Clone the Repository
```bash
git clone https://github.com/yourusername/financial-document-analyzer.git
cd financial-document-analyzer
```

### Step 2 — Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate        # Linux/Mac/WSL
# OR
.\venv\Scripts\activate         # Windows
```

### Step 3 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Install Redis (Windows users)
```bash
# Open WSL2/Ubuntu terminal
sudo apt update
sudo apt install redis-server -y
sudo service redis-server start

# Test Redis
redis-cli ping  # Should return PONG
```

### Step 5 — Set Up Environment Variables
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx       # Optional if using Groq
GROQ_API_KEY=gsk-xxxxxxxxxxxxxxxx        # Free at console.groq.com
SERPER_API_KEY=xxxxxxxxxxxxxxxx          # Free at serper.dev
```

---

## ▶️ Running the Application

You need **3 terminals** open simultaneously:

**Terminal 1 — Start Redis (WSL/Ubuntu):**
```bash
sudo service redis-server start
```

**Terminal 2 — Start Celery Worker:**
```bash
source venv/bin/activate
celery -A celery_worker worker --loglevel=info --concurrency=2
```

**Terminal 3 — Start FastAPI Server:**
```bash
source venv/bin/activate
python3 main.py
```

The API will be available at:
```
http://localhost:8000
http://localhost:8000/docs   ← Interactive API documentation
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/analyze` | Upload PDF for analysis |
| `GET` | `/status/{job_id}` | Check job status and get result |
| `GET` | `/history` | View all past analysis jobs |
| `DELETE` | `/job/{job_id}` | Delete a specific job |

### Example Usage

**Upload a PDF:**
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@financial_report.pdf" \
  -F "query=Analyze this document for investment insights"
```

**Response:**
```json
{
  "status": "queued",
  "job_id": "abc123-...",
  "message": "Analysis started! Use /status/{job_id} to check progress."
}
```

**Check Status:**
```bash
curl "http://localhost:8000/status/abc123-..."
```

**Response when completed:**
```json
{
  "job_id": "abc123-...",
  "status": "completed",
  "query": "Analyze this document for investment insights",
  "filename": "financial_report.pdf",
  "analysis": "## Financial Analysis Report\n..."
}
```

---

## 🔧 Configuration

### Changing the LLM Model
In `agents.py`:
```python
llm = LLM(
    model="groq/llama-3.3-70b-versatile",  # Groq (free)
    # model="gpt-4o-mini",                  # OpenAI (paid)
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7
)
```

### Adjusting Document Size Limit
In `tools.py`:
```python
# Increase for better coverage (may hit rate limits)
if len(full_report) > 5000:
    full_report = full_report[:5000] + "[Document truncated...]"
```

### Adjusting Concurrency
In `celery_worker.py`:
```python
celery_app.conf.update(
    worker_concurrency=2,  # increase for more parallel jobs
)
```

---

## 📦 Requirements

```
fastapi
uvicorn
crewai==0.130.0
crewai-tools
langchain-community
celery
redis
sqlalchemy
python-dotenv
python-multipart
pypdf
groq
litellm
```

---

## ⚠️ Known Limitations

- **Groq Free Tier** — Limited to ~6,000 tokens/minute. Large PDFs are truncated to 5,000 characters.
- **Rate Limits** — Concurrent jobs may hit Groq rate limits. A 3-second delay is added between jobs.
- **Redis on Windows** — Requires WSL2/Ubuntu. Redis does not have native Windows support.
- **Model Compatibility** — `allow_delegation=False` required for Groq models to avoid tool_use_failed errors.

---

## 🐛 Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `ValidationError: Input should be BaseTool` | Tool not wrapped properly | Use `BaseTool` subclass in `tools.py` |
| `OpenAIError: api_key must be set` | Missing API key | Check `.env` file exists and has correct keys |
| `429 Too Many Requests` | Rate limit exceeded | Wait 60 seconds and retry |
| `413 Payload Too Large` | PDF too large | Reduce truncation limit in `tools.py` |
| `tool_use_failed` | Groq + delegation conflict | Set `allow_delegation=False` in all agents |
| `redis-cli not found` | Redis not in PATH | Use WSL2 Ubuntu terminal |

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgements

- [CrewAI](https://crewai.com) — Multi-agent framework
- [Groq](https://groq.com) — Fast, free LLM inference
- [SerperDev](https://serper.dev) — Google Search API
- [FastAPI](https://fastapi.tiangolo.com) — Modern Python web framework
