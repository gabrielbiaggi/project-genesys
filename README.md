# Genesys: Arquiteto de Código Autônomo

## Visão Geral

Genesys é um sistema de IA avançado projetado para atuar como um arquiteto e desenvolvedor de software sênior. Integrado à plataforma **Agent-MCP (Multi-Agent Commander Platform)**, ele transcende a função de um simples assistente de código, operando como uma entidade autônoma que pode raciocinar, aprender, se auto-corrigir e interagir com o ambiente do sistema.

A arquitetura é composta por três pilares:

1.  **Agent-MCP**: O cérebro e orquestrador do sistema. É um servidor backend que gerencia agentes, tarefas, memória de longo prazo (banco de dados vetorial) e executa os ciclos de aprendizado autônomo.
2.  **Genesys Agent**: A interface de raciocínio. É um servidor FastAPI que expõe um modelo de linguagem local (LLM), aprimorado com a capacidade de delegar tarefas complexas para a API do Gemini. Ele serve como o ponto de entrada para as interações do usuário.
3.  **Cursor (via Extensão Continue)**: A interface do usuário. Através da configuração de um modelo personalizado, a IDE Cursor pode se comunicar diretamente com o Genesys Agent, permitindo uma interação fluida e nativa para desenvolvimento de código.

---

## Funcionalidades Principais

- **Raciocínio Híbrido**: Utiliza um LLM local para tarefas rápidas e a poderosa API do **Gemini 1.5 Pro** para tarefas complexas como análise de arquitetura, refatoração e depuração avançada.
- **Aprendizado Autônomo Proativo**: Após a primeira interação do usuário, o Agent-MCP inicia um loop em background para pesquisar tópicos relevantes, fazer perguntas ao Gemini e enriquecer sua base de conhecimento (RAG) sem intervenção humana.
- **Consciência de Sistema**: Equipado com ferramentas inspiradas no Desktop Commander, o Genesys pode listar processos, verificar o uso de CPU/memória e entender o ambiente em que está operando.
- **Ciclo de Auto-Correção**: Ao encontrar um erro na execução de uma ferramenta, o Genesys não desiste. Ele analisa a mensagem de erro, usa a pesquisa na web para encontrar soluções e tenta uma nova abordagem corrigida de forma autônoma.
- **Acesso Remoto Seguro**: A API do Genesys é projetada para ser exposta de forma segura via túneis (como o Cloudflare), permitindo que você trabalhe e interaja com o agente de qualquer lugar, como um notebook.
- **Dashboard de Super Admin**: Uma interface web completa para monitorar a saúde do sistema em tempo real, gerenciar a memória vetorial do agente, visualizar tarefas e auditar todas as ações.

---

## Guia de Instalação

### Pré-requisitos

- Python 3.9+
- Git
- Node.js e npm (para o dashboard)
- Uma chave de API do Google Gemini

### 1. Configuração do Ambiente

Clone o repositório para a sua máquina local:

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd Genesys
```

### 2. Arquivo de Configuração `.env`

Crie um arquivo `.env` na pasta raiz `AgentMCP/`. Este arquivo centraliza todas as chaves e configurações.

```dotenv
# Agent-MCP/.env

# Chave da API do Google Gemini (Obrigatória para funções avançadas)
GEMINI_API_KEY="sua_chave_aqui"

# Token de administrador para o Agent-MCP (será gerado na primeira execução se não for fornecido)
MCP_ADMIN_TOKEN="opcional_defina_um_token_seguro_aqui"

# URL da API do Agent-MCP (para comunicação interna)
AGENT_MCP_API_URL="http://127.0.0.1:8080"
```

### 3. Instalação das Dependências

O projeto possui dois conjuntos de dependências: um para o orquestrador Agent-MCP e outro para o Genesys Agent.

```bash
# Instalar dependências do Agent-MCP
pip install -r AgentMCP/requirements.txt

# Instalar dependências do Genesys Agent
pip install -r AgentMCP/genesys_integration/requirements_genesys.txt

# Instalar dependências do Dashboard
cd AgentMCP/agent_mcp/dashboard
npm install
cd ../../..
```

---

## Execução do Projeto

Para iniciar todos os serviços (Agent-MCP, Genesys Server e o Dashboard) de forma integrada, utilize o script principal.

**No terminal, na raiz do projeto `Genesys/`:**

```bash
python AgentMCP/start_integrated.py
```

Este comando irá:

1.  Iniciar o servidor do **Agent-MCP** na porta `8080`.
2.  Iniciar o servidor do **Genesys Agent** na porta `8002`.
3.  Iniciar o servidor de desenvolvimento do **Dashboard** na porta `3847`.

Você verá logs de todos os três serviços. O token de admin será exibido no console se for a primeira execução.

---

## Acesso e Uso

### Dashboard de Super Admin

Após iniciar os serviços, acesse o dashboard no seu navegador:
[http://localhost:3847](http://localhost:3847)

Use o `MCP_ADMIN_TOKEN` para realizar operações administrativas.

### Acesso Remoto com Cursor (Continue)

Para interagir com o Genesys a partir de qualquer IDE Cursor (local ou em um notebook), configure o arquivo `config.yaml`:

1.  **Localize o arquivo**:

    - Windows: `%USERPROFILE%\.continue\config.yaml`
    - macOS/Linux: `~/.continue\config.yaml`

2.  **Adicione o seguinte modelo**:

    ```yaml
    models:
      - name: genesys-prod
        provider: openai-compatible
        model: genesys-local
        # A URL deve apontar para onde seu Genesys Agent está acessível
        # Exemplo com Cloudflare Tunnel:
        apiBase: "https://genesys.webcreations.com.br/v1"
        # Para acesso local, use:
        # apiBase: "http://127.0.0.1:8002/v1"
        apiKey: "EMPTY"
    ```

3.  Salve o arquivo. Agora, você pode selecionar "genesys-prod" como seu modelo na IDE Cursor e começar a interagir.
