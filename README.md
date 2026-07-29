# AI Course-Builder (v1 Prototype)

Import plain text learning material (title + text) and let AI decide how it fits into your
courses — create a new course, extend an existing one, or add a single new concept — then
organize it into a Course → Module → Concept structure automatically. See
`/root/.claude/plans/project-ai-course-builder-whimsical-lampson.md` (or ask Claude) for the
full design writeup: the AI decision pipeline, course schema, and trade-offs.

## Stack

- **Backend**: Python, FastAPI, SQLite (SQLAlchemy), local `sentence-transformers` embeddings
  for candidate retrieval, Anthropic Claude API (structured outputs) for classification +
  content synthesis.
- **Frontend**: React + Vite SPA.

## Running locally

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in ANTHROPIC_API_KEY
uvicorn app.main:app --reload
```

API docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Opens at `http://localhost:5173`, proxying `/api/*` to the backend on port 8000.
