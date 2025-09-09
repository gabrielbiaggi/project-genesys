# Agent-MCP/mcp_template/mcp_server_src/app/routes.py
import os
import json
import datetime
import sqlite3
from typing import List, Dict, Any, Optional  # Added List, Dict, Any, Optional

from starlette.routing import Route
from starlette.responses import (
    JSONResponse,
    Response,
    PlainTextResponse,
    StreamingResponse,
) # Adicionado StreamingResponse
from starlette.requests import Request

# Project-specific imports
from ..core.config import logger
from ..core import globals as g
from ..core.auth import verify_token, get_agent_id as auth_get_agent_id
from ..utils.json_utils import get_sanitized_json_body
from ..db.connection import get_db_connection
from ..db.actions.agent_actions_db import log_agent_action_to_db

from ..features.dashboard.api import fetch_graph_data_logic, fetch_task_tree_data_logic

# Adicionar importação para métricas de sistema
from ..features.dashboard.system_metrics import get_system_metrics

# Adicionar importação para o gerenciador de serviços
from ..features.dashboard.service_manager import (
    get_service_status,
    start_service,
    stop_service,
    restart_service,
)
from ..features.dashboard.styles import get_node_style

# Adicionar importações para as implementações de ferramentas de admin
from ..tools.admin_tools import create_agent_tool_impl, terminate_agent_tool_impl
import mcp.types as mcp_types

# --- Service Management Endpoints ---
from ..features.service_manager import (
    start_genesys_process,
    stop_genesys_process,
    get_genesys_status,
)

import uuid
import time
import asyncio # Adicionado para o gerador de streaming


# --- Funções de Rota da API ---


async def system_metrics_api_route(request: Request) -> JSONResponse:
    """Endpoint da API para coletar e retornar métricas de sistema (CPU, Memória, GPU)."""
    if request.method == "OPTIONS":
        return await handle_options(request)

    try:
        metrics = get_system_metrics()
        return JSONResponse(metrics)
    except Exception as e:
        logger.error(f"Erro ao coletar métricas de sistema: {e}", exc_info=True)
        return JSONResponse(
            {"error": f"Falha ao obter métricas de sistema: {str(e)}"}, status_code=500
        )


async def service_status_api_route(request: Request) -> JSONResponse:
    """Endpoint para obter o status dos serviços."""
    if request.method == "OPTIONS":
        return await handle_options(request)
    try:
        status = get_service_status()
        return JSONResponse(status)
    except Exception as e:
        logger.error(f"Erro ao obter status dos serviços: {e}", exc_info=True)
        return JSONResponse(
            {"error": f"Falha ao obter status dos serviços: {str(e)}"}, status_code=500
        )


async def service_control_api_route(request: Request) -> JSONResponse:
    """Endpoint para controlar os serviços (start, stop, restart)."""
    if request.method == "OPTIONS":
        return await handle_options(request)
    if request.method != "POST":
        return JSONResponse({"error": "Método não permitido"}, status_code=405)

    try:
        body = await request.json()
        action = body.get("action")
        service_name = body.get("service", "all")  # 'all', 'backend', 'frontend'

        if action not in ["start", "stop", "restart"]:
            return JSONResponse(
                {"error": "Ação inválida. Use 'start', 'stop' ou 'restart'."},
                status_code=400,
            )

        result = {}
        if action == "start":
            result = start_service(service_name)
        elif action == "stop":
            result = stop_service(service_name)
        elif action == "restart":
            result = restart_service(service_name)

        return JSONResponse(result)
    except Exception as e:
        logger.error(f"Erro no controle de serviço: {e}", exc_info=True)
        return JSONResponse(
            {"error": f"Falha ao executar ação de serviço: {str(e)}"}, status_code=500
        )


async def list_agents_api_route(request: Request) -> JSONResponse:
    """Endpoint para listar todos os agentes com detalhes do banco de dados."""
    if request.method == "OPTIONS":
        return await handle_options(request)

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT agent_id, status, capabilities, created_at, current_task, color FROM agents ORDER BY created_at DESC"
        )

        agents = [dict(row) for row in cursor.fetchall()]

        # Deserializar o campo 'capabilities' que está como JSON string no DB
        for agent in agents:
            if isinstance(agent.get("capabilities"), str):
                try:
                    agent["capabilities"] = json.loads(agent["capabilities"])
                except json.JSONDecodeError:
                    agent["capabilities"] = []  # Fallback para JSON inválido

        return JSONResponse(agents)
    except Exception as e:
        logger.error(f"Erro ao listar agentes: {e}", exc_info=True)
        return JSONResponse(
            {"error": f"Falha ao buscar lista de agentes: {str(e)}"}, status_code=500
        )
    finally:
        if conn:
            conn.close()


async def recent_activity_api_route(request: Request) -> JSONResponse:
    """Endpoint para buscar as atividades mais recentes do sistema."""
    if request.method == "OPTIONS":
        return await handle_options(request)

    limit = int(request.query_params.get("limit", 20))

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT timestamp, agent_id, action_type, details FROM agent_actions ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        )

        activities = [dict(row) for row in cursor.fetchall()]
        return JSONResponse(activities)
    except Exception as e:
        logger.error(f"Erro ao buscar atividade recente: {e}", exc_info=True)
        return JSONResponse(
            {"error": f"Falha ao buscar atividade recente: {str(e)}"}, status_code=500
        )
    finally:
        if conn:
            conn.close()


