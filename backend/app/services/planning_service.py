from datetime import datetime, timezone
from ..agents.crisis_assessment import assess
from ..agents.geo_agent import analyze
from ..agents.shelter_agent import allocate as shelter_allocate
from ..agents.medical_agent import allocate as medical_allocate
from ..agents.resource_agent import allocate as resource_allocate
from ..agents.commander import build_plan
from ..models.crisis import CrisisInput
from ..graph.crisis_graph import run_workflow

def generate(crisis, data, version, blocked=False, changes=None):
    assessment = assess(crisis, data)
    run_workflow(crisis.model_dump(mode="json"), assessment.model_dump(), data)
    geo = analyze(data, crisis.location)
    priority_zones = assessment.priority_zones or ["Zone A", "Zone B"]
    shelter = shelter_allocate(data, blocked, priority_zones)
    medical = medical_allocate(data, assessment.severity, crisis.affected_population)
    resource = resource_allocate(data, blocked, priority_zones)
    plan = build_plan(assessment, geo, shelter, medical, resource, version, changes, crisis.location)
    return assessment, geo, shelter, medical, resource, plan

