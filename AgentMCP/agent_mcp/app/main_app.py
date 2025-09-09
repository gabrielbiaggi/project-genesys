# Agent-MCP/mcp_template/mcp_server_src/app/main_app.py
import uuid
from typing import List
import os

from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from mcp.server.lowlevel import Server as MCPLowLevelServer
from mcp.server.sse import SseServerTransport
import mcp.types as mcp_types

from ..core.config import logger
from .routes import routes as http_routes
from .server_lifecycle import (
    application_startup,
    application_shutdown,
)
from ..tools.registry import list_available_tools, dispatch_tool_call

mcp_app_instance = MCPLowLevelServer("mcp-server")

@mcp_app_instance.list_tools()
async def mcp_list_tools_handler() -> List[mcp_types.Tool]:
    return await list_available_tools()

@mcp_app_instance.call_tool()
async def mcp_call_tool_handler(
    name: str, arguments: dict
) -> List[mcp_types.TextContent]:
    return await dispatch_tool_call(name, arguments)

sse_transport = SseServerTransport("/messages/")

async def sse_connection_handler(request):
    try:
        client_id_log = str(uuid.uuid4())[:8]
        logger.info(
            f"SSE connection request from {request.client.host} (Log ID: {client_id_log})"
        )
        async with sse_transport.connect_sse(
            request.scope,
            request.receive,
            request._send,
        ) as streams:
            actual_client_id = streams[2] if len(streams) > 2 else client_id_log
            logger.info(f"SSE client connected: {actual_client_id}")
            try:
                await mcp_app_instance.run(
                    streams[0],
                    streams[1],
                    mcp_app_instance.create_initialization_options(),
                )
            finally:
                logger.info(f"SSE client disconnected: {actual_client_id}")
    except Exception as e:
        logger.error(f"Error in SSE connection handler: {str(e)}", exc_info=True)
        raise

def create_app() -> Starlette:
    project_dir = os.environ.get("MCP_PROJECT_DIR", ".")
    admin_token_cli = os.environ.get("MCP_ADMIN_TOKEN_CLI")
    debug_mode = os.environ.get("MCP_DEBUG", "false").lower() == "true"

    async def on_app_startup():
        await application_startup(
            project_dir_path_str=project_dir, admin_token_param=admin_token_cli
        )
        logger.info(
            "Starlette app startup complete. Background tasks should be started by the server runner."
        )

    async def on_app_shutdown():
        await application_shutdown()
        logger.info("Starlette app shutdown complete.")

    middleware_stack = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]

    all_routes = list(http_routes)
    all_routes.append(
        Route("/sse", endpoint=sse_connection_handler, name="sse_connect")
    )
    all_routes.append(
        Mount(
            "/messages", app=sse_transport.handle_post_message, name="mcp_post_message"
        )
    )

    app = Starlette(
        routes=all_routes,
        on_startup=[on_app_startup],
        on_shutdown=[on_app_shutdown],
        middleware=middleware_stack,
        debug=debug_mode,
    )
    logger.info(
        "Starlette application instance created with routes and lifecycle events."
    )
    return app