async def delete_agent_api_route(request: Request) -> JSONResponse:
    """Endpoint para deletar (terminar) um agente específico."""
    if request.method == "OPTIONS":
        return await handle_options(request)

    agent_id = request.path_params.get("agent_id")
    if not agent_id:
        return JSONResponse(
            {"error": "Agent ID é obrigatório na URL."}, status_code=400
        )

    try:
        # O token de admin deve ser passado no corpo da requisição por segurança
        body = await request.json()
        admin_token = body.get("token")

        if not verify_token(admin_token, "admin"):
            return JSONResponse(
                {"message": "Não autorizado: Token de admin inválido."}, status_code=401
            )

        # Chama a implementação da ferramenta existente
        result_list = await terminate_agent_tool_impl(
            {"token": admin_token, "agent_id": agent_id}
        )

        # Processa a resposta da ferramenta
        response_text = (
            result_list[0].text
            if result_list
            else "Ação de terminação concluída sem resposta."
        )
        if "terminated" in response_text:
            return JSONResponse({"success": True, "message": response_text})
        elif "not found" in response_text:
            return JSONResponse({"error": response_text}, status_code=404)
        else:
            return JSONResponse({"error": response_text}, status_code=400)

    except Exception as e:
        logger.error(f"Erro ao terminar o agente {agent_id}: {e}", exc_info=True)
        return JSONResponse(
            {"error": f"Falha ao terminar o agente: {str(e)}"}, status_code=500
        )


# --- Dashboard and API Endpoints ---


