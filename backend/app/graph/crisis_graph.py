from typing import TypedDict
try:
    from langgraph.graph import StateGraph, START, END
except ImportError:
    StateGraph = None

class CrisisState(TypedDict, total=False):
    crisis: dict
    assessment: dict
    analysis: dict

def build_graph():
    if StateGraph is None: return None
    graph = StateGraph(CrisisState)
    graph.add_node("crisis_assessment", lambda s: s)
    graph.add_node("commander", lambda s: s)
    graph.add_edge(START, "crisis_assessment"); graph.add_edge("crisis_assessment", "commander"); graph.add_edge("commander", END)
    return graph.compile()

def run_workflow(crisis: dict, assessment: dict) -> dict:
    workflow = build_graph()
    if workflow is None:
        return {"workflow": ["crisis_assessment", "commander"]}
    return workflow.invoke({"crisis": crisis, "assessment": assessment, "analysis": {}})
