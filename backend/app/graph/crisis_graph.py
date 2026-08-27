from typing import TypedDict
from ..models.crisis import CrisisInput
from ..agents.crisis_assessment import assess
from ..agents.geo_agent import analyze
from ..agents.shelter_agent import allocate as allocate_shelter
from ..agents.medical_agent import allocate as allocate_medical
from ..agents.resource_agent import allocate as allocate_resource
try:
    from langgraph.graph import StateGraph, START, END
except ImportError:
    StateGraph = None

class CrisisState(TypedDict, total=False):
    crisis: dict
    assessment: dict
    data: dict
    geo: dict
    shelter: dict
    medical: dict
    resource: dict

def build_graph():
    if StateGraph is None: return None
    graph = StateGraph(CrisisState)
    graph.add_node("crisis_assessment", lambda s: {"assessment": assess_from_state(s)})
    graph.add_node("geo", lambda s: {"geo": analyze(s["data"])})
    graph.add_node("shelter", lambda s: {"shelter": allocate_shelter(s["data"])})
    graph.add_node("medical", lambda s: {"medical": allocate_medical(s["data"])})
    graph.add_node("resource", lambda s: {"resource": allocate_resource(s["data"])})
    graph.add_node("commander", lambda s: {"analysis": {"agents_completed": ["crisis_assessment", "geo", "shelter", "medical", "resource"]}})
    graph.add_edge(START, "crisis_assessment"); graph.add_edge("crisis_assessment", "geo"); graph.add_edge("geo", "shelter"); graph.add_edge("shelter", "medical"); graph.add_edge("medical", "resource"); graph.add_edge("resource", "commander"); graph.add_edge("commander", END)
    return graph.compile()

def assess_from_state(state: CrisisState):
    return assess(CrisisInput.model_validate(state["crisis"]), state.get("data", {})).model_dump()

def run_workflow(crisis: dict, assessment: dict, data: dict | None = None) -> dict:
    workflow = build_graph()
    if workflow is None:
        return {"workflow": ["crisis_assessment", "geo", "shelter", "medical", "resource", "commander"]}
    return workflow.invoke({"crisis": crisis, "assessment": assessment, "data": data or {}})