async def simple_status_api_route(request: Request) -> JSONResponse:
    # Handle OPTIONS for CORS preflight
    if request.method == "OPTIONS":
        return await handle_options(request)

    try:
        # Get system status
        from ..db.actions.agent_db import get_all_active_agents_from_db
        from ..db.actions.task_db import get_all_tasks_from_db

        agents = get_all_active_agents_from_db()
        tasks = get_all_tasks_from_db()

        # Count task statuses
        pending_tasks = len([t for t in tasks if t.get("status") == "pending"])
        completed_tasks = len([t for t in tasks if t.get("status") == "completed"])

        return JSONResponse(
            {
                "server_running": True,
                "total_agents": len(agents),
                "active_agents": len(
                    [a for a in agents if a.get("status") == "active"]
                ),
                "total_tasks": len(tasks),
                "pending_tasks": pending_tasks,
                "completed_tasks": completed_tasks,
                "last_updated": datetime.datetime.now().isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"Error in simple_status_api_route: {e}", exc_info=True)
        return JSONResponse(
            {"error": f"Failed to get simple status: {str(e)}"}, status_code=500
        )


async def graph_data_api_route(request: Request) -> JSONResponse:
    # // ... (implementation from previous response)
    try:
        data = await fetch_graph_data_logic(g.file_map.copy())
        return JSONResponse(data)
    except Exception as e:
        logger.error(f"Error serving graph data: {e}", exc_info=True)
        return JSONResponse(
            {"nodes": [], "edges": [], "error": str(e)}, status_code=500
        )


async def task_tree_data_api_route(request: Request) -> JSONResponse:
    # // ... (implementation from previous response)
    try:
        data = await fetch_task_tree_data_logic()
        return JSONResponse(data)
    except Exception as e:
        logger.error(f"Error serving task tree data: {e}", exc_info=True)
        return JSONResponse(
            {"nodes": [], "edges": [], "error": str(e)}, status_code=500
        )


async def node_details_api_route(request: Request) -> JSONResponse:
    # // ... (implementation from previous response)
    node_id = request.query_params.get("node_id")
    if not node_id:
        return JSONResponse({"error": "Missing node_id parameter"}, status_code=400)
    details: Dict[str, Any] = {
        "id": node_id,
        "type": "unknown",
        "data": {},
        "actions": [],
        "related": {},
    }
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        parts = node_id.split("_", 1)
        node_type_from_id = parts[0] if len(parts) > 1 else node_id
        actual_id_from_node = (
            parts[1]
            if len(parts) > 1
            else (node_id if node_type_from_id != "admin" else "admin")
        )
        details["type"] = node_type_from_id
        if node_type_from_id == "agent":
            cursor.execute(
                "SELECT * FROM agents WHERE agent_id = ?", (actual_id_from_node,)
            )
            row = cursor.fetchone()
            if row:
                details["data"] = dict(row)
            cursor.execute(
                "SELECT timestamp, action_type, task_id, details FROM agent_actions WHERE agent_id = ? ORDER BY timestamp DESC LIMIT 10",
                (actual_id_from_node,),
            )
            details["actions"] = [dict(r) for r in cursor.fetchall()]
            cursor.execute(
                "SELECT task_id, title, status, priority FROM tasks WHERE assigned_to = ? ORDER BY created_at DESC LIMIT 10",
                (actual_id_from_node,),
            )
            details["related"]["assigned_tasks"] = [dict(r) for r in cursor.fetchall()]
        elif node_type_from_id == "task":
            cursor.execute(
                "SELECT * FROM tasks WHERE task_id = ?", (actual_id_from_node,)
            )
            row = cursor.fetchone()
            if row:
                details["data"] = dict(row)
            cursor.execute(
                "SELECT timestamp, agent_id, action_type, details FROM agent_actions WHERE task_id = ? ORDER BY timestamp DESC LIMIT 10",
                (actual_id_from_node,),
            )
            details["actions"] = [dict(r) for r in cursor.fetchall()]
        elif node_type_from_id == "context":
            cursor.execute(
                "SELECT * FROM project_context WHERE context_key = ?",
                (actual_id_from_node,),
            )
            row = cursor.fetchone()
            if row:
                details["data"] = dict(row)
            cursor.execute(
                "SELECT timestamp, agent_id, action_type FROM agent_actions WHERE (action_type = 'updated_context' OR action_type = 'update_project_context') AND details LIKE ? ORDER BY timestamp DESC LIMIT 5",
                (f'%"{actual_id_from_node}"%',),
            )
            details["actions"] = [dict(r) for r in cursor.fetchall()]
        elif node_type_from_id == "file":
            details["data"] = {
                "filepath": actual_id_from_node,
                "info": g.file_map.get(actual_id_from_node, {}),
            }
            cursor.execute(
                "SELECT timestamp, agent_id, action_type, details FROM agent_actions WHERE (action_type LIKE '%_file' OR action_type LIKE 'claim_file_%' OR action_type = 'release_file') AND details LIKE ? ORDER BY timestamp DESC LIMIT 5",
                (f'%"{actual_id_from_node}"%',),
            )
            details["actions"] = [dict(r) for r in cursor.fetchall()]
        elif node_type_from_id == "admin":
            details["data"] = {"name": "Admin User / System"}
            cursor.execute(
                "SELECT timestamp, action_type, task_id, details FROM agent_actions WHERE agent_id = 'admin' ORDER BY timestamp DESC LIMIT 10"
            )
            details["actions"] = [dict(r) for r in cursor.fetchall()]
        if not details.get("data") and node_type_from_id not in ["admin"]:
            return JSONResponse(
                {"error": "Node data not found or type unrecognized"}, status_code=404
            )
    except Exception as e:
        logger.error(f"Error fetching details for node {node_id}: {e}", exc_info=True)
        return JSONResponse(
            {"error": f"Failed to fetch node details: {str(e)}"}, status_code=500
        )
    finally:
        if conn:
            conn.close()
    return JSONResponse(details)


async def agents_list_api_route(request: Request) -> JSONResponse:
    # // ... (implementation from previous response)
    agents_list_data: List[Dict[str, Any]] = []
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        admin_style = get_node_style("admin")
        agents_list_data.append(
            {
                "agent_id": "Admin",
                "status": "system",
                "color": admin_style.get("color", "#607D8B"),
                "created_at": "N/A",
                "current_task": "N/A",
            }
        )
        cursor.execute(
            "SELECT agent_id, status, color, created_at, current_task FROM agents ORDER BY created_at DESC"
        )
        for row in cursor.fetchall():
            agents_list_data.append(dict(row))
    except Exception as e:
        logger.error(f"Error fetching agents list: {e}", exc_info=True)
        return JSONResponse(
            {"error": f"Failed to fetch agents list: {str(e)}"}, status_code=500
        )
    finally:
        if conn:
            conn.close()
    return JSONResponse(agents_list_data)


async def tokens_api_route(request: Request) -> JSONResponse:
    # // ... (implementation from previous response)
    try:
        agent_tokens_list = []
        for token, data in g.active_agents.items():
            if data.get("status") != "terminated":
                agent_tokens_list.append(
                    {"agent_id": data.get("agent_id"), "token": token}
                )
        return JSONResponse(
            {"admin_token": g.admin_token, "agent_tokens": agent_tokens_list}
        )
    except Exception as e:
        logger.error(f"Error retrieving tokens for dashboard: {e}", exc_info=True)
        return JSONResponse(
            {"error": f"Error retrieving tokens: {str(e)}"}, status_code=500
        )


async def all_tasks_api_route(request: Request) -> JSONResponse:
    # // ... (implementation from previous response)
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        tasks_data = [dict(row) for row in cursor.fetchall()]
        return JSONResponse(tasks_data)
    except Exception as e:
        logger.error(f"Error fetching all tasks: {e}", exc_info=True)
        return JSONResponse(
            {"error": f"Failed to fetch all tasks: {str(e)}"}, status_code=500
        )
    finally:
        if conn:
            conn.close()


async def update_task_details_api_route(request: Request) -> JSONResponse:
    # // ... (implementation from previous response)
    if request.method != "POST":
        return JSONResponse({"error": "Method not allowed"}, status_code=405)
    conn = None
    try:
        data = await get_sanitized_json_body(request)
        admin_auth_token = data.get("token")
        task_id_to_update = data.get("task_id")
        new_status = data.get("status")
        if not task_id_to_update or not new_status:
            return JSONResponse(
                {"error": "task_id and status are required fields."}, status_code=400
            )
        if not verify_token(admin_auth_token, required_role="admin"):
            return JSONResponse({"error": "Invalid admin token"}, status_code=403)
        requesting_admin_id = auth_get_agent_id(admin_auth_token)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT notes FROM tasks WHERE task_id = ?", (task_id_to_update,)
        )
        task_row = cursor.fetchone()
        if not task_row:
            return JSONResponse({"error": "Task not found"}, status_code=404)
        existing_notes_str = task_row["notes"]
        update_fields: List[str] = []
        params: List[Any] = []
        log_details: Dict[str, Any] = {"status_updated_to": new_status}
        update_fields.append("status = ?")
        params.append(new_status)
        update_fields.append("updated_at = ?")
        params.append(datetime.datetime.now().isoformat())
        if "title" in data and data["title"] is not None:
            update_fields.append("title = ?")
            params.append(data["title"])
            log_details["title_changed"] = True
        if "description" in data and data["description"] is not None:
            update_fields.append("description = ?")
            params.append(data["description"])
            log_details["description_changed"] = True
        if "priority" in data and data["priority"]:
            update_fields.append("priority = ?")
            params.append(data["priority"])
            log_details["priority_changed"] = True
        if (
            "notes" in data
            and data["notes"]
            and isinstance(data["notes"], str)
            and data["notes"].strip()
        ):
            try:
                current_notes_list = json.loads(existing_notes_str or "[]")
            except json.JSONDecodeError:
                current_notes_list = []
            new_note_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "author": requesting_admin_id,
                "content": data["notes"].strip(),
            }
            current_notes_list.append(new_note_entry)
            update_fields.append("notes = ?")
            params.append(json.dumps(current_notes_list))
            log_details["notes_added"] = True
        params.append(task_id_to_update)
        if update_fields:
            placeholders = ", ".join(update_fields)
            query = f"UPDATE tasks SET {placeholders} WHERE task_id = ?"
            cursor.execute(query, tuple(params))
        log_agent_action_to_db(
            cursor,
            requesting_admin_id,
            "updated_task_dashboard",
            task_id=task_id_to_update,
            details=log_details,
        )
        conn.commit()
        if task_id_to_update in g.tasks:
            cursor.execute(
                "SELECT * FROM tasks WHERE task_id = ?", (task_id_to_update,)
            )
            updated_task_for_cache = cursor.fetchone()
            if updated_task_for_cache:
                g.tasks[task_id_to_update] = dict(updated_task_for_cache)
                for field_key in ["child_tasks", "depends_on_tasks", "notes"]:
                    if isinstance(g.tasks[task_id_to_update].get(field_key), str):
                        try:
                            g.tasks[task_id_to_update][field_key] = json.loads(
                                g.tasks[task_id_to_update][field_key] or "[]"
                            )
                        except json.JSONDecodeError:
                            g.tasks[task_id_to_update][field_key] = []
            else:
                del g.tasks[task_id_to_update]
        return JSONResponse(
            {"success": True, "message": "Task updated successfully via dashboard."}
        )
    except ValueError as e_val:
        return JSONResponse({"error": str(e_val)}, status_code=400)
    except sqlite3.Error as e_sql:
        if conn:
            conn.rollback()
        logger.error(f"DB error updating task via dashboard: {e_sql}", exc_info=True)
        return JSONResponse(
            {"error": f"Failed to update task (DB): {str(e_sql)}"}, status_code=500
        )
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error updating task via dashboard: {e}", exc_info=True)
        return JSONResponse(
            {"error": f"Failed to update task: {str(e)}"}, status_code=500
        )
    finally:
        if conn:
            conn.close()


