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
    analysis: dict


def build_graph():
    if StateGraph is None:
        return None

    graph = StateGraph(CrisisState)

    # Crisis Assessment Agent
    graph.add_node(
        "crisis_assessment",
        lambda s: {
            "assessment": assess_from_state(s)
        }
    )

    # Geo Agent
    graph.add_node(
        "geo_agent",
        lambda s: {
            "geo": analyze(s["data"])
        }
    )

    # Shelter Agent
    graph.add_node(
        "shelter_agent",
        lambda s: {
            "shelter": allocate_shelter(s["data"])
        }
    )

    # Medical Agent
    graph.add_node(
        "medical_agent",
        lambda s: {
            "medical": allocate_medical(s["data"])
        }
    )

    # Resource Agent
    graph.add_node(
        "resource_agent",
        lambda s: {
            "resource": allocate_resource(s["data"])
        }
    )

    # Commander Agent
    graph.add_node(
        "commander",
        lambda s: {
            "analysis": {
                "agents_completed": [
                    "crisis_assessment",
                    "geo_agent",
                    "shelter_agent",
                    "medical_agent",
                    "resource_agent"
                ]
            }
        }
    )

    # Workflow
    graph.add_edge(START, "crisis_assessment")
    graph.add_edge("crisis_assessment", "geo_agent")
    graph.add_edge("geo_agent", "shelter_agent")
    graph.add_edge("shelter_agent", "medical_agent")
    graph.add_edge("medical_agent", "resource_agent")
    graph.add_edge("resource_agent", "commander")
    graph.add_edge("commander", END)

    return graph.compile()


def assess_from_state(state: CrisisState):
    return assess(
        CrisisInput.model_validate(state["crisis"]),
        state.get("data", {})
    ).model_dump()


def run_workflow(
    crisis: dict,
    assessment: dict,
    data: dict | None = None
) -> dict:

    workflow = build_graph()

    if workflow is None:
        return {
            "workflow": [
                "crisis_assessment",
                "geo_agent",
                "shelter_agent",
                "medical_agent",
                "resource_agent",
                "commander"
            ]
        }

    return workflow.invoke(
        {
            "crisis": crisis,
            "assessment": assessment,
            "data": data or {}
        }
    )