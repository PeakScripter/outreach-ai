import os
import random
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
# Replace with 'gpt-4o' if you prefer OpenAI, but Gemini is faster/free-tier friendly
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.2
)

# --- STATE DEFINITION ---
class AgentState(TypedDict):
    company_name: str
    signal: str  # e.g., "Series B Funding"
    research_data: Dict[str, Any]
    score: int
    scorecard: Dict[str, Any]
    personalized_assets: Dict[str, str]
    routing_plan: Dict[str, Any]
    logs: List[str]  # To show live progress on Frontend
    next_step: str

# --- AGENT NODES ---

def _derive_key_contacts(company: str) -> List[Dict[str, str]]:
    titles = [
        "VP of Revenue",
        "Head of Demand Gen",
        "Director of Sales Ops",
        "Chief Growth Officer",
        "VP of Sales"
    ]
    domains = company.replace(" ", "").lower()
    contacts = []
    for title in random.sample(titles, 2):
        first = title.split()[0]
        email = f"{first.lower()}@{domains}.com"
        contacts.append({"name": f"{first} {company.split()[0]}", "title": title, "email": email})
    return contacts


def _pain_and_opportunity_from_signal(signal: str) -> Dict[str, List[str]]:
    if "Funding" in signal:
        return {
            "pain_points": ["Need to scale GTM headcount efficiently", "Pressure to show ROI on new capital"],
            "opportunities": ["Position outbound playbooks for fast growth", "Offer onboarding for new sales hires"]
        }
    if "Hiring" in signal:
        return {
            "pain_points": ["Manual sourcing slowing recruiting", "Unclear messaging for new markets"],
            "opportunities": ["Share candidate intent data", "Bundle outreach cadences for open roles"]
        }
    if "Website" in signal or "Pricing" in signal:
        return {
            "pain_points": ["High bounce rate on pricing page", "Unknown ICP visitors"],
            "opportunities": ["Serve targeted experiences", "Offer conversational capture to convert traffic"]
        }
    return {
        "pain_points": ["Fragmented revops tooling", "No unified intent signals"],
        "opportunities": ["Deploy live buyer intelligence", "Automate research and routing"]
    }


def researcher_node(state: AgentState):
    """
    Simulates researching the company. 
    """
    company = state["company_name"]
    signal = state["signal"]

    print(f"🕵️ RESEARCHER: Looking up {company}...")
    insights = _pain_and_opportunity_from_signal(signal)

    prompt = f"""
    You are an elite GTM research analyst. Summarize {company} reacting to the signal "{signal}".
    Provide a crisp paragraph highlighting why now is a good time for outbound outreach.
    """
    response = llm.invoke(prompt)

    research_data = {
        "summary": response.content.strip(),
        "pain_points": insights["pain_points"],
        "opportunities": insights["opportunities"],
        "decision_makers": _derive_key_contacts(company),
        "sources": ["Crunchbase", "LinkedIn", "G2 (simulated)"]
    }

    key_contact = research_data["decision_makers"][0]["name"]
    new_logs = state["logs"] + [f"🕵️ Research: Found data on {company}. Key contact: {key_contact}"]
    return {"research_data": research_data, "logs": new_logs}

def scorer_node(state: AgentState):
    """
    Scores the lead based on the signal and research.
    """
    print(f"⚖️ SCORER: Evaluating...")
    signal = state["signal"]

    score = 55
    intent_level = "Medium Intent"
    reasons = ["Active digital footprint"]

    if "Funding" in signal:
        score = 92
        intent_level = "High Intent"
        reasons = ["Fresh capital", "Likely tool consolidation"]
    elif "Hiring" in signal:
        score = 82
        intent_level = "High Intent"
        reasons = ["Team expansion underway"]
    elif "Website" in signal or "Pricing" in signal:
        score = 68
        reasons = ["Evaluating solutions", "Pricing page visits"]

    scorecard = {
        "score": score,
        "intent_level": intent_level,
        "reasons": reasons,
        "next_best_action": "Trigger AE review" if score > 80 else "Drop into SDR fast lane",
        "confidence": random.choice(["High", "Medium"])
    }

    new_logs = state["logs"] + [f"⚖️ Scoring: Lead Score {score}/100. Intent: {intent_level}"]
    return {"score": score, "scorecard": scorecard, "logs": new_logs}