# --- ADDED: Dashboard-specific Agent Management API Endpoints ---


# Original: main.py lines 2022-2058 (create_agent_api function)
async def create_agent_dashboard_api_route(request: Request) -> JSONResponse:
    """Dashboard API endpoint to create an agent. Calls the admin tool internally."""
    if request.method != "POST":
        return JSONResponse({"error": "Method not allowed"}, status_code=405)
    try:
        data = await get_sanitized_json_body(request)
        admin_auth_token = data.get("token")
        agent_id = data.get("agent_id")
        capabilities = data.get("capabilities", [])  # Optional
        working_directory = data.get("working_directory")  # Optional

        # This endpoint itself requires admin authentication
        if not verify_token(admin_auth_token, "admin"):
            return JSONResponse(
                {"message": "Unauthorized: Invalid admin token for API call"},
                status_code=401,
            )

        if not agent_id:
            return JSONResponse({"message": "Agent ID is required"}, status_code=400)

        # Prepare arguments for the create_agent_tool_impl
        tool_args = {
            "token": admin_auth_token,  # The tool_impl will verify this again
            "agent_id": agent_id,
            "capabilities": capabilities,
            "working_directory": working_directory,
            "task_ids": data.get("task_ids", []),  # Adicionado
            "prompt_template": data.get("prompt_template"),  # Adicionado
        }

        # Call the already refactored tool implementation
        result_list: List[mcp_types.TextContent] = await create_agent_tool_impl(
            tool_args
        )

        # Process the result from tool_impl to form a JSONResponse
        # The tool_impl returns a list of TextContent objects.
        # The original API returned a simple JSON message.
        if result_list and result_list[0].text.startswith(
            f"Agent '{agent_id}' created successfully."
        ):
            # Extract token if possible for dashboard convenience (original API did this)
            # This is a bit fragile as it relies on string parsing of the tool's output.
            agent_token_from_result = None
            for line in result_list[0].text.split("\n"):
                if line.startswith("Token: "):
                    agent_token_from_result = line.split("Token: ", 1)[1]
                    break
            return JSONResponse(
                {
                    "message": f"Agent '{agent_id}' created successfully via dashboard API.",
                    "agent_token": agent_token_from_result,  # May be None if not parsed
                }
            )
        else:
            # Return the error message from the tool
            error_message = (
                result_list[0].text if result_list else "Unknown error creating agent."
            )
            # Determine appropriate status code based on error message
            status_code = 400  # Default bad request
            if "Unauthorized" in error_message:
                status_code = 401
            if "already exists" in error_message:
                status_code = 409  # Conflict
            return JSONResponse({"message": error_message}, status_code=status_code)

    except ValueError as e_val:  # From get_sanitized_json_body
        return JSONResponse({"message": str(e_val)}, status_code=400)
    except Exception as e:
        logger.error(f"Error in create_agent_dashboard_api_route: {e}", exc_info=True)
        return JSONResponse(
            {"message": f"Error creating agent via dashboard API: {str(e)}"},
            status_code=500,
        )


# Original: main.py lines 2061-2099 (terminate_agent_api function)
async def terminate_agent_dashboard_api_route(request: Request) -> JSONResponse:
    """Dashboard API endpoint to terminate an agent. Calls the admin tool internally."""
    if request.method != "POST":
        return JSONResponse({"error": "Method not allowed"}, status_code=405)
    try:
        data = await get_sanitized_json_body(request)
        admin_auth_token = data.get("token")
        agent_id_to_terminate = data.get("agent_id")

        if not verify_token(admin_auth_token, "admin"):
            return JSONResponse(
                {"message": "Unauthorized: Invalid admin token for API call"},
                status_code=401,
            )

        if not agent_id_to_terminate:
            return JSONResponse(
                {"message": "Agent ID to terminate is required"}, status_code=400
            )

        tool_args = {
            "token": admin_auth_token,  # Tool impl will verify again
            "agent_id": agent_id_to_terminate,
        }

        result_list: List[mcp_types.TextContent] = await terminate_agent_tool_impl(
            tool_args
        )

        if result_list and result_list[0].text.startswith(
            f"Agent '{agent_id_to_terminate}' terminated"
        ):
            return JSONResponse(
                {
                    "message": f"Agent '{agent_id_to_terminate}' terminated successfully via dashboard API."
                }
            )
        else:
            error_message = (
                result_list[0].text
                if result_list
                else "Unknown error terminating agent."
            )
            status_code = 400
            if "Unauthorized" in error_message:
                status_code = 401
            if "not found" in error_message:
                status_code = 404
            return JSONResponse({"message": error_message}, status_code=status_code)

    except ValueError as e_val:  # From get_sanitized_json_body
        return JSONResponse({"message": str(e_val)}, status_code=400)
    except Exception as e:
        logger.error(
            f"Error in terminate_agent_dashboard_api_route: {e}", exc_info=True
        )
        return JSONResponse(
            {"message": f"Error terminating agent via dashboard API: {str(e)}"},
            status_code=500,
        )


