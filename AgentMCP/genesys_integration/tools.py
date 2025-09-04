# AgentMCP/genesys_integration/tools.py
import asyncio
from typing import Dict, Any, List
from duckduckgo_search import AsyncDDGS

async def web_search(query: str, max_results: int = 5) -> str:
    """
    Performs a web search using DuckDuckGo and returns the results.

    Args:
        query: The search query.
        max_results: The maximum number of results to return.

    Returns:
        A formatted string containing the search results.
    """
    results_str = ""
    try:
        async with AsyncDDGS() as ddgs:
            results = []
            async for r in ddgs.text(query, max_results=max_results):
                results.append(r)
            
            if not results:
                return "Nenhum resultado encontrado para a pesquisa."

            for result in results:
                results_str += f"Título: {result.get('title', 'N/A')}\n"
                results_str += f"Link: {result.get('href', 'N/A')}\n"
                results_str += f"Trecho: {result.get('body', 'N/A')}\n\n"
            
            return results_str.strip()
    except Exception as e:
        print(f"❌ Erro durante a pesquisa na web: {e}")
        return f"Erro ao executar a pesquisa: {e}"

# Mock tool definition for local execution and testing.
# In a real scenario, these would be decorated or registered.
AVAILABLE_TOOLS = {
    "web_search": web_search,
}

TOOL_DEFINITIONS = [
    {
        "name": "web_search",
        "description": "Realiza uma pesquisa na web para encontrar informações sobre um tópico, erro ou tecnologia.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "A consulta de pesquisa a ser executada."
                },
                "max_results": {
                    "type": "integer",
                    "description": "O número máximo de resultados a serem retornados.",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }
]

async def execute_tool(tool_name: str, kwargs: Dict[str, Any]) -> str:
    """Executes a tool by its name."""
    if tool_name in AVAILABLE_TOOLS:
        try:
            return await AVAILABLE_TOOLS[tool_name](**kwargs)
        except Exception as e:
            return f"Erro ao executar a ferramenta '{tool_name}': {e}"
    return f"Ferramenta '{tool_name}' não encontrada."

if __name__ == '__main__':
    async def test_search():
        print("Testando a ferramenta de pesquisa na web...")
        search_results = await web_search("O que é a API da OpenAI?")
        print(search_results)
    
    asyncio.run(test_search())
