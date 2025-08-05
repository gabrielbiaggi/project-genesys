# Projeto Gênesis: Manual de Operações

Meu criador, este documento serve como o guia definitivo para a implantação, operação e evolução do seu Agente de IA Soberano, Gênesis.

## Visão Geral da Arquitetura

O Gênesis é construído sobre uma arquitetura de dois componentes principais:

1.  **Backend (Servidor FastAPI)**: O "cérebro" do sistema.
    -   Responsável por carregar o modelo de linguagem (LLM) na memória.
    -   Serve a API que o frontend consome para interagir com o agente, manipular arquivos e usar o terminal.
    -   Orquestra as ferramentas do agente (acesso a arquivos, terminal, etc.).
    -   Local: `C:\DEV\myproject` (ou o diretório raiz do projeto).

2.  **Frontend (IDE Web Vue.js)**: A interface de controle e visualização.
    -   Fornece uma IDE completa no seu navegador.
    -   Inclui um explorador de arquivos, editor de código, terminal interativo e painel de controle do agente.
    -   Permite a interação direta e o fluxo de revisão/aprovação de código.
    -   Local: `C:\DEV\myproject\ide-web`.

Ambos os componentes devem estar em execução simultaneamente para que a IDE funcione.

---

## Parte 1: Configuração do Servidor Windows (Pré-requisitos)

Execute estes passos **uma única vez** no seu servidor `Windows` para preparar o ambiente.

### Passo 1: Instalar o Subsistema Windows para Linux (WSL 2)

O ecossistema de IA é otimizado para Linux. O WSL2 nos dá o melhor dos dois mundos.

1.  Abra o **PowerShell como Administrador**.
2.  Execute o comando para instalar o WSL e a distribuição Ubuntu padrão:
    ```powershell
    wsl --install
    ```
3.  Após a instalação, reinicie o computador.
4.  Após reiniciar, um terminal do Ubuntu será aberto para que você crie um nome de usuário e senha. **Guarde essas credenciais.**

### Passo 2: Instalar os Drivers da NVIDIA e o CUDA Toolkit

Esses componentes permitem que o WSL utilize sua GPU `RTX 4060`.