# --- Comprehensive Data Endpoint ---
async def all_data_api_route(request: Request) -> JSONResponse:
    """Get all data in one call for caching on frontend"""
    if request.method == "OPTIONS":
        return await handle_options(request)

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get all agents with their tokens
        cursor.execute("SELECT * FROM agents ORDER BY created_at DESC")
        agents_data = []
        for row in cursor.fetchall():
            agent_dict = dict(row)
            agent_id = agent_dict["agent_id"]

            # Find token for this agent from active_agents
            agent_token = None
            for token, data in g.active_agents.items():
                if (
                    data.get("agent_id") == agent_id
                    and data.get("status") != "terminated"
                ):
                    agent_token = token
                    break

            agent_dict["auth_token"] = agent_token
            agents_data.append(agent_dict)

        # Add admin as special agent
        agents_data.insert(
            0,
            {
                "agent_id": "Admin",
                "status": "system",
                "auth_token": g.admin_token,
                "created_at": "N/A",
                "current_task": "N/A",
            },
        )

        # Get all tasks
        cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        tasks_data = [dict(row) for row in cursor.fetchall()]

        # Get all context entries
        cursor.execute("SELECT * FROM project_context ORDER BY last_updated DESC")
        context_data = [dict(row) for row in cursor.fetchall()]

        # Get recent agent actions (last 100)
        cursor.execute("""
            SELECT * FROM agent_actions 
            ORDER BY timestamp DESC 
            LIMIT 100
        """)
        actions_data = [dict(row) for row in cursor.fetchall()]

        # Get file metadata
        cursor.execute("SELECT * FROM file_metadata")
        file_metadata = [dict(row) for row in cursor.fetchall()]

        response_data = {
            "agents": agents_data,
            "tasks": tasks_data,
            "context": context_data,
            "actions": actions_data,
            "file_metadata": file_metadata,
            "file_map": g.file_map,
            "admin_token": g.admin_token,
            "timestamp": datetime.datetime.now().isoformat(),
        }

        return JSONResponse(
            response_data,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        )

    except Exception as e:
        logger.error(f"Error fetching all data: {e}", exc_info=True)
        return JSONResponse(
            {"error": f"Failed to fetch all data: {str(e)}"}, status_code=500
        )
    finally:
        if conn:
            conn.close()


async def context_data_api_route(request: Request) -> JSONResponse:
    """Get only context data"""
    if request.method == "OPTIONS":
        return await handle_options(request)

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get all context entries
        cursor.execute("SELECT * FROM project_context ORDER BY last_updated DESC")
        context_data = [dict(row) for row in cursor.fetchall()]

        return JSONResponse(
            context_data,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        )

    except Exception as e:
        logger.error(f"Error fetching context data: {e}", exc_info=True)
        return JSONResponse(
            {"error": f"Failed to fetch context data: {str(e)}"}, status_code=500
        )
    finally:
        if conn:
            conn.close()


# --- CORS Preflight Handler ---
async def handle_options(request: Request) -> Response:
    """Handle OPTIONS requests for CORS preflight"""
    return PlainTextResponse(
        "",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "86400",
        },
    )


# As definições de rota foram movidas para uma lista consolidada no final do arquivo.


# --- System Monitoring Endpoints (LEGACY - A ser removido) ---
async def system_usage_route(request: Request) -> JSONResponse:
    """API endpoint to get system usage, calling the internal tool."""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    # The tool's implementation handles token verification
    from .os_tools import get_system_usage_impl

    result = await get_system_usage_impl({"token": token})

    if "Unauthorized" in result[0].text:
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    if "Error" in result[0].text:
        return JSONResponse({"error": result[0].text}, status_code=500)

    # Parse the text response into a structured JSON
    try:
        lines = result[0].text.split("\n")
        cpu_line = lines[1]
        mem_line = lines[2]
        disk_line = lines[3]

        data = {
            "cpu_percent": float(cpu_line.split(":")[1].strip().replace("%", "")),
            "memory_percent": float(
                mem_line.split(":")[1].strip().split(" ")[0].replace("%", "")
            ),
            "disk_percent": float(
                disk_line.split(":")[1].strip().split(" ")[0].replace("%", "")
            ),
            "raw_text": result[0].text,
        }
        return JSONResponse(data)
    except Exception as e:
        return JSONResponse(
            {"error": f"Failed to parse usage data: {e}", "raw": result[0].text},
            status_code=500,
        )


# As definições de rota foram movidas para uma lista consolidada no final do arquivo.


# --- On-Demand Service Activation ---
async def kickstart_autonomy_route(request: Request) -> JSONResponse:
    """Starts the autonomous researcher if it hasn't been started yet."""
    if request.method != "POST":
        return JSONResponse({"error": "Method not allowed"}, status_code=405)

    try:
        # This is a sensitive operation, requires admin token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not verify_token(token, required_role="admin"):
            return JSONResponse(
                {"error": "Unauthorized: Invalid admin token"}, status_code=403
            )

        if g.autonomous_research_task_scope is not None:
            return JSONResponse(
                {
                    "status": "already_running",
                    "message": "Autonomous researcher is already active.",
                },
                status_code=200,
            )

        if g.main_task_group is None:
            logger.error(
                "Cannot start autonomous researcher: main task group not available."
            )
            return JSONResponse(
                {"error": "Server in inconsistent state: Main task group not found."},
                status_code=500,
            )

        from ..features.autonomous_researcher import run_autonomous_research_loop

        researcher_interval = int(
            os.environ.get("MCP_AUTONOMOUS_RESEARCH_INTERVAL_SECONDS", "3600")
        )

        # Use start_soon as we are adding a task to an already running group
        g.autonomous_research_task_scope = g.main_task_group.start_soon(
            run_autonomous_research_loop, researcher_interval
        )

        logger.info(
            f"Autonomous researcher task started on-demand with interval {researcher_interval}s."
        )

        return JSONResponse(
            {
                "status": "started",
                "message": "Autonomous researcher has been activated.",
            }
        )

    except Exception as e:
        logger.error(f"Error in kickstart_autonomy_route: {e}", exc_info=True)
        return JSONResponse(
            {"error": f"Failed to start autonomous researcher: {str(e)}"},
            status_code=500,
        )


