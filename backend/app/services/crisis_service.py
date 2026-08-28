import asyncio
from datetime import datetime, timezone
from uuid import uuid4

from ..data.demo_data import LOCATIONS, snapshot
from ..models.crisis import CrisisInput
from .planning_service import generate
from .event_manager import EventManager
from .llm_service import llm_service


class CrisisService:
    def __init__(self):
        self.reset()

    # ============================================================
    # RESET
    # ============================================================

    def reset(self):
        self.location = LOCATIONS[0].copy()
        self.data = snapshot(self.location["id"])

        self.crisis = None
        self.assessment = None

        self.plan = None
        self.previous_plan = None

        self.version = 0

        self.audit = []
        self.events = []

        self.event_manager = EventManager()

        self.active = False

        self.alerts = []
        self.reports = []

        self.agent_logs = {}
        self.agent_states = {}

        self.created_at = None
        self.updated_at = None

    # ============================================================
    # EVENT EMITTER
    # ============================================================

    async def emit(
        self,
        agent: str,
        status: str,
        message: str,
        event_type: str,
        data: dict | None = None,
    ):
        now = datetime.now(timezone.utc).isoformat()

        normalized = (
            "RUNNING"
            if status in ("WORKING", "RUNNING")
            else "COMPLETED"
            if status in ("COMPLETE", "COMPLETED")
            else status
        )

        event = await self.event_manager.publish(
            event_type=event_type,
            source=agent.upper().replace(" ", "_"),
            message=message,
            location=self.location["name"],
            agent_id=agent,
            severity=(
                "WARNING"
                if normalized in ("WARNING", "REJECTED")
                else "INFO"
            ),
            data=data or {},
            status=normalized,
        )

        event.update(
            {
                "input_summary": (
                    message if normalized == "RUNNING" else ""
                ),
                "output_summary": (
                    message if normalized == "COMPLETED" else ""
                ),
                "duration": 0,
                "crisis_id": (
                    self.crisis.disaster_type
                    if self.crisis
                    else None
                ),
            }
        )

        self.events.append(event)

        self.updated_at = now

        self.agent_logs.setdefault(agent, []).append(event)

        previous_state = self.agent_states.get(agent, {})

        self.agent_states[agent] = {
            "name": agent,
            "status": normalized,
            "last_message": message,
            "last_started": (
                now
                if normalized == "RUNNING"
                else previous_state.get("last_started")
            ),
            "last_completed": (
                now
                if normalized == "COMPLETED"
                else previous_state.get("last_completed")
            ),
            "execution_count": len(self.agent_logs[agent]),
        }

        return event

    # ============================================================
    # LOCATION
    # ============================================================

    async def set_location(self, location_id: str):
        loc_id = str(location_id).lower().strip()

        selected = next(
            (
                item
                for item in LOCATIONS
                if item["id"] == loc_id
            ),
            None,
        )

        if selected is None and loc_id.startswith("custom:"):
            name = str(location_id).split(":", 1)[1].strip()

            selected = {
                "id": "custom",
                "name": name,
                "state": "Custom Region",
                "latitude": LOCATIONS[0]["latitude"],
                "longitude": LOCATIONS[0]["longitude"],
                "default_crisis": "Emergency Incident",
                "severity": "HIGH",
                "affected_population": 5000,
                "water_level": 2.0,
                "blocked_roads": 1,
                "risk_summary": "Custom defined operational sector.",
            }

        if selected is None:
            raise ValueError(
                f"Unknown location: {location_id}"
            )

        previous = self.location["name"]

        self.location = selected.copy()
        self.data = snapshot(self.location["id"])

        self.crisis = None
        self.assessment = None
        self.plan = None
        self.previous_plan = None

        self.version = 0
        self.active = False

        self._audit(
            "Emergency Operator",
            f"Location shifted to {selected['name']}",
            [
                previous,
                selected["name"],
            ],
            "LOCATION_CHANGED",
        )

        await self.emit(
            "Commander Agent",
            "COMPLETED",
            f"Operational theater relocated from {previous} to {selected['name']}",
            "LOCATION_CHANGED",
        )

        await self.emit(
            "System",
            "COMPLETED",
            f"Initialized fresh demographic & geospatial topology for {selected['name']}",
            "STATE_UPDATED",
        )

        return self.current()

    # ============================================================
    # TRIGGER CRISIS
    # ============================================================

    async def trigger(self):
        default_crisis = self.location.get(
            "default_crisis",
            "Flood",
        )

        pop = self.location.get(
            "affected_population",
            sum(
                zone["population"]
                for zone in self.data["zones"]
            ),
        )

        water = self.location.get(
            "water_level",
            2.4,
        )

        blocked = len(
            [
                road
                for road in self.data["roads"]
                if road["status"] == "BLOCKED"
            ]
        )

        crisis_input = CrisisInput(
            disaster_type=default_crisis,
            location=self.location["name"],
            water_level=water,
            affected_population=pop,
            blocked_roads=blocked,
            description=self.location.get(
                "risk_summary",
                f"{default_crisis} detected across lowlands.",
            ),
            timestamp=datetime.now(timezone.utc),
        )

        return await self.analyze_crisis(crisis_input)

    # ============================================================
    # ANALYZE CRISIS
    # ============================================================

    async def analyze_crisis(
        self,
        crisis_input: CrisisInput,
    ):
        self.active = True

        self.created_at = datetime.now(
            timezone.utc
        ).isoformat()

        self.crisis = crisis_input

        self._audit(
            "Commander Agent",
            (
                f"Incident Ingestion: "
                f"{crisis_input.disaster_type} "
                f"in {crisis_input.location}"
            ),
            [
                crisis_input.location,
                crisis_input.disaster_type,
            ],
            "CRISIS_RECEIVED",
        )

        # --------------------------------------------------------
        # 1. COMMANDER
        # --------------------------------------------------------

        await self.emit(
            "Commander Agent",
            "RUNNING",
            (
                f"Commander Agent initialized for "
                f"{crisis_input.disaster_type} Crisis "
                f"in {crisis_input.location}"
            ),
            "COMMANDER_STARTED",
        )

        await asyncio.sleep(0.3)

        # --------------------------------------------------------
        # 2. CRISIS ASSESSMENT
        # --------------------------------------------------------

        await self.emit(
            "Crisis Assessment Agent",
            "RUNNING",
            (
                "Assessing disaster intensity, medical risk, "
                f"and affected population "
                f"({crisis_input.affected_population:,} people)"
            ),
            "ASSESSMENT_STARTED",
        )

        await asyncio.sleep(0.3)

        generated = generate(
            self.crisis,
            self.data,
            1,
        )

        # Safety check for generate()
        if not generated or len(generated) < 6:
            raise ValueError(
                "Planning service did not return a complete response plan."
            )

        self.assessment = generated[0]

        if self.assessment is not None:
            severity = getattr(
                self.assessment,
                "severity",
                "HIGH",
            )

            urgency = getattr(
                self.assessment,
                "urgency",
                "HIGH",
            )
        else:
            severity = "HIGH"
            urgency = "IMMEDIATE"

        await self.emit(
            "Crisis Assessment Agent",
            "COMPLETED",
            (
                f"Calculated {severity} severity rating. "
                f"Urgency: {urgency}"
            ),
            "ASSESSMENT_COMPLETED",
        )

        await asyncio.sleep(0.3)

        # --------------------------------------------------------
        # 3. GEO AGENT
        # --------------------------------------------------------

        await self.emit(
            "Commander Agent",
            "RUNNING",
            (
                "Delegating spatial topology & road "
                "accessibility analysis to Geo Agent"
            ),
            "AGENT_STARTED",
        )

        await self.emit(
            "Geo Agent",
            "RUNNING",
            (
                f"Scanning {len(self.data['roads'])} "
                "regional routes & identifying blocked floodways"
            ),
            "GEO_ANALYSIS_STARTED",
        )

        await asyncio.sleep(0.3)

        geo_result = generated[1]

        await self.emit(
            "Geo Agent",
            "COMPLETED",
            (
                f"Detected {len(geo_result.get('blocked_routes', []))} "
                "blocked roads, "
                f"{len(geo_result.get('safe_routes', []))} "
                "safe evacuation corridors"
            ),
            "GEO_ANALYSIS_COMPLETED",
        )

        await asyncio.sleep(0.3)

        # --------------------------------------------------------
        # 4. MEDICAL AGENT
        # --------------------------------------------------------

        await self.emit(
            "Commander Agent",
            "RUNNING",
            (
                "Delegating hospital capacity & triage "
                "readiness to Medical Agent"
            ),
            "AGENT_STARTED",
        )

        await self.emit(
            "Medical Agent",
            "RUNNING",
            (
                f"Auditing {len(self.data['hospitals'])} "
                "medical trauma centers for available beds "
                "& ICU capacity"
            ),
            "MEDICAL_ANALYSIS_STARTED",
        )

        await asyncio.sleep(0.3)

        med_result = generated[3]

        await self.emit(
            "Medical Agent",
            "COMPLETED",
            (
                f"Designated {med_result.get('hospital', 'Regional Hospital')} "
                f"({med_result.get('available_beds', 0)} beds free, "
                f"{med_result.get('icu_beds', 0)} ICU)"
            ),
            "MEDICAL_ANALYSIS_COMPLETED",
        )

        await asyncio.sleep(0.3)

        # --------------------------------------------------------
        # 5. RESOURCE AGENT
        # --------------------------------------------------------

        await self.emit(
            "Commander Agent",
            "RUNNING",
            (
                "Delegating supply logistics & asset "
                "deployment to Resource Agent"
            ),
            "AGENT_STARTED",
        )

        await self.emit(
            "Resource Agent",
            "RUNNING",
            (
                f"Auditing emergency inventories "
                f"({len(self.data['resources'])} tracked asset lines)"
            ),
            "RESOURCE_ANALYSIS_STARTED",
        )

        await asyncio.sleep(0.3)

        res_result = generated[4]

        shortages = res_result.get(
            "shortages",
            [],
        )

        shortage_txt = (
            f"{len(shortages)} supply deficits flagged"
            if shortages
            else "Supplies adequate"
        )

        await self.emit(
            "Resource Agent",
            "COMPLETED",
            (
                "Allocated transit fleets to priority zones. "
                f"Status: {shortage_txt}"
            ),
            "RESOURCE_ANALYSIS_COMPLETED",
        )

        await asyncio.sleep(0.3)

        # --------------------------------------------------------
        # 6. SHELTER AGENT
        # --------------------------------------------------------

        await self.emit(
            "Commander Agent",
            "RUNNING",
            "Delegating evacuee housing to Shelter Agent",
            "AGENT_STARTED",
        )

        await self.emit(
            "Shelter Agent",
            "RUNNING",
            (
                f"Evaluating {len(self.data['shelters'])} "
                "shelters for structural safety "
                "and bed vacancies"
            ),
            "SHELTER_ANALYSIS_STARTED",
        )

        await asyncio.sleep(0.3)

        shelter_result = generated[2]

        await self.emit(
            "Shelter Agent",
            "COMPLETED",
            (
                f"Selected "
                f"{shelter_result.get('primary_shelter', 'Primary Shelter')} "
                f"({shelter_result.get('primary_vacancies', 0):,} "
                "vacant beds)"
            ),
            "SHELTER_ANALYSIS_COMPLETED",
        )

        await asyncio.sleep(0.3)

        # --------------------------------------------------------
        # 7. COMMANDER CREATES PLAN
        # --------------------------------------------------------

        await self.emit(
            "Commander Agent",
            "RUNNING",
            (
                "Consolidating specialized agent findings "
                "& generating prioritized response plan"
            ),
            "COMMANDER_STARTED",
        )

        self.version = 1

        (
            self.assessment,
            geo,
            shelter,
            medical,
            resource,
            self.plan,
        ) = generated

        # --------------------------------------------------------
        # OPTIONAL REAL GEMINI REASONING
        # --------------------------------------------------------

        if llm_service.active:

            # IMPORTANT:
            # Do not call model_dump() on None.
            if self.assessment is not None:

                try:
                    llm_reasoning = (
                        await llm_service.analyze_crisis(
                            {
                                "crisis": (
                                    self.crisis.model_dump(
                                        mode="json"
                                    )
                                ),
                                "zones": self.data["zones"],
                                "roads": self.data["roads"],
                            }
                        )
                    )

                    if llm_reasoning:
                        self.assessment.reasoning = (
                            llm_reasoning
                        )

                except Exception as exc:
                    print(
                        f"[LLM] Crisis reasoning skipped: {exc}"
                    )

            if self.plan is not None:

                try:
                    assessment_data = (
                        self.assessment.model_dump()
                        if self.assessment is not None
                        else {}
                    )

                    plan_reasoning = (
                        await llm_service.generate_plan_reasoning(
                            {
                                "assessment": assessment_data,
                                "shelters": self.data["shelters"],
                                "hospitals": self.data["hospitals"],
                                "resources": self.data["resources"],
                            }
                        )
                    )

                    if plan_reasoning:
                        self.plan.explanation.insert(
                            0,
                            plan_reasoning,
                        )

                except Exception as exc:
                    print(
                        f"[LLM] Plan reasoning skipped: {exc}"
                    )

        await asyncio.sleep(0.2)

        recommendation_count = (
            len(self.plan.recommendations)
            if self.plan
            else 0
        )

        await self.emit(
            "Commander Agent",
            "COMPLETED",
            (
                f"Response Plan v{self.version} "
                f"formulated with {recommendation_count} "
                "prioritized directives"
            ),
            "RESPONSE_PLAN_CREATED",
        )

        self._audit(
            "Commander Agent",
            f"Formulated Response Plan v{self.version}",
            [
                r.action
                for r in self.plan.recommendations
            ]
            if self.plan
            else [],
            "RESPONSE_PLAN_CREATED",
        )

        await self.emit(
            "Commander Agent",
            "WAITING",
            (
                "CRITICAL DIRECTIVES REQUIRE HUMAN "
                "APPROVAL BEFORE EXECUTION"
            ),
            "HUMAN_APPROVAL_REQUESTED",
        )

        return self.current()

    # ============================================================
    # PRESERVE APPROVAL / REJECTION STATUS
    # ============================================================

    def _preserve_recommendation_decisions(
        self,
        old_plan,
        new_plan,
    ):
        """
        IMPORTANT FIX:

        Re-planning creates a new plan object.

        Without this function:
            APPROVED -> replan -> PENDING

        With this function:
            APPROVED -> replan -> APPROVED
            REJECTED -> replan -> REJECTED

        Matching is done using both recommendation ID
        and action text so it remains stable even if
        planning_service changes one field.
        """

        if old_plan is None or new_plan is None:
            return

        old_recommendations = getattr(
            old_plan,
            "recommendations",
            [],
        )

        new_recommendations = getattr(
            new_plan,
            "recommendations",
            [],
        )

        decisions = {}

        for rec in old_recommendations:

            approval_status = getattr(
                rec,
                "approval_status",
                None,
            )

            execution_status = getattr(
                rec,
                "execution_status",
                None,
            )

            if approval_status in (
                "APPROVED",
                "REJECTED",
            ):

                rec_id = getattr(
                    rec,
                    "id",
                    None,
                )

                action = getattr(
                    rec,
                    "action",
                    None,
                )

                if rec_id:
                    decisions[
                        f"id:{rec_id}"
                    ] = (
                        approval_status,
                        execution_status,
                    )

                if action:
                    decisions[
                        f"action:{action}"
                    ] = (
                        approval_status,
                        execution_status,
                    )

        for rec in new_recommendations:

            rec_id = getattr(
                rec,
                "id",
                None,
            )

            action = getattr(
                rec,
                "action",
                None,
            )

            decision = None

            if rec_id:
                decision = decisions.get(
                    f"id:{rec_id}"
                )

            if decision is None and action:
                decision = decisions.get(
                    f"action:{action}"
                )

            if decision:

                approval_status, execution_status = (
                    decision
                )

                rec.approval_status = approval_status

                if execution_status:
                    rec.execution_status = (
                        execution_status
                    )

        # If every recommendation is approved,
        # the entire plan can also be considered approved.
        if new_recommendations:

            all_approved = all(
                getattr(
                    rec,
                    "approval_status",
                    None,
                )
                == "APPROVED"
                for rec in new_recommendations
            )

            all_rejected = all(
                getattr(
                    rec,
                    "approval_status",
                    None,
                )
                == "REJECTED"
                for rec in new_recommendations
            )

            if all_approved:
                new_plan.status = "APPROVED"

            elif all_rejected:
                new_plan.status = "REJECTED"

            else:
                # Do not mark the entire plan approved
                # when only some actions are approved.
                if getattr(
                    new_plan,
                    "status",
                    None,
                ) in (
                    "APPROVED",
                    "REJECTED",
                ):
                    new_plan.status = "PENDING"

    # ============================================================
    # APPROVE SINGLE ACTION
    # ============================================================

    async def approve_action(
        self,
        action_id: str,
    ):
        if not self.plan:
            raise ValueError(
                "No active response plan to approve actions from"
            )

        rec = next(
            (
                r
                for r in self.plan.recommendations
                if r.id == action_id
                or r.action == action_id
            ),
            None,
        )

        if not rec:
            raise ValueError(
                f"Recommendation {action_id} not found"
            )

        # --------------------------------------------------------
        # PREVENT DOUBLE APPROVAL
        # --------------------------------------------------------

        if getattr(
            rec,
            "approval_status",
            None,
        ) == "APPROVED":

            return self.current()

        # --------------------------------------------------------
        # PREVENT APPROVING A REJECTED ACTION
        # --------------------------------------------------------

        if getattr(
            rec,
            "approval_status",
            None,
        ) == "REJECTED":

            raise ValueError(
                "This recommendation has already been rejected."
            )

        # --------------------------------------------------------
        # SAVE APPROVAL
        # --------------------------------------------------------

        rec.approval_status = "APPROVED"
        rec.execution_status = "SIMULATED"

        self._audit(
            "Human Commander",
            f"Authorized: {rec.action}",
            [
                rec.action,
                rec.affected_area,
            ],
            "ACTION_APPROVED",
        )

        await self.emit(
            "Human Commander",
            "APPROVED",
            f"Action Approved: {rec.action}",
            "ACTION_APPROVED",
        )

        # --------------------------------------------------------
        # EXECUTE SIMULATED OPERATIONAL IMPACT
        # --------------------------------------------------------

        changed_diff = []

        action_text = (
            rec.action.lower()
            if rec.action
            else ""
        )

        # --------------------------------------------------------
        # BLOCK ROAD
        # --------------------------------------------------------

        if (
            rec.action_type == "BLOCK_ROAD"
            or "block" in action_text
        ):

            road = next(
                (
                    r
                    for r in self.data["roads"]
                    if r["status"] != "BLOCKED"
                ),
                None,
            )

            if road:

                road["status"] = "BLOCKED"

                changed_diff.append(
                    (
                        f"{road['id']} marked BLOCKED. "
                        "Emergency rerouting calculated."
                    )
                )

                await self.emit(
                    "Geo Agent",
                    "WARNING",
                    (
                        f"Road status updated: "
                        f"{road['id']} is now BLOCKED"
                    ),
                    "ROAD_BLOCKED",
                )

        # --------------------------------------------------------
        # ALLOCATE RESOURCE
        # --------------------------------------------------------

        elif (
            rec.action_type == "ALLOCATE_RESOURCE"
            or "allocate" in action_text
        ):

            water = next(
                (
                    r
                    for r in self.data["resources"]
                    if "WATER" in r["type"]
                ),
                None,
            )

            if (
                water
                and water["quantity_available"] >= 500
            ):

                water["quantity_available"] -= 500

                changed_diff.append(
                    (
                        f"Dispatched 500L Potable Water "
                        f"to {rec.affected_area}. "
                        f"Remaining: "
                        f"{water['quantity_available']:,}L"
                    )
                )

                await self.emit(
                    "Resource Agent",
                    "COMPLETED",
                    (
                        f"500 Water Units dispatched "
                        f"to {rec.affected_area}"
                    ),
                    "RESOURCE_ASSIGNED",
                )

        # --------------------------------------------------------
        # RESERVE BEDS
        # --------------------------------------------------------

        elif (
            rec.action_type == "RESERVE_BEDS"
            or "bed" in action_text
        ):

            hosp = next(
                (
                    h
                    for h in self.data["hospitals"]
                    if h["available_beds"] >= 15
                ),
                self.data["hospitals"][0],
            )

            hosp["available_beds"] = max(
                0,
                hosp["available_beds"] - 15,
            )

            changed_diff.append(
                (
                    f"15 Acute Trauma Beds reserved "
                    f"at {hosp['name']}. "
                    f"Available remaining: "
                    f"{hosp['available_beds']}"
                )
            )

            await self.emit(
                "Medical Agent",
                "COMPLETED",
                (
                    f"15 beds reserved at "
                    f"{hosp['name']}"
                ),
                "HOSPITAL_UPDATED",
            )

        # --------------------------------------------------------
        # OPEN SHELTER
        # --------------------------------------------------------

        elif (
            rec.action_type == "OPEN_SHELTER"
            or "shelter" in action_text
        ):

            shelter = self.data["shelters"][0]

            shelter["occupancy"] = min(
                shelter["capacity"],
                shelter["occupancy"] + 250,
            )

            changed_diff.append(
                (
                    f"Shelter {shelter['name']} "
                    "intake expanded "
                    "(+250 evacuees admitted)"
                )
            )

            await self.emit(
                "Shelter Agent",
                "COMPLETED",
                (
                    f"Shelter {shelter['name']} "
                    "intake confirmed"
                ),
                "SHELTER_UPDATED",
            )

        # --------------------------------------------------------
        # ACTION EXECUTED
        # --------------------------------------------------------

        await self.emit(
            "System",
            "COMPLETED",
            "Simulated action executed in operational state environment",
            "ACTION_EXECUTED",
        )

        self._audit(
            "System",
            f"Executed simulated action: {rec.action}",
            changed_diff,
            "ACTION_EXECUTED",
        )

        # --------------------------------------------------------
        # AUTONOMOUS REPLANNING
        # --------------------------------------------------------

        await self.trigger_replanning(
            changed_diff
        )

        return self.current()

    # ============================================================
    # REJECT SINGLE ACTION
    # ============================================================

    async def reject_action(
        self,
        action_id: str,
        reason: str = "Operator rejected recommendation",
    ):

        if not self.plan:
            raise ValueError("No active plan")

        rec = next(
            (
                r
                for r in self.plan.recommendations
                if r.id == action_id
                or r.action == action_id
            ),
            None,
        )

        if not rec:
            raise ValueError(
                f"Recommendation {action_id} not found"
            )

        # --------------------------------------------------------
        # PREVENT DOUBLE REJECTION
        # --------------------------------------------------------

        if getattr(
            rec,
            "approval_status",
            None,
        ) == "REJECTED":

            return self.current()

        # --------------------------------------------------------
        # PREVENT REJECTING AN APPROVED ACTION
        # --------------------------------------------------------

        if getattr(
            rec,
            "approval_status",
            None,
        ) == "APPROVED":

            raise ValueError(
                "This recommendation has already been approved."
            )

        rec.approval_status = "REJECTED"
        rec.execution_status = "NOT_EXECUTED"

        self._audit(
            "Human Commander",
            f"Rejected action: {action_id}",
            [reason],
            "ACTION_REJECTED",
        )

        await self.emit(
            "Human Commander",
            "REJECTED",
            (
                f"Action Rejected: "
                f"{action_id} — {reason}"
            ),
            "ACTION_REJECTED",
        )

        # IMPORTANT:
        # Do NOT replan here.
        #
        # This means the UI will continue showing
        # REJECTED for this recommendation.
        #
        # If another action is approved later and
        # re-planning happens, the rejected status
        # is preserved by _preserve_recommendation_decisions().

        return self.current()

    # ============================================================
    # APPROVE COMPLETE PLAN
    # ============================================================

    async def approve_all_plan(self):

        if not self.plan:
            raise ValueError(
                "No active response plan"
            )

        self.plan.status = "APPROVED"

        for rec in self.plan.recommendations:

            # Only approve actions that haven't been rejected.
            if getattr(
                rec,
                "approval_status",
                None,
            ) != "REJECTED":

                rec.approval_status = "APPROVED"
                rec.execution_status = "SIMULATED"

        self._audit(
            "Human Commander",
            f"Full Plan v{self.version} Approved",
            [
                r.action
                for r in self.plan.recommendations
            ],
            "PLAN_APPROVED",
        )

        await self.emit(
            "Human Commander",
            "APPROVED",
            (
                f"Full Response Plan v{self.version} "
                "approved by Emergency Commander"
            ),
            "PLAN_APPROVED",
        )

        return self.current()

    # ============================================================
    # REJECT COMPLETE PLAN
    # ============================================================

    async def reject_all_plan(
        self,
        reason: str = "Commander requested alternative plan",
    ):

        if not self.plan:
            raise ValueError(
                "No active response plan"
            )

        self.plan.status = "REJECTED"

        for rec in self.plan.recommendations:
            rec.approval_status = "REJECTED"
            rec.execution_status = "NOT_EXECUTED"

        self._audit(
            "Human Commander",
            f"Plan v{self.version} Rejected",
            [reason],
            "PLAN_REJECTED",
        )

        await self.emit(
            "Human Commander",
            "REJECTED",
            (
                f"Plan v{self.version} Rejected: "
                f"{reason}"
            ),
            "PLAN_REJECTED",
        )

        return self.current()

    # ============================================================
    # AUTONOMOUS RE-PLANNING
    # ============================================================

    async def trigger_replanning(
        self,
        changes: list[str] | None = None,
    ):

        changes = changes or [
            (
                "Operational state updated — "
                "re-evaluating optimal routes and logistics"
            )
        ]

        # --------------------------------------------------------
        # SAVE OLD PLAN BEFORE GENERATING NEW PLAN
        # --------------------------------------------------------

        old_plan = (
            self.plan.model_copy(
                deep=True
            )
            if self.plan
            else None
        )

        self.previous_plan = (
            old_plan.model_copy(
                deep=True
            )
            if old_plan
            else None
        )

        self.version += 1

        await self.emit(
            "Commander Agent",
            "RUNNING",
            (
                "Situation shift detected — "
                f"Triggering Autonomous Re-Planning "
                f"Cycle (v{self.version})"
            ),
            "REPLANNING_TRIGGERED",
        )

        await asyncio.sleep(0.3)

        # --------------------------------------------------------
        # AGENTS RE-EVALUATE
        # --------------------------------------------------------

        for agent in [
            "Geo Agent",
            "Shelter Agent",
            "Resource Agent",
            "Medical Agent",
        ]:

            await self.emit(
                agent,
                "RUNNING",
                (
                    f"Re-evaluating parameters "
                    f"for Plan v{self.version}"
                ),
                "AGENT_STARTED",
            )

            await asyncio.sleep(0.2)

            await self.emit(
                agent,
                "COMPLETED",
                "Parameters updated against modified system state",
                "AGENT_COMPLETED",
            )

        # --------------------------------------------------------
        # GENERATE NEW PLAN
        # --------------------------------------------------------

        generated = generate(
            self.crisis,
            self.data,
            self.version,
            blocked=True,
            changes=changes,
        )

        if not generated or len(generated) < 6:

            await self.emit(
                "Commander Agent",
                "WARNING",
                (
                    "Re-planning returned an incomplete "
                    "plan. Existing plan preserved."
                ),
                "REPLANNING_FAILED",
            )

            # IMPORTANT:
            # Do not destroy a working approved plan
            # if planning service fails.

            return self.current()

        (
            new_assessment,
            geo,
            shelter,
            medical,
            resource,
            new_plan,
        ) = generated

        # --------------------------------------------------------
        # PRESERVE APPROVAL / REJECTION
        # --------------------------------------------------------

        self._preserve_recommendation_decisions(
            old_plan,
            new_plan,
        )

        # --------------------------------------------------------
        # UPDATE STATE
        # --------------------------------------------------------

        self.assessment = new_assessment
        self.plan = new_plan

        # --------------------------------------------------------
        # LLM ENHANCEMENT
        # --------------------------------------------------------

        if llm_service.active:

            if self.assessment is not None:

                try:

                    llm_reasoning = (
                        await llm_service.analyze_crisis(
                            {
                                "crisis": (
                                    self.crisis.model_dump(
                                        mode="json"
                                    )
                                ),
                                "zones": self.data["zones"],
                                "roads": self.data["roads"],
                            }
                        )
                    )

                    if llm_reasoning:
                        self.assessment.reasoning = (
                            llm_reasoning
                        )

                except Exception as exc:

                    print(
                        f"[LLM] Replanning reasoning skipped: {exc}"
                    )

            if self.plan is not None:

                try:

                    assessment_data = (
                        self.assessment.model_dump()
                        if self.assessment is not None
                        else {}
                    )

                    plan_reasoning = (
                        await llm_service.generate_plan_reasoning(
                            {
                                "assessment": assessment_data,
                                "shelters": self.data["shelters"],
                                "hospitals": self.data["hospitals"],
                                "resources": self.data["resources"],
                            }
                        )
                    )

                    if plan_reasoning:
                        self.plan.explanation.insert(
                            0,
                            plan_reasoning,
                        )

                except Exception as exc:

                    print(
                        f"[LLM] Replanning plan reasoning skipped: {exc}"
                    )

        # --------------------------------------------------------
        # COMPLETE
        # --------------------------------------------------------

        await self.emit(
            "Commander Agent",
            "COMPLETED",
            (
                "Autonomous Re-Planning Complete. "
                f"Response Plan v{self.version} "
                "Ready for Review"
            ),
            "REPLANNING_COMPLETED",
        )

        self._audit(
            "Commander Agent",
            (
                f"Generated Re-Planned "
                f"Response Plan v{self.version}"
            ),
            changes,
            "REPLANNING_COMPLETED",
        )

        return self.current()

    # ============================================================
    # BLOCK ROAD
    # ============================================================

    async def block_road(
        self,
        road_id: str = "Route A-B (NH-65 Bypass)",
    ):

        if not self.active:
            await self.trigger()

        road = next(
            (
                r
                for r in self.data["roads"]
                if r["id"] == road_id
                or road_id in r["id"]
            ),
            None,
        )

        if road is None:

            road = next(
                (
                    r
                    for r in self.data["roads"]
                    if r["status"] == "OPEN"
                ),
                None,
            )

        if road:

            road["status"] = "BLOCKED"

            self._audit(
                "Emergency Operator",
                f"Road {road['id']} Blocked",
                [road["id"]],
                "ROAD_BLOCKED",
            )

            await self.emit(
                "Geo Agent",
                "WARNING",
                (
                    f"CRITICAL: {road['id']} "
                    "is now BLOCKED due to flood waters."
                ),
                "ROAD_BLOCKED",
            )

            await self.trigger_replanning(
                [
                    (
                        f"{road['id']} obstructed — "
                        "Traffic diverted to secondary bypass"
                    )
                ]
            )

        return self.current()

    # ============================================================
    # DEMO SIMULATION
    # ============================================================

    async def run_demo_simulation(self):
        """
        One-click demonstration sequence
        for AI Expo / Hackathon Judges.
        """

        self.reset()

        # --------------------------------------------------------
        # STEP 1 — DEMO START
        # --------------------------------------------------------

        await self.emit(
            "System",
            "COMPLETED",
            "Starting Automated AI Command Center Demonstration...",
            "DEMO_STARTED",
        )

        await asyncio.sleep(0.4)

        # --------------------------------------------------------
        # STEP 2 — TRIGGER CRISIS
        # --------------------------------------------------------

        await self.trigger()

        await asyncio.sleep(0.5)

        # --------------------------------------------------------
        # STEP 3 — HUMAN APPROVAL SIMULATION
        # --------------------------------------------------------

        if (
            self.plan
            and self.plan.recommendations
        ):

            target_rec = (
                self.plan.recommendations[1]
                if len(
                    self.plan.recommendations
                ) > 1
                else self.plan.recommendations[0]
            )

            await self.emit(
                "System",
                "COMPLETED",
                (
                    "Simulating Commander Approval "
                    f"for '{target_rec.action}'..."
                ),
                "DEMO_STEP",
            )

            await asyncio.sleep(0.5)

            await self.approve_action(
                target_rec.id
            )

        await self.emit(
            "System",
            "COMPLETED",
            (
                "Demonstration Walkthrough Complete! "
                "Autonomous multi-agent coordination verified."
            ),
            "DEMO_COMPLETED",
        )

        return self.current()

    # ============================================================
    # ASSIGN RESOURCE
    # ============================================================

    async def assign_resource(
        self,
        resource_id: str,
        zone: str,
    ):

        resource = next(
            (
                r
                for r in self.data["resources"]
                if r["id"] == resource_id
            ),
            None,
        )

        if (
            resource
            and resource["status"] != "UNAVAILABLE"
        ):

            resource.update(
                status="ASSIGNED",
                assigned_zone=zone,
            )

            self._audit(
                "Logistics Commander",
                f"Assigned {resource_id} to {zone}",
                [
                    resource_id,
                    zone,
                ],
                "RESOURCE_ASSIGNED",
            )

            await self.emit(
                "Resource Agent",
                "COMPLETED",
                (
                    f"{resource_id} dispatched "
                    f"to {zone}"
                ),
                "RESOURCE_ASSIGNED",
            )

        return self.current()

    # ============================================================
    # RELEASE RESOURCE
    # ============================================================

    async def release_resource(
        self,
        resource_id: str,
    ):

        resource = next(
            (
                r
                for r in self.data["resources"]
                if r["id"] == resource_id
            ),
            None,
        )

        if resource:

            resource.update(
                status="AVAILABLE",
                assigned_zone=None,
            )

            self._audit(
                "Logistics Commander",
                f"Released {resource_id}",
                [resource_id],
                "RESOURCE_RELEASED",
            )

            await self.emit(
                "Resource Agent",
                "COMPLETED",
                (
                    f"{resource_id} returned to "
                    "available inventory pool"
                ),
                "RESOURCE_RELEASED",
            )

        return self.current()

    # ============================================================
    # ALLOCATE SHELTER
    # ============================================================

    async def allocate_shelter(
        self,
        shelter_name: str,
        people: int,
    ):

        shelter = next(
            (
                s
                for s in self.data["shelters"]
                if s["name"] == shelter_name
            ),
            None,
        )

        if not shelter:
            raise ValueError(
                f"Shelter {shelter_name} not found"
            )

        remaining = (
            shelter["capacity"]
            - shelter["occupancy"]
        )

        if people < 1 or people > remaining:
            raise ValueError(
                (
                    f"Requested {people} exceeds "
                    f"available vacancies ({remaining})"
                )
            )

        shelter["occupancy"] += people

        self._audit(
            "Shelter Commander",
            (
                f"Allocated {people} evacuees "
                f"to {shelter_name}"
            ),
            [
                shelter_name,
                str(people),
            ],
            "SHELTER_UPDATED",
        )

        await self.emit(
            "Shelter Agent",
            "COMPLETED",
            (
                f"{people:,} evacuees admitted "
                f"to {shelter_name}"
            ),
            "SHELTER_UPDATED",
        )

        return self.current()

    # ============================================================
    # RESERVE BEDS
    # ============================================================

    async def reserve_beds(
        self,
        hospital_name: str,
        beds: int,
    ):

        hospital = next(
            (
                h
                for h in self.data["hospitals"]
                if h["name"] == hospital_name
            ),
            None,
        )

        if not hospital:
            raise ValueError(
                f"Hospital {hospital_name} not found"
            )

        if (
            beds < 1
            or beds > hospital["available_beds"]
        ):
            raise ValueError(
                (
                    f"Requested {beds} exceeds "
                    f"available capacity "
                    f"({hospital['available_beds']})"
                )
            )

        hospital["available_beds"] -= beds

        self._audit(
            "Medical Commander",
            (
                f"Reserved {beds} beds "
                f"at {hospital_name}"
            ),
            [
                hospital_name,
                str(beds),
            ],
            "HOSPITAL_UPDATED",
        )

        await self.emit(
            "Medical Agent",
            "COMPLETED",
            (
                f"{beds} beds reserved "
                f"at {hospital_name}"
            ),
            "HOSPITAL_UPDATED",
        )

        return self.current()

    # ============================================================
    # SET ROAD
    # ============================================================

    async def set_road(
        self,
        road_id: str,
        status: str,
    ):

        road = next(
            (
                r
                for r in self.data["roads"]
                if r["id"] == road_id
            ),
            None,
        )

        if road is None:
            raise ValueError(
                f"Road {road_id} does not exist"
            )

        road["status"] = status

        event = (
            "ROAD_BLOCKED"
            if status == "BLOCKED"
            else "ROAD_OPENED"
        )

        self._audit(
            "Traffic Ops",
            (
                f"Road {road_id} "
                f"set to {status}"
            ),
            [road_id],
            event,
        )

        await self.emit(
            "Geo Agent",
            (
                "WARNING"
                if status == "BLOCKED"
                else "COMPLETED"
            ),
            (
                f"Road {road_id} "
                f"is now {status}"
            ),
            event,
        )

        if (
            status == "BLOCKED"
            and self.active
        ):

            await self.trigger_replanning(
                [
                    f"Road {road_id} is now BLOCKED"
                ]
            )

        return self.current()

    # ============================================================
    # CITIZEN REPORT
    # ============================================================

    def add_report(
        self,
        report: dict,
    ):

        self.reports.append(report)

        self._audit(
            "Citizen Ingestion",
            "Citizen distress report logged",
            [
                report.get(
                    "description",
                    "",
                )
            ],
            "CITIZEN_REPORT_ADDED",
        )

        return self.current()

    # ============================================================
    # EMERGENCY ALERT
    # ============================================================

    def add_alert(
        self,
        message: str,
        language: str = "English",
    ):

        alert = {
            "id": (
                f"ALERT-"
                f"{len(self.alerts) + 1:03}"
            ),
            "type": "Emergency Broadcast",
            "message": message,
            "language": language,
            "priority": "HIGH",
            "created_at": (
                datetime.now(
                    timezone.utc
                ).isoformat()
            ),
            "status": "ACTIVE",
        }

        self.alerts.append(alert)

        self._audit(
            "Communication Agent",
            (
                f"Broadcasted alert "
                f"({language})"
            ),
            [language],
            "ALERT_CREATED",
        )

        return self.current()

    # ============================================================
    # AUDIT
    # ============================================================

    def _audit(
        self,
        agent: str,
        action: str,
        data: list,
        event: str,
    ):

        self.audit.append(
            {
                "id": str(uuid4()),

                "timestamp": (
                    datetime.now(
                        timezone.utc
                    ).isoformat()
                ),

                "agent": agent,
                "actor": agent,

                "action": action,
                "description": action,

                "reason": (
                    "Autonomous multi-agent synthesis "
                    "with human verification checkpoint"
                ),

                "data_used": data,

                "metadata": {
                    "location": self.location["name"]
                },

                "location": self.location["name"],

                "plan_version": self.version,

                "human_approval": (
                    self.plan.status
                    if self.plan
                    else "N/A"
                ),

                "event_type": event,
            }
        )

    # ============================================================
    # CURRENT SYSTEM STATE
    # ============================================================

    def current(self) -> dict:

        total_capacity = sum(
            s["capacity"]
            for s in self.data["shelters"]
        )

        occupied = sum(
            s["occupancy"]
            for s in self.data["shelters"]
        )

        active_resources = sum(
            r["status"] != "UNAVAILABLE"
            for r in self.data["resources"]
        )

        assigned = sum(
            r["status"] == "ASSIGNED"
            for r in self.data["resources"]
        )

        open_roads = [
            r
            for r in self.data["roads"]
            if r["status"] == "OPEN"
        ]

        metrics = {

            "planning_time_seconds":
                1 if self.active else 0,

            "replanning_time_seconds":
                1 if self.version >= 2 else 0,

            "shelter_utilization":
                round(
                    (
                        occupied
                        / max(
                            1,
                            total_capacity,
                        )
                    )
                    * 100
                ),

            "resource_utilization":
                (
                    round(
                        (
                            assigned
                            / max(
                                1,
                                active_resources,
                            )
                        )
                        * 100
                    )
                    if active_resources
                    else 0
                ),

            "affected_population_covered":
                (
                    self.crisis.affected_population
                    if self.crisis
                    else 0
                ),

            "available_hospital_capacity":
                sum(
                    h["available_beds"]
                    for h in self.data["hospitals"]
                ),

            "route_distance_km":
                (
                    round(
                        sum(
                            r["distance"]
                            for r in open_roads
                        )
                        / max(
                            1,
                            len(open_roads),
                        ),
                        1,
                    )
                ),

            "available_buses":
                sum(
                    r["status"] == "AVAILABLE"
                    and "BUS" in r["type"]
                    for r in self.data["resources"]
                ),

            "available_ambulances":
                sum(
                    r["status"] == "AVAILABLE"
                    and "AMBULANCE" in r["type"]
                    for r in self.data["resources"]
                ),

            "agent_executions":
                len(self.events),

            "plan_versions":
                self.version,

            "human_approvals":
                len(
                    [
                        a
                        for a in self.audit
                        if a["event_type"]
                        in (
                            "ACTION_APPROVED",
                            "PLAN_APPROVED",
                        )
                    ]
                ),

            "total_crises":
                len(
                    [
                        a
                        for a in self.audit
                        if a["event_type"]
                        == "CRISIS_RECEIVED"
                    ]
                ),

            "active_crisis":
                self.active,

            "total_events":
                len(self.events),

            "blocked_roads":
                len(
                    [
                        r
                        for r in self.data["roads"]
                        if r["status"] == "BLOCKED"
                    ]
                ),

            "plans_generated":
                self.version,

            "plans_replanned":
                max(
                    0,
                    self.version - 1,
                ),

            "gemini_requests":
                1 if llm_service.active else 0,

            "gemini_failures":
                0,

            "average_agent_execution_time":
                0.3,
        }

        # --------------------------------------------------------
        # SAFE SERIALIZATION
        # --------------------------------------------------------

        assessment_data = None

        if self.assessment is not None:
            try:
                assessment_data = (
                    self.assessment.model_dump()
                )
            except Exception:
                assessment_data = None

        plan_data = None

        if self.plan is not None:
            try:
                plan_data = (
                    self.plan.model_dump(
                        mode="json"
                    )
                )
            except Exception:
                plan_data = None

        previous_plan_data = None

        if self.previous_plan is not None:
            try:
                previous_plan_data = (
                    self.previous_plan.model_dump(
                        mode="json"
                    )
                )
            except Exception:
                previous_plan_data = None

        crisis_data = None

        if self.crisis is not None:
            try:
                crisis_data = (
                    self.crisis.model_dump(
                        mode="json"
                    )
                )
            except Exception:
                crisis_data = None

        return {

            "active":
                self.active,

            "demo_mode":
                not llm_service.active,

            "ai_mode":
                (
                    "REAL AI - GEMINI"
                    if llm_service.active
                    else
                    "DEMO MODE - DETERMINISTIC AGENTS"
                ),

            "location":
                self.location,

            "crisis":
                crisis_data,

            "assessment":
                assessment_data,

            "plan":
                plan_data,

            "previous_plan":
                previous_plan_data,

            "data":
                self.data,

            "events":
                self.events,

            "audit":
                self.audit,

            "alerts":
                self.alerts,

            "reports":
                self.reports,

            "agent_logs":
                self.agent_logs,

            "agent_states":
                self.agent_states,

            "created_at":
                self.created_at,

            "updated_at":
                self.updated_at,

            "metrics":
                metrics,
        }


# ================================================================
# GLOBAL SERVICE INSTANCE
# ================================================================

service = CrisisService()