# Genesys: Arquiteto de Código Autônomo

## Visão Geral

Genesys é um sistema de IA avançado projetado para atuar como um arquiteto e desenvolvedor de software sênior. Integrado à plataforma **Agent-MCP (Multi-Agent Commander Platform)**, ele transcende a função de um simples assistente de código, operando como uma entidade autônoma que pode raciocinar, aprender, se auto-corrigir e interagir com o ambiente do sistema.

A arquitetura é composta por três pilares:

1.  **Agent-MCP**: O cérebro e orquestrador do sistema. É um servidor backend que gerencia agentes, tarefas, memória de longo prazo (banco de dados vetorial) e executa os ciclos de aprendizado autônomo.
2.  **Genesys Agent**: A interface de raciocínio. É um servidor FastAPI que expõe um modelo de linguagem local (LLM), aprimorado com a capacidade de delegar tarefas complexas para a API do Gemini. Ele serve como o ponto de entrada para as interações do usuário e é **gerenciado (iniciado/parado) pelo Agent-MCP**.
3.  **Dashboard de Super Admin**: Uma interface web completa para iniciar e parar o Genesys, monitorar a saúde do sistema em tempo real, gerenciar a memória vetorial, visualizar tarefas e auditar todas as ações.
4.  **Cursor (via Extensão Continue)**: A interface do usuário. Através da configuração de um modelo personalizado, a IDE Cursor pode se comunicar diretamente com o Genesys Agent, permitindo uma interação fluida e nativa para desenvolvimento de código.

---

## Funcionalidades Principais

- **Gerenciamento como Serviço**: Inicie e pare o Agent-MCP e o Dashboard como serviços de background independentes com um único comando.
- **Controle Remoto via Dashboard**: Inicie, pare e monitore o status do Genesys Agent diretamente da interface web.
- **Raciocínio Híbrido**: Utiliza um LLM local para tarefas rápidas e a poderosa API do **Gemini 1.5 Pro** para tarefas complexas como análise de arquitetura, refatoração e depuração avançada.
- **Aprendizado Autônomo Proativo**: Após a primeira interação do usuário, o Agent-MCP inicia um loop em background para pesquisar tópicos relevantes, fazer perguntas ao Gemini e enriquecer sua base de conhecimento (RAG) sem intervenção humana.
- **Consciência de Sistema**: Equipado com ferramentas inspiradas no Desktop Commander, o Genesys pode listar processos, verificar o uso de CPU/memória e entender o ambiente em que está operando.
- **Ciclo de Auto-Correção**: Ao encontrar um erro, o Genesys usa a API do Gemini para analisar o problema, pesquisar soluções e tentar novamente de forma autônoma.
- **Acesso Remoto Seguro**: A API do Genesys e o Dashboard são projetados para serem expostos de forma segura via túneis (como o Cloudflare).

---

## Guia de Inicialização Rápida

Siga estes três passos para colocar todo o sistema no ar.

### Passo 1: Criar o Arquivo de Configuração `.env`

Na **raiz do projeto**, crie um arquivo chamado `.env`.

**Preencha as seguintes variáveis (use o arquivo `.env` que acabamos de criar como base):**

```dotenv
# .env (na raiz do projeto)

# --- Configurações do Genesys Agent e Agent-MCP ---
GEMINI_API_KEY="sua_chave_gemini_aqui"
OPENAI_API_KEY="" # Opcional
MCP_ADMIN_TOKEN="seu_token_seguro"

# Token de administrador para proteger o dashboard e a API
MCP_ADMIN_TOKEN="defina_um_token_seguro_aqui"
```

### Passo 2: Configurar o Ambiente

Execute este script **uma única vez** para instalar todas as dependências.

> **Importante**: Execute o PowerShell como **Administrador**.

```powershell
.\setup_environment.ps1
```

### Passo 3: Iniciar o Sistema

Execute este script para iniciar o **Agent-MCP Backend** e o **Dashboard Frontend** como serviços de background.

```powershell
.\start.ps1
```

Após a execução, os serviços estarão rodando. Você pode fechar a janela do terminal.

- **Acesse o Dashboard**: [http://localhost:3847](http://localhost:3847)
- Use o Dashboard para **iniciar o Genesys Agent** na aba "System".

### Passo 4: Parar o Sistema

Para parar todos os serviços de background (Backend e Dashboard), execute:

```powershell
.\stop.ps1
```

---

## Configuração do Cursor (Continue)

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
        # Para acesso local (após iniciar via dashboard):
        # apiBase: "http://127.0.0.1:8002/v1"
        apiKey: "EMPTY"
    ```

3.  Salve o arquivo. Agora, você pode selecionar "genesys-prod" como seu modelo na IDE Cursor e começar a interagir.

---

## Acesso Online ao Dashboard (Opcional)

Para acessar o dashboard de "Super Admin" de qualquer lugar, você pode expô-lo através do seu Cloudflare Tunnel, da mesma forma que o Genesys Agent.

**Pré-requisito**: Você já deve ter o `cloudflared` instalado e um túnel configurado para `genesys.webcreations.com.br`.

### Passos para Configuração

1.  **Acesse seu Dashboard da Cloudflare**:

    - Vá para a seção "Zero Trust".
    - Navegue até `Access -> Tunnels`.

2.  **Selecione seu Túnel**:

    - Clique no túnel que você usa para o Genesys e vá em "Configure".

3.  **Adicione um Novo Serviço (Public Hostname)**:

    - Clique em "Add a public hostname".
    - **Subdomain**: `dashboard` (ou o que preferir, como `painel`).
    - **Domain**: `genesys.webcreations.com.br`.
    - **Service Type**: `HTTP`.
    - **URL**: `localhost:3847` (a porta padrão do dashboard).

4.  **Salve as Alterações**:
    - Clique em "Save hostname".

Após alguns instantes, o dashboard deverá estar acessível publicamente em **`http://dashboard.genesys.webcreations.com.br`**. O acesso ainda dependerá do seu `MCP_ADMIN_TOKEN` para operações sensíveis.
