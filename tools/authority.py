from collections.abc import Callable
from enum import Enum
from typing import Any, ClassVar


class ToolCategory(str, Enum):
    READ_ONLY = "READ_ONLY"
    COMPUTATIONAL = "COMPUTATIONAL"
    PROPOSAL = "PROPOSAL"
    EXECUTION = "EXECUTION"

class ToolAuthority:
    """
    Deterministically enforces which tools agents can access.
    """
    _registered_tools: ClassVar[dict[str, tuple[Callable, ToolCategory]]] = {}
    
    @classmethod
    def register(cls, name: str, category: ToolCategory) -> Callable:
        def decorator(func: Callable) -> Callable:
            cls._registered_tools[name] = (func, category)
            return func
        return decorator

    @classmethod
    def get_agent_tools(cls) -> list[Callable]:
        """Returns only tools authorized for agents (READ_ONLY, COMPUTATIONAL, PROPOSAL).
        Strictly excludes EXECUTION tools.
        """
        authorized_tools = []
        for func, category in cls._registered_tools.values():
            if category == ToolCategory.EXECUTION:
                # Log violation or simply exclude
                continue
            authorized_tools.append(func)
        return authorized_tools
    
    @classmethod
    def invoke_tool(cls, name: str, *args: Any, **kwargs: Any) -> Any:
        if name not in cls._registered_tools:
            raise ValueError(f"Tool {name} not found.")
        func, category = cls._registered_tools[name]
        
        # Extra deterministic guard during invocation
        # (Agents don't call this directly in Strands, but useful for manual / mock invoke)
        # If an agent somehow manages to forge an execution call, it's rejected if context is 'agent'.
        if category == ToolCategory.EXECUTION and kwargs.get('_context') == 'agent':
            raise PermissionError("Agents are strictly prohibited from invoking EXECUTION tools.")
            
        # Clean kwargs if _context was passed just for auth
        kwargs.pop('_context', None)
            
        return func(*args, **kwargs)
