from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from graph import app_graph
from datetime import datetime
from typing import List, Dict, Any
import random

app = FastAPI()

# Enable CORS for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000","https://outreach-ai-theta.vercel.app"],
    allow_origin_regex=r"^https?://localhost:\d{4}$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- In-memory "DB" for demo ---
RUN_HISTORY: List[Dict[str, Any]] = []
CRM_EVENTS: List[Dict[str, Any]] = []


INTENT_SIGNALS = [
    ("TechNova Inc", "Series B Funding - $50M Round", "Funding"),
    ("GreenEnergy Systems", "Hiring: VP of Sales & RevOps", "Hiring"),
    ("RetailKing", "Visited Pricing Page 5x / 48h", "Website"),
    ("FinSight AI", "G2 Category Surge: Sales Intelligence", "G2"),
    ("HealthLoop", "Leadership Change: New COO Announced", "Leadership"),
    ("OmniStack", "Competitor Churn: Replacing Outreach", "Churn"),
    ("Voyage Robotics", "Keyword Spike: 'pipeline automation'", "Keyword"),
    ("LumenData", "Tech Stack Update: Added HubSpot Enterprise", "Tech Stack")
]


def generate_mock_signals():
    now = datetime.utcnow()
    feed = []
    for idx, (company, message, category) in enumerate(INTENT_SIGNALS, start=1):
        minutes_ago = random.randint(2, 180)
        feed.append(
            {
                "id": idx,
                "company": company,
                "signal": message,
                "category": category,
                "time": f"{minutes_ago} mins ago",
                "intent_strength": "High" if category in ["Funding", "Hiring", "Churn"] else "Medium",
                "next_step": "Review in Agent Console"
            }
        )
    return feed


MOCK_SIGNALS = generate_mock_signals()


class ProcessRequest(BaseModel):
    company: str
    signal: str


class CRMEvent(BaseModel):
    run_id: str
    crm: str
    status: str
    payload: Dict[str, Any] = {}

@app.get("/signals")
def get_signals():
    """Returns the dashboard feed data."""
    return generate_mock_signals()


@app.get("/runs")
def list_runs():
    """
    Returns recent agent runs for audit.
    """
    # Return last 20 runs, newest first
    return list(reversed(RUN_HISTORY[-20:]))


@app.get("/crm/events")
def list_crm_events():
    """
    Returns simulated CRM sync events.
    """
    return list(reversed(CRM_EVENTS[-50:]))

@app.post("/process-lead")
async def process_lead(request: ProcessRequest):
    """
    Trigger the Multi-Agent System for a specific lead.
    """
    run_id = f"{request.company}-{int(datetime.utcnow().timestamp())}"

    initial_state = {
        "company_name": request.company,
        "signal": request.signal,
        "research_data": {},
        "score": None,
        "scorecard": {},
        "personalized_assets": {},
        "routing_plan": {},
        "logs": ["🚀 System: Workflow initialized..."]
    }
    
    # Run the graph
    final_state = app_graph.invoke(initial_state)

    enriched = {
        "run_id": run_id,
        "created_at": datetime.utcnow().isoformat(),
        "company": request.company,
        "signal": request.signal,
        "logs": final_state["logs"],
        "score": final_state["score"],
        "scorecard": final_state.get("scorecard", {}),
        "research": final_state["research_data"],
        "assets": final_state.get("personalized_assets", {}),
        "routing": final_state.get("routing_plan", {})
    }

    # Persist in-memory for demo
    RUN_HISTORY.append(enriched)
    
    return enriched


@app.post("/crm/sync")
async def crm_sync(event: CRMEvent):
    """
    Simulates a CRM sync endpoint where a routing decision is pushed into Salesforce/HubSpot.
    In a real system, this would call external APIs.
    """
    stored = {
        "run_id": event.run_id,
        "crm": event.crm,
        "status": event.status,
        "payload": event.payload,
        "received_at": datetime.utcnow().isoformat()
    }
    CRM_EVENTS.append(stored)
    return {"ok": True, "stored": stored}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)