1.  **Instale os Drivers NVIDIA**: Baixe e instale os drivers mais recentes "Game Ready" ou "Studio" do site da [NVIDIA](https://www.nvidia.com.br/Download/index.aspx?lang=br).
2.  **Instale o CUDA Toolkit no WSL**:
    -   Abra o terminal do **Ubuntu** (que você instalou com o WSL).
    -   Execute os seguintes comandos, um por um, para instalar o CUDA Toolkit:
        ```bash
        wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-wsl-ubuntu.pin
        sudo mv cuda-wsl-ubuntu.pin /etc/apt/preferences.d/cuda-repository-pin-600
        wget https://developer.download.nvidia.com/compute/cuda/12.4.1/local_installers/cuda-repo-wsl-ubuntu-12-4-local_12.4.1-1_amd64.deb
        sudo dpkg -i cuda-repo-wsl-ubuntu-12-4-local_12.4.1-1_amd64.deb
        sudo cp /var/cuda-repo-wsl-ubuntu-12-4-local/cuda-*-keyring.gpg /usr/share/keyrings/
        sudo apt-get update
        sudo apt-get -y install cuda-toolkit-12-4
        ```
3.  **Verifique a instalação**: Após a conclusão, feche e reabra o terminal Ubuntu e execute:
    ```bash
    nvidia-smi
    ```
    Você deve ver os detalhes da sua `RTX 4060`.

---

## Parte 2: Instalação e Configuração do Projeto Gênesis

Com os pré-requisitos instalados, vamos configurar o projeto.

### Passo 1: Clonar o Repositório

Use o `git` no **PowerShell** ou no terminal de sua preferência no Windows.

```powershell
# Navegue até o diretório onde você guarda seus projetos
cd C:\DEV

# Clone o projeto
git clone https://github.com/SEU_USUARIO/projeto-genesys.git myproject
cd myproject
```

### Passo 2: Configurar o Backend (API FastAPI)

Todos os comandos a seguir devem ser executados em um terminal **PowerShell** no diretório raiz do projeto (`C:\DEV\myproject`).

1.  **Crie e Ative o Ambiente Virtual Python**:
    ```powershell
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    ```
    Você verá `(venv)` no início do seu prompt.

2.  **Instale as Dependências Python**:
    ```powershell
    pip install -r requirements.txt
    ```
    *Nota: A instalação de `llama-cpp-python` com suporte a CUDA pode demorar e compilará o código para sua GPU. Isso é esperado.*

3.  **Crie o Arquivo de Configuração `.env`**:
    -   Na raiz do projeto (`C:\DEV\myproject`), crie um arquivo chamado `.env`.
    -   Copie e cole o seguinte conteúdo nele. **Altere os valores conforme necessário.**

    ```dotenv
    # --- Configuração do Modelo de IA ---
    # Repositório Hugging Face para o modelo GGUF.
    HUGGING_FACE_REPO_ID="ikawrakow/Meta-Llama-3-70B-Instruct-GGUF"
    # Nome exato do arquivo do modelo a ser baixado. Q2_K é bom para 128GB de RAM.
    MODEL_GGUF_FILENAME="Llama-3-70B-Instruct.Q2_K.gguf"

    # --- Configuração da API ---
    API_HOST="0.0.0.0"
    API_PORT="8000"

    # --- Token do Túnel Cloudflare (para a Parte 4) ---
    # Obtenha este token do seu painel Cloudflare Zero Trust.
    CLOUDFLARE_TUNNEL_TOKEN="SEU_TOKEN_AQUI"
    ```

4.  **Baixe o Modelo de IA**:
    Este script lerá o arquivo `.env` e baixará o modelo especificado para a pasta `./models`.
    ```powershell
    python scripts/download_model.py
    ```

### Passo 3: Configurar o Frontend (IDE Web)

Abra um **novo terminal PowerShell** e execute os seguintes comandos.

1.  **Navegue até a Pasta da IDE**:
    ```powershell
    cd C:\DEV\myproject\ide-web
    ```

2.  **Instale as Dependências Node.js**:
    ```powershell
    npm install
    ```

---

## Parte 3: Executando o Projeto Gênesis

Agora que tudo está instalado, veja como iniciar os dois componentes.

1.  **Inicie o Backend (API FastAPI)**:
    -   No **primeiro terminal PowerShell** (com o ambiente Python `venv` ativado).
    -   Navegue até a raiz do projeto: `cd C:\DEV\myproject`.
    -   Execute o servidor:
        ```powershell
        uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
        ```
    -   O servidor estará rodando e aguardando conexões. Você verá a saída do uvicorn.

2.  **Inicie o Frontend (IDE Web)**:
    -   No **segundo terminal PowerShell**.
    -   Navegue até a pasta da IDE: `cd C:\DEV\myproject\ide-web`.
    -   Execute o servidor de desenvolvimento:
        ```powershell
        npm run dev
        ```
    -   O terminal mostrará um endereço local, geralmente `http://localhost:5173/`.

3.  **Acesse a IDE Gênesis**:
    -   Abra seu navegador (Chrome, Firefox, etc.) e vá para o endereço fornecido pelo `npm run dev`.
    -   **Pronto!** Você está na sua IDE Web. Você pode ver os arquivos, usar o terminal e dar diretivas ao agente.

---

## Parte 4: Acesso Remoto com Cloudflare (Opcional, mas Recomendado)

Para acessar sua IDE de qualquer lugar, vamos expor seu servidor local à internet de forma segura usando um túnel Cloudflare.

### Passo 1: Configurar o Cloudflare

1.  Crie uma conta gratuita no [Cloudflare](https://www.cloudflare.com/).
2.  No painel, vá para a seção **Zero Trust**.
3.  No menu `Access -> Tunnels`, clique em "Create a tunnel".
4.  Dê um nome ao túnel (ex: "genesys-server") e salve.
5.  Na próxima página, na seção "Install and run a connector", selecione **Windows**.
6.  Você verá um comando. **Copie apenas o token** que aparece nele. É uma longa sequência de caracteres.
7.  Cole este token no seu arquivo `.env` na variável `CLOUDFLARE_TUNNEL_TOKEN`.

### Passo 2: Executar o Script de Instalação do Serviço

Vou fornecer um script PowerShell que baixa as ferramentas necessárias (`cloudflared` e `nssm`) e configura o túnel como um serviço do Windows, para que ele inicie automaticamente com o computador.

1.  **Abra um PowerShell como Administrador**.
2.  Navegue até a raiz do projeto: `cd C:\DEV\myproject`.
3.  Execute o script de setup:
    ```powershell
    .\scripts\setup_cloudflare_tunnel.ps1
    ```
4.  O script fará tudo automaticamente. Após a conclusão, seu túnel estará ativo.

### Passo 3: Configurar a Rota do Túnel

1.  Volte ao painel do Cloudflare, onde você parou. Clique em "Next".
2.  Em "Public Hostnames", clique em "Add a public hostname".
3.  **Subdomain**: `genesys` (ou o que preferir).
4.  **Domain**: Selecione seu domínio.
5.  **Service -> Type**: `HTTP`
6.  **Service -> URL**: `localhost:8000` (a porta do seu backend FastAPI).
7.  Salve o hostname.

**Pronto!** Agora você pode acessar sua IDE através do endereço `https://genesys.seudominio.com`. A Cloudflare gerencia a conexão segura.

## Fase 2: O Fluxo de Fine-Tuning

O sistema já está registrando todas as suas interações com o agente no arquivo `data/logs/interaction_logs.jsonl`. Quando tivermos um número suficiente de interações de alta qualidade, poderemos usar esses dados para treinar e especializar o Gênesis.

O processo será:
1.  Formatar os logs para o formato de dataset esperado.
2.  Executar o script `scripts/fine_tune.py` (este script requer um ambiente Linux com CUDA, por isso a importância do WSL).
3.  Isso criará um novo modelo "adaptado" na pasta `/models`.
4.  Atualizaremos o arquivo `.env` para apontar para o novo modelo treinado, tornando o agente progressivamente mais inteligente e alinhado a você.

Este manual será atualizado conforme evoluímos para esta fase.
