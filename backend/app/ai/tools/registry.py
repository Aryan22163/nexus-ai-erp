from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
from app.core.exceptions import PermissionDeniedException


@dataclass
class ToolDefinition:
    name: str
    description: str
    required_permission: str
    handler: Callable
    is_mutating: bool = False


class ToolRegistry:
    """Central registry of domain-authorized AI tools."""
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}

    def register(
        self,
        name: str,
        description: str,
        required_permission: str,
        is_mutating: bool = False,
    ):
        def decorator(func: Callable):
            self._tools[name] = ToolDefinition(
                name=name,
                description=description,
                required_permission=required_permission,
                handler=func,
                is_mutating=is_mutating,
            )
            return func
        return decorator

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_available_tools(self, user_permissions: List[str]) -> List[ToolDefinition]:
        """List all tools that the current user has permission to invoke."""
        is_super = "*" in user_permissions
        return [
            tool for tool in self._tools.values()
            if is_super or tool.required_permission in user_permissions
        ]


global_tool_registry = ToolRegistry()
