# Agent-MCP/mcp_template/mcp_server_src/tools/__init__.py

"""
This __init__.py file ensures that all tool modules are imported when the 'tools' package is imported.
This process is crucial for the dynamic registration of tools. When each tool module is imported,
it calls `register_tool` from the `tools.registry` module, populating the global dictionaries
`tool_schemas` and `tool_implementations`.

This setup allows for a modular and extensible tool system where new tools can be added
simply by creating a new module and ensuring it's imported here.
"""

from . import admin_tools  # noqa: F401
from . import task_tools  # noqa: F401
from . import file_management_tools  # noqa: F401
from . import project_context_tools  # noqa: F401
from . import file_metadata_tools  # noqa: F401
from . import agent_tools  # noqa: F401
from . import rag_tools  # noqa: F401
from . import utility_tools  # noqa: F401
from . import agent_communication_tools  # noqa: F401
from .registry import tool_schemas, tool_implementations
from ..core.config import logger

# After all imports, the tool registry in tools.registry should be populated.
# We can optionally add a log here to confirm, or check the registry's state.

logger.info(
    f"Tools package initialized. {len(tool_schemas)} tool schemas and "
    f"{len(tool_implementations)} implementations registered."
)
