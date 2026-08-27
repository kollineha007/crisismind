import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

class LLMService:
    """Optional Gemini adapter. Verified application data remains authoritative."""
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY", "").strip()
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.model = None
        if self.api_key:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                self.model = ChatGoogleGenerativeAI(model=self.model_name, google_api_key=self.api_key, temperature=0.2)
            except Exception:
                self.model = None

    @property
    def active(self) -> bool:
        return self.model is not None

    async def _ask(self, role: str, task: str, facts: dict[str, Any]) -> str | None:
        if not self.model:
            return None
        prompt = f"SYSTEM ROLE: {role}\nNever invent or modify numerical facts. Use only the verified facts below.\nVERIFIED FACTS: {facts}\nTASK: {task}\nReturn concise operational reasoning only."
        try:
            response = await self.model.ainvoke(prompt)
            return response.content if isinstance(response.content, str) else str(response.content)
        except Exception:
            return None

    async def analyze_crisis(self, facts: dict[str, Any]) -> str | None:
        return await self._ask("Emergency crisis assessment specialist", "Interpret the incident, explain severity and medical risk, and identify priority zones. Do not change the supplied values.", facts)

    async def generate_plan_reasoning(self, facts: dict[str, Any]) -> str | None:
        return await self._ask("Emergency response commander", "Explain why the verified route, shelter, hospital, and resource recommendations are compatible.", facts)

    async def generate_alert(self, facts: dict[str, Any], language: str) -> str | None:
        return await self._ask("Emergency communications specialist", f"Write a concise citizen-safe evacuation alert in {language}.", facts)

    async def generate_explanation(self, facts: dict[str, Any]) -> str | None:
        return await self._ask("Explainable emergency decision specialist", "Summarize data used, alternatives rejected, and expected impact.", facts)

    async def analyze_citizen_report(self, report: str) -> str | None:
        return await self._ask("Citizen report triage specialist", "Extract incident type, location, affected people, urgency, and required response without inventing facts.", {"report": report})

    async def analyze_image(self, image_description: str) -> str | None:
        return await self._ask("Emergency visual assessment specialist", "Describe visible flooding, likely blockage, approximate severity, visible people or vehicles, and safety concerns. Do not claim exact measurements.", {"image": image_description})

llm_service = LLMService()