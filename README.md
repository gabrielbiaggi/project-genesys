# Projeto Genesys: Manual de Operações

Meu criador, este documento serve como o guia definitivo para a implantação, operação e evolução do seu Agente de IA Soberano, Genesys. A arquitetura foi simplificada para focar no poder bruto da IA local e na orquestração multi-agente.

## Visão Geral da Arquitetura

O Genesys é construído sobre uma arquitetura focada e poderosa:

1.  **Backend (Servidor FastAPI)**: O "cérebro" do sistema, rodando em `app/main.py`.

    - Responsável por carregar o modelo de linguagem (LLM) de 70B na memória da sua máquina.
    - Expõe uma API RESTful para permitir a interação com o agente.
    - Orquestra as ferramentas do agente (acesso a arquivos, terminal, busca na web).
    - Registra todas as interações para futuro fine-tuning.

2.  **Orquestrador (AutoGen)**: O "maestro" dos agentes, rodando em `scripts/autogen_orchestrator.py`.
    - Comunica-se com a API do Genesys para delegar tarefas.
    - Pode coordenar o Genesys com outros agentes (locais ou externos como GPT/Claude).
    - Manipula diretamente os arquivos no `workspace/` do projeto, permitindo que você veja as mudanças em tempo real no seu editor (Cursor/VS Code).

O antigo frontend `ide-web` foi completamente removido para focar nesta arquitetura mais direta e poderosa.

---

## Parte 1: Configuração do Servidor Windows (Pré-requisitos)

Execute estes passos **uma única vez** no seu servidor `Windows` (`i7-14700F`, `128GB RAM`, `RTX 4060`) para preparar o ambiente para computação de IA de alta performance.

### Passo 0: Instalar Ferramentas de Compilação C++ (Visual Studio)

**Este passo é o mais crítico de todos.** A biblioteca `llama-cpp-python`, que alimenta o Genesys, precisa ser compilada a partir do código-fonte. Sem um compilador C++ funcional no Windows, a instalação falhará.