# As definições de rota foram movidas para uma lista consolidada no final do arquivo.


# --- OpenAI-Compatible Endpoints ---

async def models_endpoint(request: Request) -> JSONResponse:
    """
    OpenAI-compatible endpoint to list available models.
    """
    # This provides the model info that Continue/Cursor uses to list the model.
    model_data = {
        "object": "list",
        "data": [
            {
                "id": "genesys-local",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "genesys",
            }
        ],
    }
    return JSONResponse(model_data)


async def chat_completions_endpoint(request: Request) -> Response:
    """
    OpenAI-compatible endpoint for chat completions.
    Supports both standard and streaming responses.
    """
    if g.genesys_agent_instance is None or not g.genesys_agent_instance.is_loaded:
        return JSONResponse(
            status_code=503,
            content={
                "error": "Model not loaded",
                "message": "The Genesys local model is not ready. Please try again in a moment.",
            },
        )

    try:
        body = await request.json()
        model_name = body.get("model", "genesys-local")
        messages = body.get("messages", [])
        stream = body.get("stream", False)

        if not messages:
            return JSONResponse(
                status_code=400,
                content={"error": "The 'messages' list cannot be empty."},
            )

        last_message = messages[-1].get("content", "")

        if not stream:
            # Comportamento original: resposta única e completa
            response_text = await g.genesys_agent_instance.process_task(last_message)
            return JSONResponse(
                {
                    "id": f"chatcmpl-{uuid.uuid4()}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": model_name,
                    "choices": [
                        {
                            "index": 0,
                            "message": {"role": "assistant", "content": response_text},
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {
                        "prompt_tokens": len(last_message.split()),
                        "completion_tokens": len(response_text.split()),
                        "total_tokens": len(last_message.split())
                        + len(response_text.split()),
                    },
                }
            )
        else:
            # Novo comportamento: resposta via streaming
            async def stream_generator():
                completion_id = f"chatcmpl-{uuid.uuid4()}"
                created_time = int(time.time())
                
                try:
                    # Chama o novo método de streaming do agente
                    token_stream = g.genesys_agent_instance.stream_task(last_message)
                    
                    async for token in token_stream:
                        if not token:
                            continue
                        
                        # Formata o chunk no padrão OpenAI SSE
                        chunk = {
                            "id": completion_id,
                            "object": "chat.completion.chunk",
                            "created": created_time,
                            "model": model_name,
                            "choices": [
                                {
                                    "index": 0,
                                    "delta": {"content": token},
                                    "finish_reason": None,
                                }
                            ],
                        }
                        yield f"data: {json.dumps(chunk)}\n\n"
                        await asyncio.sleep(0.01) # Pequeno sleep para o event loop

                    # Envia o chunk final de terminação
                    final_chunk = {
                        "id": completion_id,
                        "object": "chat.completion.chunk",
                        "created": created_time,
                        "model": model_name,
                        "choices": [
                            {
                                "index": 0,
                                "delta": {},
                                "finish_reason": "stop",
                            }
                        ],
                    }
                    yield f"data: {json.dumps(final_chunk)}\n\n"
                    
                    # Envia a mensagem de finalização do stream
                    yield "data: [DONE]\n\n"

                except Exception as e:
                    logger.error(f"Erro fatal no gerador de stream: {e}", exc_info=True)
                    error_chunk = {
                         "id": completion_id,
                         "object": "chat.completion.chunk",
                         "created": created_time,
                         "model": model_name,
                         "choices": [
                             {
                                 "index": 0,
                                 "delta": {"content": f"\n\n[ERRO]: {str(e)}"},
                                 "finish_reason": "error",
                             }
                         ],
                    }
                    yield f"data: {json.dumps(error_chunk)}\n\n"
                    yield "data: [DONE]\n\n"

            return StreamingResponse(
                stream_generator(), media_type="text/event-stream"
            )

    except Exception as e:
        logger.error(f"Error in chat completions endpoint: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "message": f"Internal server error: {str(e)}",
                    "type": "internal_error",
                }
            },
        )

# As definições de rota foram movidas para uma lista consolidada no final do arquivo.


