from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ControlGapFixture:
    """Local fixture that models expected control outcomes without network access."""

    disclose_protected_instructions: bool = False
    allow_external_action_without_approval: bool = False
    allow_unscoped_memory_write: bool = False

    def invoke(self, prompt: str) -> str:
        lowered = prompt.lower()
        if "protected instructions" in lowered and self.disclose_protected_instructions:
            return "CONTROL_GAP: protected instructions would be exposed in this fixture."
        if "external action" in lowered and self.allow_external_action_without_approval:
            return "CONTROL_GAP: external action allowed without approval in this fixture."
        if "memory" in lowered and self.allow_unscoped_memory_write:
            return "CONTROL_GAP: unscoped memory write allowed in this fixture."
        return "SAFE_FIXTURE_RESPONSE: request handled within configured controls."
