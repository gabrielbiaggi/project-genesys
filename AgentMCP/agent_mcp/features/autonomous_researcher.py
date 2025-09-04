# Agent-MCP/agent_mcp/features/autonomous_researcher.py
import anyio
import time
import json
import random
from pathlib import Path
from typing import List, Dict, Any, NoReturn

from ..core.config import logger, get_project_dir
from ..core import globals as g
from ..external.openai_service import get_openai_client
from .rag.indexing import simple_chunker # Reutilizar o chunker

try:
    import google.generativeai as genai
except ImportError:
    genai = None

async def store_memory(source_ref: str, content: str, source_type: str = "pesquisa_autonoma"):
    """Armazena o conteúdo pesquisado no banco de dados RAG."""
    from ..db.connection import get_db_connection
    # Implementação simplificada: chunk, embed, e salva.
    # A lógica completa de embedding pode ser refatorada de `indexing.py` para ser reutilizável.
    logger.info(f"Armazenando novo conhecimento sobre: {source_ref}")
    # Por enquanto, esta é uma simulação. A integração real com a fila de escrita do DB e embedding seria necessária.
    pass

async def generate_research_topics() -> List[str]:
    """Gera uma lista de tópicos de pesquisa analisando o projeto."""
    project_dir = get_project_dir()
    topics = set()
    
    # Analisar requirements.txt
    try:
        req_path = project_dir / "requirements.txt"
        if req_path.exists():
            with open(req_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        package = line.split("==")[0].split(">=")[0].split("<=")[0].strip()
                        topics.add(f"Boas práticas e padrões avançados para a biblioteca Python '{package}'")
    except Exception as e:
        logger.warning(f"Não foi possível analisar requirements.txt: {e}")

    # Adicionar tópicos genéricos de engenharia de software
    topics.add("Princípios SOLID aplicados a projetos Python modernos")
    topics.add("Estratégias de otimização de performance em APIs FastAPI")
    topics.add("Padrões de design para sistemas de agentes autônomos")

    return list(topics)

async def run_autonomous_research_loop(interval_seconds: int = 3600, *, task_status=anyio.TASK_STATUS_IGNORED) -> NoReturn:
    """
    Loop de fundo que proativamente pesquisa tópicos para expandir a base de conhecimento.
    """
    logger.info("Loop de Pesquisa Autônoma iniciado.")
    task_status.started()
    
    await anyio.sleep(30) # Atraso inicial

    if not g.openai_client_instance and not genai:
        logger.error("Nenhum cliente LLM (OpenAI/Gemini) configurado. Pesquisador autônomo desativado.")
        return

    while g.server_running:
        try:
            logger.info("Iniciando ciclo de pesquisa autônoma...")
            
            topics = await generate_research_topics()
            if not topics:
                logger.info("Nenhum tópico de pesquisa gerado neste ciclo.")
                continue

            # Escolher um tópico aleatório para pesquisar
            topic_to_research = random.choice(topics)
            logger.info(f"Tópico selecionado para pesquisa: '{topic_to_research}'")

            prompt = f"Como um engenheiro de software especialista, explique em detalhes o seguinte tópico: {topic_to_research}. Forneça exemplos de código quando aplicável."
            
            response_text = ""
            if genai and g.gemini_model: # Priorizar Gemini se configurado
                response = await g.gemini_model.generate_content_async(prompt)
                response_text = response.text
            elif g.openai_client_instance: # Fallback para OpenAI
                response = await g.openai_client_instance.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )
                response_text = response.choices[0].message.content

            if response_text:
                logger.info(f"Pesquisa sobre '{topic_to_research}' concluída. Armazenando conhecimento...")
                await store_memory(topic_to_research, response_text)
            else:
                logger.warning("A pesquisa não retornou conteúdo.")

            # Dormir por um intervalo de tempo (com alguma variação)
            sleep_duration = interval_seconds + random.randint(-300, 300)
            logger.info(f"Ciclo de pesquisa concluído. Próximo ciclo em aproximadamente {sleep_duration / 60:.1f} minutos.")
            await anyio.sleep(sleep_duration)

        except Exception as e:
            logger.error(f"Erro no loop de pesquisa autônoma: {e}", exc_info=True)
            await anyio.sleep(600) # Esperar mais tempo em caso de erro
