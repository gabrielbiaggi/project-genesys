# Agent-MCP/agent_mcp/tools/os_tools.py
import psutil
from typing import Dict, Any, List

import mcp.types as mcp_types
from .registry import register_tool
from ..core.auth import verify_token


async def list_running_processes_impl(
    arguments: Dict[str, Any],
) -> List[mcp_types.TextContent]:
    """Lists running processes on the host machine."""
    token = arguments.get("token")
    if not verify_token(token, required_role="admin"):
        return [mcp_types.TextContent(text="Unauthorized: Admin token required.")]

    try:
        processes = []
        for proc in psutil.process_iter(
            ["pid", "name", "username", "cpu_percent", "memory_info"]
        ):
            processes.append(
                f"PID: {proc.info['pid']}, Name: {proc.info['name']}, "
                f"User: {proc.info['username']}, CPU: {proc.info['cpu_percent']}%, "
                f"Memory: {proc.info['memory_info'].rss / (1024 * 1024):.2f} MB"
            )
        return [mcp_types.TextContent(text="\\n".join(processes))]
    except Exception as e:
        return [mcp_types.TextContent(text=f"Error listing processes: {e}")]


async def get_system_usage_impl(
    arguments: Dict[str, Any],
) -> List[mcp_types.TextContent]:
    """Gets overall system resource usage (CPU, Memory, Disk)."""
    token = arguments.get("token")
    if not verify_token(token, required_role="admin"):
        return [mcp_types.TextContent(text="Unauthorized: Admin token required.")]

    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        disk_usage = psutil.disk_usage("/")

        usage_report = (
            f"System Usage Report:\\n"
            f"- CPU Usage: {cpu_usage}%\\n"
            f"- Memory Usage: {memory_info.percent}% (Total: {memory_info.total / (1024**3):.2f} GB, Used: {memory_info.used / (1024**3):.2f} GB)\\n"
            f"- Disk Usage (Root): {disk_usage.percent}% (Total: {disk_usage.total / (1024**3):.2f} GB, Used: {disk_usage.used / (1024**3):.2f} GB)"
        )
        return [mcp_types.TextContent(text=usage_report)]
    except Exception as e:
        return [mcp_types.TextContent(text=f"Error getting system usage: {e}")]


def register_os_tools():
    """Registers the OS interaction tools."""
    register_tool(
        name="list_running_processes",
        description="Lists all running processes on the server machine. Requires admin privileges.",
        input_schema={
            "type": "object",
            "properties": {
                "token": {
                    "type": "string",
                    "description": "Admin authentication token.",
                }
            },
            "required": ["token"],
        },
        implementation=list_running_processes_impl,
    )
    register_tool(
        name="get_system_usage",
        description="Gets overall system resource usage (CPU, Memory, Disk). Requires admin privileges.",
        input_schema={
            "type": "object",
            "properties": {
                "token": {
                    "type": "string",
                    "description": "Admin authentication token.",
                }
            },
            "required": ["token"],
        },
        implementation=get_system_usage_impl,
    )