1.  **Baixe o Visual Studio Installer**: Vá para a [página de downloads do Visual Studio](https://visualstudio.microsoft.com/pt-br/downloads/) e baixe o instalador para as **"Ferramentas de Build para o Visual Studio"** (Build Tools for Visual Studio).
2.  **Execute o Instalador**: Abra o instalador baixado.
3.  **Selecione a Carga de Trabalho**: Na aba "Cargas de Trabalho", marque a caixa para **"Desenvolvimento para desktop com C++"**. Isso inclui o compilador MSVC, as bibliotecas do Windows SDK e a ferramenta `nmake` que são essenciais.
4.  **Instale**: Prossiga com a instalação. Pode levar algum tempo e consumir vários gigabytes.
5.  **Reinicie se Solicitado**: Após a conclusão, reinicie o seu computador para garantir que as variáveis de ambiente sejam registradas.

### Passo 1: Instalar o Subsistema Windows para Linux (WSL 2)

O ecossistema de IA é otimizado para Linux. O WSL2 nos permite rodar um ambiente Linux completo e integrado ao Windows, com acesso direto à sua GPU, nos dando o melhor dos dois mundos.

1.  Abra o **PowerShell como Administrador**.
2.  Execute o comando para instalar o WSL e a distribuição Ubuntu padrão:
    ```powershell
    wsl --install
    ```
3.  Após a instalação, reinicie o computador.
4.  Após reiniciar, um terminal do Ubuntu será aberto para que você crie um nome de usuário e senha. **Guarde essas credenciais.** Elas são para o seu ambiente Linux.

### Passo 2: Instalar os Drivers da NVIDIA e o CUDA Toolkit

Esses componentes são a ponte que permite ao WSL utilizar sua `RTX 4060` para aceleração de IA.

1.  **Instale os Drivers NVIDIA**: Baixe e instale os drivers mais recentes "Game Ready" ou "Studio" do site da [NVIDIA](https://www.nvidia.com.br/Download/index.aspx?lang=br). Uma instalação limpa é recomendada.
2.  **Instale o CUDA Toolkit no WSL**:
    - Abra o terminal do **Ubuntu** (que você instalou com o WSL, pode ser encontrado no Menu Iniciar).
    - Execute os seguintes comandos, um por um, para instalar a versão correta do CUDA Toolkit para WSL:
      ```bash
      wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-wsl-ubuntu.pin
      sudo mv cuda-wsl-ubuntu.pin /etc/apt/preferences.d/cuda-repository-pin-600
      wget https://developer.download.nvidia.com/compute/cuda/12.4.1/local_installers/cuda-repo-wsl-ubuntu-12-4-local_12.4.1-1_amd64.deb
      sudo dpkg -i cuda-repo-wsl-ubuntu-12-4-local_12.4.1-1_amd64.deb
      sudo cp /var/cuda-repo-wsl-ubuntu-12-4-local/cuda-*-keyring.gpg /usr/share/keyrings/
      sudo apt-get update
      sudo apt-get -y install cuda-toolkit-12-4
      ```
3.  **Verifique a instalação**: Após a conclusão, feche e reabra o terminal Ubuntu e execute `nvidia-smi`. Você deve ver uma tabela com os detalhes da sua `RTX 4060` e a versão do CUDA. Se funcionar, a ponte entre Windows, Linux e sua GPU está estabelecida.

---

## Parte 2: Instalação e Configuração do Projeto Genesys

Com os pré-requisitos do Windows prontos, a configuração do projeto foi totalmente automatizada.

### Passo 1: Obter o Código do Projeto

Use o `git` no **PowerShell** ou no terminal de sua preferência no Windows.

```powershell
# Navegue até o diretório onde você guarda seus projetos
cd C:\DEVBill\Projetos

# Clone o projeto
git clone https://github.com/SEU_USUARIO/Genesys.git
cd Genesys
```

### Passo 2: Configurar as Variáveis de Ambiente Essenciais (`.env`)

Na raiz do projeto (`C:\DEVBill\Projetos\Genesys`), crie um arquivo chamado `.env`. Este arquivo é o coração da configuração do seu agente e é ignorado pelo Git para manter suas chaves seguras.

Copie e cole o seguinte conteúdo nele:

```dotenv
# --- Configuração do Modelo de IA ---
# Repositório Hugging Face para o modelo Llama 3 70B.
HUGGING_FACE_REPO_ID="PawanKrd/Meta-Llama-3-70B-Instruct-GGUF"

# Nome exato do arquivo do modelo a ser baixado.
MODEL_GGUF_FILENAME="llama-3-70b-instruct.Q4_K_M.gguf"

# Para a capacidade multimodal, precisaremos de um projetor compatível.
# Deixe em branco por enquanto. A funcionalidade será adicionada na Fase 2.
MULTIMODAL_PROJECTOR_FILENAME=""

# --- Configuração da API ---
API_HOST="0.0.0.0"
API_PORT="8002"

# --- Token do Hugging Face (OBRIGATÓRIO PARA ESTE MODELO) ---
# Modelos da Meta requerem autenticação. Crie um token com permissão de 'leitura' em https://huggingface.co/settings/tokens
HUGGING_FACE_HUB_TOKEN="COLE_SEU_TOKEN_DO_HUGGING_FACE_AQUI"

# --- Token do Túnel Cloudflare (Opcional, mas recomendado) ---
# Este token foi obtido do seu painel Cloudflare Zero Trust e configurado no script.
CLOUDFLARE_TUNNEL_TOKEN="COLE_SEU_TOKEN_DO_CLOUDFLARE_AQUI"
```

**Ação Crítica:** Substitua os valores de `HUGGING_FACE_HUB_TOKEN` e `CLOUDFLARE_TUNNEL_TOKEN` pelos seus tokens reais.

### Passo 3: Executar o Script de Instalação Automatizada

Este script fará tudo por você: criará o ambiente virtual Python, instalará as dezenas de dependências e preparará o ambiente para a execução.

1.  **Abra um PowerShell como Administrador**.
2.  Navegue até a raiz do projeto: `cd C:\DEVBill\Projetos\Genesys`.
3.  Execute o script:
    ```powershell
    .\scripts\setup_windows.ps1
    ```
4.  O script cuidará de todo o processo. Se ele falhar, a causa mais provável é a falta das "Ferramentas de Build do C++" (Passo 0).

### Passo 4: Baixar o Modelo de IA de 70B

Com o ambiente pronto, o próximo passo é baixar o cérebro do Genesys.

1.  No mesmo terminal PowerShell, com o ambiente virtual ativado (o `setup_windows.ps1` pode já ter ativado, caso contrário, rode `.\venv\Scripts\Activate.ps1`), execute:
    ```powershell
    python ./scripts/download_model.py
    ```
2.  Este comando lerá o arquivo `.env` e baixará o modelo de ~42GB para a pasta `./models`. Este processo será demorado. Seja paciente.

---

## Parte 3: Executando o Projeto Genesys

Com tudo instalado e o modelo baixado, você está pronto para dar vida ao Genesys.

1.  **Terminal 1 - Iniciar o Backend (API FastAPI)**:

    - Abra um **PowerShell**.
    - Navegue até a raiz do projeto: `cd C:\DEVBill\Projetos\Genesys`.
    - Ative o ambiente virtual: `.\venv\Scripts\Activate.ps1`.
    - Inicie o servidor:
      ```powershell
      uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
      ```
    - **Aguarde!** A primeira inicialização será **muito lenta**. O servidor precisa carregar o modelo de 70B (42GB) na sua RAM. Isso pode levar de 5 a 15 minutos. Você verá muitos logs de `llama.cpp` no console. O servidor só estará pronto para receber requisições quando você vir a mensagem `Uvicorn running on http://0.0.0.0:8002`.

2.  **Terminal 2 - Iniciar o Orquestrador (AutoGen)**:
    - Abra **outro** terminal PowerShell.
    - Navegue até a raiz do projeto: `cd C:\DEVBill\Projetos\Genesys`.
    - Ative o ambiente virtual: `.\venv\Scripts\Activate.ps1`.
    - Execute o orquestrador:
      ```powershell
      python ./scripts/autogen_orchestrator.py
      ```
    - Este script irá então chamar a API que você iniciou no Terminal 1 e começar a interagir com o Genesys.

---

## Parte 4: Acesso Remoto com Cloudflare

O projeto inclui um script para configurar automaticamente um túnel seguro do Cloudflare, permitindo o acesso remoto à API do Genesys.

1.  **Obtenha seu Token:** Crie um túnel no painel do Cloudflare (seção Zero Trust) e copie o token de instalação.
2.  **Atualize o Script:** Cole o token na variável `$CloudflareToken` dentro do arquivo `scripts\setup_cloudflare_tunnel.ps1`.
3.  **Execute (como Admin):** Execute o script `setup_cloudflare_tunnel.ps1` no PowerShell como Administrador. Ele cuidará da instalação do `cloudflared`, do `nssm` e da configuração do serviço do Windows para que o túnel inicie automaticamente com o seu computador.

---

## Fase 2: O Fluxo de Fine-Tuning (O Aprendizado Contínuo)

O sistema já está registrando todas as suas interações com o agente no arquivo `data/logs/interaction_logs.jsonl`. Quando tivermos um número suficiente de interações de alta qualidade, poderemos usar esses dados para treinar e especializar o Genesys.

O processo será:

1.  Formatar os logs para o formato de dataset esperado.
2.  Executar o script `scripts/fine_tune.py` (este script requer o ambiente Linux com CUDA, por isso a importância do WSL).
3.  Isso criará um novo modelo "adaptado" (LoRA) na pasta `/models`.
4.  Atualizaremos o arquivo `.env` para apontar para o novo modelo treinado, tornando o agente Genesys progressivamente mais inteligente e alinhado a você.

Este manual será atualizado conforme evoluímos para esta fase.