def personalization_node(state: AgentState):
    """
    Generates multi-channel outreach using the LLM.
    """
    print("✍️ PERSONALIZER: Drafting assets...")

    if state["score"] < 30:
        message = "Lead too cold — recycle in 30 days."
        new_logs = state["logs"] + ["⛔ Outreach: Skipped (Very Low Score)"]
        return {"personalized_assets": {"email": message, "linkedin": message, "call_script": message}, "logs": new_logs}

    signal = state["signal"]
    company = state["company_name"]
    research_summary = state["research_data"]["summary"]
    pain_points = state["research_data"].get("pain_points", [])
    opportunities = state["research_data"].get("opportunities", [])
    primary_contact = state["research_data"]["decision_makers"][0]
    contact_name = primary_contact["name"]
    contact_title = primary_contact["title"]

    email_prompt = f"""
    You are a senior outbound copywriter.
    Write a highly intent-specific cold email to {contact_name}, {contact_title} at {company}.

    - DO NOT use placeholders like [Company Name] or [VP's Name]; always use the concrete values: company={company}, contact={contact_name}.
    - The triggering intent signal was: "{signal}".
    - Research summary: {research_summary}
    - Key pain points: {", ".join(pain_points) if pain_points else "n/a"}
    - Key opportunities: {", ".join(opportunities) if opportunities else "n/a"}

    Requirements:
    - 80–120 words
    - First 1–2 sentences must clearly tie the outreach to the specific signal (not a generic congratulations).
    - Make 1–2 sharp observations that could only be true because of this signal + pains above.
    - End with a specific question that tests interest or timing.
    """

    linkedin_prompt = f"""
    You are writing a LinkedIn message to {contact_name}, {contact_title} at {company}.
    The conversation is triggered by this live signal: "{signal}".
    Research summary: {research_summary}
    Pain points: {", ".join(pain_points) if pain_points else "n/a"}

    Write 3 short sentences:
    - Sentence 1: reference the signal in plain language.
    - Sentence 2: connect one pain point to a potential outcome they care about.
    - Sentence 3: a soft CTA asking if it's worth comparing approaches.
    Do NOT use any bracket-style placeholders; use the real company and role.
    """

    call_prompt = f"""
    You are coaching an SDR on how to call {contact_name}, {contact_title} at {company}.
    This call is triggered by the signal: "{signal}".
    Research summary: {research_summary}
    Pain points: {", ".join(pain_points) if pain_points else "n/a"}.

    Create a 3-step talk track:
    1) Opening hook that references the signal in the first sentence.
    2) 1–2 discovery questions that prove you understand their situation from the research.
    3) Close that proposes a next step if the signal is indeed a priority.
    Format the answer as three numbered steps with 1–2 bullet points under each.
    Do NOT use generic placeholders like [Company Name] or [Prospect Name].
    """

    email = llm.invoke(email_prompt).content.strip()
    linkedin = llm.invoke(linkedin_prompt).content.strip()
    call_script = llm.invoke(call_prompt).content.strip()

    assets = {
        "email": email,
        "linkedin": linkedin,
        "call_script": call_script,
        "sequence": "Momentum Blitz (3-touch / 5 days)"
    }

    new_logs = state["logs"] + ["✅ Outreach: Multi-channel assets drafted."]
    return {"personalized_assets": assets, "logs": new_logs}


def routing_node(state: AgentState):
    """
    Decides routing / CRM sync recommendations.
    """
    print("🧭 ROUTING: Assigning owner...")
    score = state["score"]
    owner = "Enterprise Pod" if score > 80 else "Velocity Pod"
    crm_target = "Salesforce" if score > 60 else "HubSpot Nurture"

    routing_plan = {
        "recommended_owner": owner,
        "priority": "Hot" if score > 80 else "Warm",
        "crm_target": crm_target,
        "sla_minutes": 30 if score > 80 else 240,
        "playbook": state.get("personalized_assets", {}).get("sequence", "Standard Follow-up"),
        "notes": "Push to AE + create task" if score > 80 else "Add to SDR queue"
    }

    new_logs = state["logs"] + [f"📬 Routing: Sent to {owner}. CRM: {crm_target}"]
    return {"routing_plan": routing_plan, "logs": new_logs}

def supervisor_node(state: AgentState):
    """
    The Boss. Decides who works next.
    """
    if not state.get("research_data"):
        return {"next_step": "researcher"}
    if state.get("score") is None:
        return {"next_step": "scorer"}
    if not state.get("personalized_assets"):
        return {"next_step": "personalizer"}
    if not state.get("routing_plan"):
        return {"next_step": "routing"}
    return {"next_step": "FINISH"}

# --- GRAPH BUILDER ---
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("researcher", researcher_node)
workflow.add_node("scorer", scorer_node)
workflow.add_node("personalizer", personalization_node)
workflow.add_node("routing", routing_node)

# Add Edges (Everyone reports back to Supervisor)
workflow.add_edge("researcher", "supervisor")
workflow.add_edge("scorer", "supervisor")
workflow.add_edge("personalizer", "supervisor")
workflow.add_edge("routing", "supervisor")

# Conditional Routing
workflow.set_entry_point("supervisor")
workflow.add_conditional_edges(
    "supervisor",
    lambda x: x["next_step"],
    {
        "researcher": "researcher",
        "scorer": "scorer",
        "personalizer": "personalizer",
        "routing": "routing",
        "FINISH": END
    }
)

app_graph = workflow.compile()