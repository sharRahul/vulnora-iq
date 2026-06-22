from __future__ import annotations

from collections.abc import Iterable

from modules.base import AssessmentModule
from modules.production_wrapper import wrap_production_modules
from modules.starter import build_starter_modules


class ModuleRegistry:
    """Registry for built-in and future third-party assessment modules."""

    def __init__(self) -> None:
        self._modules: dict[str, AssessmentModule] = {}
        for name, module in wrap_production_modules(build_starter_modules()).items():
            self.register(name, module)

    def register(self, name: str, module: AssessmentModule) -> None:
        if not name:
            raise ValueError("Module name cannot be empty")
        if name in self._modules:
            raise ValueError(f"Module already registered: {name}")
        self._modules[name] = module

    def get(self, name: str) -> AssessmentModule:
        try:
            return self._modules[name]
        except KeyError as exc:
            raise KeyError(f"Unknown assessment module: {name}") from exc

    def names(self) -> list[str]:
        return sorted(self._modules)

    def resolve(self, names: Iterable[str]) -> list[AssessmentModule]:
        return [self.get(name) for name in names]
