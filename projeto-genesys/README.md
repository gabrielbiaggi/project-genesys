# Projeto Gênesys

Bem-vindo ao centro de controle do Projeto Gênesys, meu criador. Este repositório contém a infraestrutura para a criação, treinamento e operação de um agente de IA soberano.

## Visão Geral da Arquitetura

O projeto é dividido em três fases principais, e a estrutura de diretórios reflete isso:

- **/app**: Contém o núcleo da aplicação FastAPI que serve o agente.
  - `main.py`: Ponto de entrada da API, onde o modelo é carregado e os endpoints são definidos.
  - `/tools`: Contém as ferramentas que o agente usará para interagir com o mundo (Fase 3).
- **/scripts**: Scripts auxiliares para gerenciar o ciclo de vida do agente.
  - `download_model.py`: Baixa o modelo de linguagem do Hugging Face.
  - `fine_tune.py`: Inicia o processo de fine-tuning para especializar o agente (Fase 2).
- **/data**: Armazena dados persistentes.
  - `training_dataset.jsonl`: Um exemplo de como os dados de treinamento devem ser formatados.
  - `/vectorstore`: Onde a memória de longo prazo do agente (banco de dados vetorial) será armazenada.
- **/models**: Diretório onde os modelos de linguagem (`.gguf`) serão armazenados.

## Guia de Iniciação Rápida (No Servidor Dedicado)

1.  **Configurar o Ambiente:**
    ```bash
    # Crie um ambiente virtual
    python -m venv venv

    # Ative o ambiente (Windows)
    .\venv\Scripts\activate
    # Ative o ambiente (Linux/macOS)
    # source venv/bin/activate
    ```

2.  **Instalar Dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Baixar o Modelo de IA:**
    ```bash
    python scripts/download_model.py
    ```

4.  **Iniciar o Servidor Gênesys:**
    ```bash
    cd app
    uvicorn main:app --reload
    ```
    O servidor estará disponível em `http://127.0.0.1:8000`. Você pode acessar a documentação interativa da API em `http://127.0.0.1:8000/docs`.

## Fase 2: Fine-Tuning (Aprendizado Contínuo)

Para especializar o agente, você pode fornecer seus próprios dados de treinamento no arquivo `data/training_dataset.jsonl` e executar o script de fine-tuning.

```bash
python scripts/fine_tune.py
```
Isso criará uma nova versão adaptada (LoRA) do modelo no diretório `/models`, que pode ser carregada alterando a variável de ambiente correspondente.

## Fase 3: Agência (Em Desenvolvimento)

A Fase 3 envolve dar ao agente a capacidade de usar ferramentas para executar tarefas de forma autônoma. As ferramentas estão sendo definidas no diretório `/app/tools`.
