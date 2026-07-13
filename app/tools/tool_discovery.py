from __future__ import annotations

import importlib
import inspect
import pkgutil
from typing import Iterable

from app.tools.base_tool import BaseTool


IGNORED_MODULES = {
    "__init__",
    "base_tool",
    "tool_context",
    "tool_discovery",
    "tool_executor",
    "tool_permissions",
    "tool_registry",
    "tool_result",
    "tool_validation",
}


def discover_tools(package_name: str = "app.tools", ignore_modules: Iterable[str] | None = None) -> list[BaseTool]:
    ignored = set(IGNORED_MODULES)
    ignored.update(ignore_modules or [])
    package = importlib.import_module(package_name)
    discovered: list[BaseTool] = []

    for module_info in pkgutil.iter_modules(package.__path__):
        if module_info.name in ignored:
            continue
        module = importlib.import_module(f"{package_name}.{module_info.name}")
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if obj is BaseTool or not issubclass(obj, BaseTool):
                continue
            discovered.append(obj())
    return discovered