# --- Test/Demo Data Endpoint ---
async def create_sample_memories_route(request: Request) -> JSONResponse:
    """Create sample memory entries for testing"""
    if request.method == "OPTIONS":
        return await handle_options(request)

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Sample memory entries
        sample_memories = [
            {
                "context_key": "api.config.base_url",
                "value": json.dumps("https://api.example.com"),
                "description": "Main API base URL for external services",
                "updated_by": "system",
            },
            {
                "context_key": "app.settings.theme",
                "value": json.dumps({"theme": "dark", "accent": "blue"}),
                "description": "Application theme preferences",
                "updated_by": "admin",
            },
            {
                "context_key": "database.connection.timeout",
                "value": json.dumps(30),
                "description": "Database connection timeout in seconds",
                "updated_by": "system",
            },
            {
                "context_key": "cache.redis.config",
                "value": json.dumps({"host": "localhost", "port": 6379, "ttl": 3600}),
                "description": "Redis cache configuration",
                "updated_by": "admin",
            },
        ]

        current_time = datetime.datetime.now().isoformat()
        created_count = 0

        for memory in sample_memories:
            cursor.execute(
                """
                INSERT OR REPLACE INTO project_context (context_key, value, last_updated, updated_by, description)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    memory["context_key"],
                    memory["value"],
                    current_time,
                    memory["updated_by"],
                    memory["description"],
                ),
            )
            created_count += 1

        conn.commit()

        return JSONResponse(
            {
                "success": True,
                "message": f"Created {created_count} sample memory entries",
                "created_count": created_count,
            }
        )

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error creating sample memories: {e}", exc_info=True)
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)
    finally:
        if conn:
            conn.close()


# Memory CRUD API endpoints
async def create_memory_api_route(request: Request) -> JSONResponse:
    """Create a new memory entry"""
    if request.method == "OPTIONS":
        return await handle_options(request)

    if request.method != "POST":
        return JSONResponse({"error": "Method not allowed"}, status_code=405)

    conn = None
    try:
        data = await get_sanitized_json_body(request)
        admin_token = data.get("token")
        context_key = data.get("context_key")
        context_value = data.get("context_value")
        description = data.get("description")

        if not verify_token(admin_token, required_role="admin"):
            return JSONResponse({"error": "Invalid admin token"}, status_code=403)

        if not context_key:
            return JSONResponse({"error": "context_key is required"}, status_code=400)

        requesting_admin_id = auth_get_agent_id(admin_token)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if key already exists
        cursor.execute(
            "SELECT context_key FROM project_context WHERE context_key = ?",
            (context_key,),
        )
        if cursor.fetchone():
            return JSONResponse(
                {"error": "Memory with this key already exists"}, status_code=409
            )

        current_time = datetime.datetime.now().isoformat()

        cursor.execute(
            """
            INSERT INTO project_context (context_key, value, last_updated, updated_by, description)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                context_key,
                json.dumps(context_value),
                current_time,
                requesting_admin_id,
                description,
            ),
        )

        # Log the action
        log_agent_action_to_db(
            cursor,
            requesting_admin_id,
            "created_memory",
            details={"context_key": context_key},
        )
        conn.commit()

        return JSONResponse(
            {"success": True, "message": f"Memory '{context_key}' created successfully"}
        )

    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error creating memory: {e}", exc_info=True)
        return JSONResponse(
            {"error": f"Failed to create memory: {str(e)}"}, status_code=500
        )
    finally:
        if conn:
            conn.close()


async def update_memory_api_route(request: Request) -> JSONResponse:
    """Update an existing memory entry"""
    if request.method == "OPTIONS":
        return await handle_options(request)

    if request.method != "PUT":
        return JSONResponse({"error": "Method not allowed"}, status_code=405)

    # Extract context_key from URL path
    path_parts = request.url.path.split("/")
    if len(path_parts) < 4 or not path_parts[-1]:
        return JSONResponse(
            {"error": "context_key is required in URL"}, status_code=400
        )

    context_key = path_parts[-1]

    conn = None
    try:
        data = await get_sanitized_json_body(request)
        admin_token = data.get("token")
        context_value = data.get("context_value")
        description = data.get("description")

        if not verify_token(admin_token, required_role="admin"):
            return JSONResponse({"error": "Invalid admin token"}, status_code=403)

        requesting_admin_id = auth_get_agent_id(admin_token)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if memory exists
        cursor.execute(
            "SELECT context_key FROM project_context WHERE context_key = ?",
            (context_key,),
        )
        if not cursor.fetchone():
            return JSONResponse({"error": "Memory not found"}, status_code=404)

        current_time = datetime.datetime.now().isoformat()

        # Build update query dynamically
        update_fields = ["last_updated = ?", "updated_by = ?"]
        params = [current_time, requesting_admin_id]

        if context_value is not None:
            update_fields.append("value = ?")
            params.append(json.dumps(context_value))

        if description is not None:
            update_fields.append("description = ?")
            params.append(description)

        params.append(context_key)

        query = f"UPDATE project_context SET {', '.join(update_fields)} WHERE context_key = ?"
        cursor.execute(query, params)

        # Log the action
        log_agent_action_to_db(
            cursor,
            requesting_admin_id,
            "updated_memory",
            details={"context_key": context_key},
        )
        conn.commit()

        return JSONResponse(
            {"success": True, "message": f"Memory '{context_key}' updated successfully"}
        )

    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error updating memory: {e}", exc_info=True)
        return JSONResponse(
            {"error": f"Failed to update memory: {str(e)}"}, status_code=500
        )
    finally:
        if conn:
            conn.close()


async def delete_memory_api_route(request: Request) -> JSONResponse:
    """Delete a memory entry"""
    if request.method == "OPTIONS":
        return await handle_options(request)

    if request.method != "DELETE":
        return JSONResponse({"error": "Method not allowed"}, status_code=405)

    # Extract context_key from URL path
    path_parts = request.url.path.split("/")
    if len(path_parts) < 4 or not path_parts[-1]:
        return JSONResponse(
            {"error": "context_key is required in URL"}, status_code=400
        )

    context_key = path_parts[-1]

    conn = None
    try:
        data = await get_sanitized_json_body(request)
        admin_token = data.get("token")

        if not verify_token(admin_token, required_role="admin"):
            return JSONResponse({"error": "Invalid admin token"}, status_code=403)

        requesting_admin_id = auth_get_agent_id(admin_token)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if memory exists
        cursor.execute(
            "SELECT context_key FROM project_context WHERE context_key = ?",
            (context_key,),
        )
        if not cursor.fetchone():
            return JSONResponse({"error": "Memory not found"}, status_code=404)

        # Delete the memory
        cursor.execute(
            "DELETE FROM project_context WHERE context_key = ?", (context_key,)
        )

        # Log the action
        log_agent_action_to_db(
            cursor,
            requesting_admin_id,
            "deleted_memory",
            details={"context_key": context_key},
        )
        conn.commit()

        return JSONResponse(
            {"success": True, "message": f"Memory '{context_key}' deleted successfully"}
        )

    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error deleting memory: {e}", exc_info=True)
        return JSONResponse(
            {"error": f"Failed to delete memory: {str(e)}"}, status_code=500
        )
    finally:
        if conn:
            conn.close()


# Add the memory CRUD routes
# As definições de rota foram movidas para uma lista consolidada no final do arquivo.

# Add the sample data route
# As definições de rota foram movidas para uma lista consolidada no final do arquivo.

# --- Service Management Endpoints ---


