# app/tools/web_search_tool.py
from langchain.tools import tool
from duckduckgo_search import DDGS

@tool("WebSearch")
def web_search(query: str) -> str:
    """
    Realiza uma pesquisa na web usando o DuckDuckGo para encontrar informações atualizadas.
    Use esta ferramenta para pesquisar documentações, resolver erros ou obter informações sobre eventos recentes.
    Retorna uma lista de resultados.
    """
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=5)]
        
        if not results:
            return "Nenhum resultado encontrado para a sua pesquisa."
            
        # Formata os resultados para serem facilmente compreendidos pelo LLM
        formatted_results = "\n\n".join(
            [f"Título: {res['title']}\nLink: {res['href']}\nResumo: {res['body']}" for res in results]
        )
        return formatted_results
    except Exception as e:
        return f"Ocorreu um erro ao realizar a pesquisa na web: {e}"
