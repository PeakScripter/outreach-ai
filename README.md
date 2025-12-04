# Outreach-AI

AI-powered outreach platform that turns **live buyer intent signals** into **researched, scored, routed, and fully drafted multi-channel outreach**.

This repo is a small but realistic MVP you can demo or extend.

---

## 1. What This Does

Outreach-AI shows how a modern GTM team could run **autonomous, intent-based outbound**:

- **Capture live signals** (simulated for now):  
  Funding, hiring, leadership changes, pricing-page visits, G2 surges, tech stack changes, competitor churn, keyword spikes.
- **Research accounts & contacts**:  
  Auto-generated company summary, pain points, opportunities, and key decision makers.
- **Score & route**:  
  Lead score, intent level, reasons, next-best action, and routing plan (owner, CRM, SLA).
- **Generate outreach** (all from the same signal):  
  - Email draft  
  - LinkedIn message  
  - Call script  
- **Provide one GTM workspace**:  
  React UI where SDRs/AEs can see signals, agent logs, research, people, outreach drafts, and routing in a single view.

---

## 2. Tech Stack

- **Frontend**
  - React 18 + Vite
  - Tailwind-style utility classes
  - `react-markdown` for nicely formatted drafts

- **Backend**
  - FastAPI
  - LangGraph for multi-agent orchestration
  - `langchain-google-genai` (Gemini 2.5 Flash by default)
  - Simple in-memory stores for run history and CRM events

This is intentionally light: it looks like a real product, but infra like Kafka, Postgres, and real data vendors are simulated.

---

## 3. Project Structure

```text
outreach-ai/
  backend/
    main.py          # FastAPI app & endpoints
    graph.py         # LangGraph agent workflow
    requirements.txt # Python deps

  frontend/
    src/
      App.jsx        # Main UI
      main.jsx       # React entry
      index.css      # Global styles
    package.json     # Frontend deps & scripts
    vite.config.js
    tailwind.config.js
    postcss.config.js
    index.html

  .gitignore
  README.md
```

---

## 4. Backend – Agents & API

### 4.1 Agent Graph (`backend/graph.py`)

Agents share a typed state (`AgentState`) and are orchestrated via LangGraph:

- **Research Agent – `researcher_node`**
  - Input: `company_name`, `signal`
  - Output:
    - `summary`: concise research blurb
    - `pain_points`: list of GTM pains inferred from the signal
    - `opportunities`: list of opportunities
    - `decision_makers`: fake-but-realistic contacts (name, title, email)
    - `sources`: simulated (Crunchbase, LinkedIn, G2)

- **Scoring Agent – `scorer_node`**
  - Looks at the signal and assigns:
    - `score` (0–100)
    - `intent_level` (High/Medium)
    - `reasons` (why we scored it that way)
    - `next_best_action` (e.g., “Trigger AE review”)
    - `confidence`

- **Personalization Agent – `personalization_node`**
  - Builds channel-specific outreach using:
    - The exact **signal**
    - The **company**
    - The **research summary, pains, opportunities**
    - The primary **decision maker** (name + title)
  - Outputs:
    - `email` (80–120 words)
    - `linkedin` (3-sentence message)
    - `call_script` (3-step talk track)
    - `sequence` name
  - Prompts are strict:
    - No `[Company Name]`-style placeholders
    - Must reference the actual signal in the opening
    - Must use the real contact name and role

- **Routing Agent – `routing_node`**
  - Output:
    - `recommended_owner` (e.g., Enterprise Pod / Velocity Pod)
    - `priority` (Hot/Warm)
    - `crm_target` (Salesforce vs HubSpot nurture)
    - `sla_minutes`
    - `playbook` (sequence label)
    - `notes` (short explanation)

- **Supervisor – `supervisor_node`**
  - Simple router: research → score → personalize → route → FINISH.

### 4.2 FastAPI (`backend/main.py`)

Key endpoints:

- `GET /signals`
  - Returns a list of simulated live signals:
    - `company`, `signal`, `category`, `time`, `intent_strength`, `next_step`.

- `POST /process-lead`
  - Body:
    ```json
    { "company": "TechNova Inc", "signal": "Series B Funding - $50M Round" }
    ```
  - Runs the agent graph and returns:
    - `run_id`, `created_at`
    - `score`, `scorecard`
    - `research`
    - `assets` (email, linkedin, call_script, sequence)
    - `routing`
    - `logs`

- `GET /runs`
  - Returns the last 20 agent runs (simple audit log).

- `POST /crm/sync`
  - Simulates sending routing decisions to a CRM:
    ```json
    { "run_id": "TechNova Inc-1234567890", "crm": "Salesforce", "status": "queued", "payload": { ... } }
    ```
  - Stores to an in-memory `CRM_EVENTS` list.

- `GET /crm/events`
  - Returns recent simulated CRM events.

---

## 5. Frontend – GTM Workspace

The React app lives in `frontend/src/App.jsx`. It talks to the FastAPI backend at `http://localhost:8000` (via `API_URL`).

Main pieces:

- **Incoming Signals Sidebar**
  - List of current signals; each card shows:
    - Company name
    - Signal text
    - Time (e.g., “32 mins ago”)
  - Clicking a card (or its “Generate Outreach” button) calls `/process-lead`.

- **System Status Panel**
  - Shows live agent logs:
    - Research started / completed
    - Scoring decisions
    - Outreach generation
    - Routing decisions

- **Metrics Row**
  - Lead score (/100) with color-coded intent.
  - “Recommendation” card with next best action and tags for reasons.

- **Research Card**
  - Narrative research summary.
  - Split columns for **Pain Points** and **Opportunities**.

- **Key Decision Makers**
  - One or more cards with:
    - Name
    - Title
    - “Verified” badge

- **Outreach Drafts (Markdown-rendered)**
  - Tabs for **Email / LinkedIn / Call Script**.
  - Drafts rendered with `react-markdown` so lists, bold, etc. look like real content.
  - **Copy Draft** button copies the currently selected channel to clipboard.

- **Routing Info**
  - Owner, priority, CRM target, and agent note (“Agent Note” box).

Visually, the app looks like a modern B2B SaaS dashboard: clean header, left-hand signal list, right-hand workspace.

---

## 6. Running the Project

### 6.1 Backend

From the project root:

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` in `backend/`:

```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```

Run FastAPI:

```bash
uvicorn main:app --reload --port 8000
```

### 6.2 Frontend

From the project root:

```bash
cd frontend
npm install
npm run dev
```

Open the URL from Vite (usually `http://localhost:5173`).

Make sure the backend is running on `http://localhost:8000`.

---

## 8. Next Ideas / Extensions

- Swap mocked signals for real connectors (G2, Crunchbase, job boards, product telemetry).
- Add Postgres/Redis instead of in-memory lists.
- Add more channels (Slack, in-app messages) to the personalization agent.
- Build a visual **Agent Workflow Builder** on top of the LangGraph graph.

This repo is intentionally small and opinionated so you can quickly understand it, demo it, and then grow it into whatever outbound system you want.