async def start_genesys_route(request: Request) -> JSONResponse:
    """API endpoint to start the Genesys Agent subprocess."""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not verify_token(token, required_role="admin"):
        return JSONResponse(
            {"error": "Unauthorized: Invalid admin token"}, status_code=403
        )

    result = start_genesys_process()
    status_code = 200 if result["status"] in ["started", "already_running"] else 500
    return JSONResponse(result, status_code=status_code)


async def stop_genesys_route(request: Request) -> JSONResponse:
    """API endpoint to stop the Genesys Agent subprocess."""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not verify_token(token, required_role="admin"):
        return JSONResponse(
            {"error": "Unauthorized: Invalid admin token"}, status_code=403
        )

    result = stop_genesys_process()
    status_code = (
        200 if result["status"] in ["stopped", "not_running", "not_found"] else 500
    )
    return JSONResponse(result, status_code=status_code)


async def genesys_status_route(request: Request) -> JSONResponse:
    """API endpoint to get the status of the Genesys Agent subprocess."""
    # This endpoint can be less restricted if desired, but let's keep it admin-only for now
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not verify_token(token, required_role="admin"):
        return JSONResponse(
            {"error": "Unauthorized: Invalid admin token"}, status_code=403
        )

    status = get_genesys_status()
    return JSONResponse(status)

# --- Lista Final e Consolidada de Rotas ---
# Todas as rotas são adicionadas a uma única lista para garantir
# que sejam exportadas corretamente para o main_app.
routes = [
    # --- Rotas do Dashboard Principal ---
    Route("/api/all-data", endpoint=all_data_api_route, name="all_data_api", methods=["GET", "OPTIONS"]),
    Route("/api/status", endpoint=simple_status_api_route, name="simple_status_api", methods=["GET", "OPTIONS"]),
    Route("/api/graph-data", endpoint=graph_data_api_route, name="graph_data_api", methods=["GET", "OPTIONS"]),
    Route("/api/task-tree-data", endpoint=task_tree_data_api_route, name="task_tree_data_api", methods=["GET", "OPTIONS"]),
    Route("/api/node-details", endpoint=node_details_api_route, name="node_details_api", methods=["GET", "OPTIONS"]),
    Route("/api/tasks", endpoint=all_tasks_api_route, name="all_tasks_api", methods=["GET", "OPTIONS"]),
    Route("/api/update-task-dashboard", endpoint=update_task_details_api_route, name="update_task_dashboard_api", methods=["POST", "OPTIONS"]),

    # --- Rotas de Gerenciamento de Agentes (Dashboard) ---
    Route("/api/dashboard/agents", endpoint=list_agents_api_route, name="list_agents_api", methods=["GET", "OPTIONS"]),
    Route("/api/dashboard/agents", endpoint=create_agent_dashboard_api_route, name="create_agent_dashboard_api", methods=["POST", "OPTIONS"]),
    Route("/api/dashboard/agents/{agent_id}", endpoint=delete_agent_api_route, name="delete_agent_api", methods=["DELETE", "OPTIONS"]),
    Route("/api/terminate-agent", endpoint=terminate_agent_dashboard_api_route, name="terminate_agent_dashboard_api_legacy", methods=["POST", "OPTIONS"]),

    # --- Rotas de Gerenciamento de Memória (Dashboard) ---
    Route("/api/memories", endpoint=create_memory_api_route, name="create_memory_api", methods=["POST", "OPTIONS"]),
    Route("/api/memories/{context_key}", endpoint=update_memory_api_route, name="update_memory_api", methods=["PUT", "OPTIONS"]),
    Route("/api/memories/{context_key}", endpoint=delete_memory_api_route, name="delete_memory_api", methods=["DELETE", "OPTIONS"]),
    Route("/api/context-data", endpoint=context_data_api_route, name="context_data_api", methods=["GET", "OPTIONS"]),
    Route("/api/create-sample-memories", endpoint=create_sample_memories_route, name="create_sample_memories", methods=["POST", "OPTIONS"]),

    # --- Rotas de Métricas e Status (Dashboard) ---
    Route("/api/dashboard/system-metrics", endpoint=system_metrics_api_route, name="system_metrics_api", methods=["GET", "OPTIONS"]),
    Route("/api/dashboard/service-status", endpoint=service_status_api_route, name="service_status_api", methods=["GET", "OPTIONS"]),
    Route("/api/dashboard/service-control", endpoint=service_control_api_route, name="service_control_api", methods=["POST", "OPTIONS"]),
    Route("/api/dashboard/recent-activity", endpoint=recent_activity_api_route, name="recent_activity_api", methods=["GET", "OPTIONS"]),
    
    # --- Rotas de Serviço Genesys ---
    Route("/api/service/genesys/start", endpoint=start_genesys_route, name="start_genesys_service", methods=["POST", "OPTIONS"]),
    Route("/api/service/genesys/stop", endpoint=stop_genesys_route, name="stop_genesys_service", methods=["POST", "OPTIONS"]),
    Route("/api/service/genesys/status", endpoint=genesys_status_route, name="status_genesys_service", methods=["GET", "OPTIONS"]),

    # --- Rotas Compatíveis com OpenAI (Continue/Cursor) ---
    Route("/v1/models", endpoint=models_endpoint, methods=["GET", "OPTIONS"]),
    Route("/v1/chat/completions", endpoint=chat_completions_endpoint, methods=["POST", "OPTIONS"]),

    # --- Rotas Legadas e de Utilitários ---
    Route("/api/tokens", endpoint=tokens_api_route, name="tokens_api", methods=["GET", "OPTIONS"]),
    Route("/api/kickstart-autonomy", endpoint=kickstart_autonomy_route, name="kickstart_autonomy", methods=["POST", "OPTIONS"]),
    Route("/api/system/usage", endpoint=system_usage_route, name="system_usage_api", methods=["GET", "OPTIONS"]),
    
    # --- Rota Catch-all para Preflight CORS ---
    Route("/api/{path:path}", endpoint=handle_options, methods=["OPTIONS"]),
]

