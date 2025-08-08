# scripts/fine_tune.py
import os
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, PeftModel, get_peft_model
from trl import SFTTrainer
from dotenv import load_dotenv

# --- NOTA DE EXECUÇÃO ---
# Este script foi projetado para ser executado dentro do ambiente WSL2 com CUDA configurado,
# pois dependências como 'bitsandbytes' são otimizadas para Linux.

def fine_tune_model():
    """
    Executa o processo de fine-tuning do modelo Genesys usando os dados de interação logados.
    """
    print("--- Iniciando o Processo de Fine-Tuning do Agente Genesys ---")

    # 1. Carregar Configurações do Ambiente
    load_dotenv(dotenv_path='../.env')
    base_model_name = os.getenv("MODEL_GGUF_FILENAME")
    if not base_model_name:
        raise ValueError("MODEL_GGUF_FILENAME não encontrado no arquivo .env. O fine-tuning não pode continuar.")
    
    # O fine-tuning requer o modelo original do Hugging Face, não o GGUF.
    # Vamos derivar o nome do repositório a partir da configuração do GGUF.
    # Ex: ikawrakow/Meta-Llama-3-70B-Instruct-GGUF -> meta-llama/Meta-Llama-3-70B-Instruct
    # Esta é uma suposição que pode precisar de ajuste manual.
    hf_repo_id = "meta-llama/Meta-Llama-3-70B-Instruct" # Ajuste se o modelo base for outro
    print(f"Usando o modelo base do Hugging Face: {hf_repo_id}")

    # Caminho para salvar os adaptadores LoRA treinados
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'models', 'genesys-adapter-v1')
    os.makedirs(output_dir, exist_ok=True)
    print(f"Os adaptadores treinados serão salvos em: {output_dir}")

    # 2. Carregar o Dataset de Logs
    log_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'logs', 'interaction_logs.jsonl')
    if not os.path.exists(log_file_path):
        print(f"Arquivo de log '{log_file_path}' não encontrado. Não há dados para treinar. Encerrando.")
        return

    print(f"Carregando dataset de: {log_file_path}")
    dataset = load_dataset('json', data_files=log_file_path, split='train')

    # 3. Configurar Quantização (BitsAndBytes) para economizar VRAM
    # Carregamos o modelo em 4-bit para o treinamento.
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )
    print("Configuração de quantização (4-bit) definida.")

    # 4. Carregar o Modelo e o Tokenizer
    print("Carregando modelo e tokenizer. Isso pode levar alguns minutos...")
    model = AutoModelForCausalLM.from_pretrained(
        hf_repo_id,
        quantization_config=bnb_config,
        device_map="auto",  # Deixa o accelerate decidir como distribuir o modelo (GPU, CPU, etc.)
        trust_remote_code=True
    )
    model.config.use_cache = False
    model.config.pretraining_tp = 1

    tokenizer = AutoTokenizer.from_pretrained(hf_repo_id, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    print("Modelo e tokenizer carregados com sucesso.")

    # 5. Configurar o LoRA (Low-Rank Adaptation)
    peft_config = LoraConfig(
        lora_alpha=16,
        lora_dropout=0.1,
        r=64,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=[ # Módulos específicos para o Llama 3
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ]
    )
    model = get_peft_model(model, peft_config)
    print("Modelo configurado com adaptadores LoRA.")

    # 6. Definir os Argumentos de Treinamento
    training_arguments = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=1,  # Comece com 1 época, aumente se necessário
        per_device_train_batch_size=1, # Batch size pequeno devido ao tamanho do modelo
        gradient_accumulation_steps=4, # Simula um batch size maior (1*4=4)
        optim="paged_adamw_32bit",
        save_steps=50,
        logging_steps=10,
        learning_rate=2e-4,
        weight_decay=0.001,
        fp16=False,
        bf16=True, # Use bf16 para melhor performance em GPUs Ampere+ (como a RTX 4060)
        max_grad_norm=0.3,
        max_steps=-1,
        warmup_ratio=0.03,
        group_by_length=True,
        lr_scheduler_type="cosine",
        report_to="tensorboard"
    )
    print("Argumentos de treinamento definidos.")

    # 7. Inicializar o Trainer com SFTTrainer
    # SFTTrainer cuidará da formatação do prompt para nós.
    # Ele espera uma coluna 'text' no dataset. Vamos formatá-la.
    def format_dataset(example):
        # Formato básico de instrução para o Llama 3
        return {'text': f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\\n\\n{example['prompt']}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\\n\\n{example['response']}<|eot_id|>"}

    formatted_dataset = dataset.map(format_dataset)
    
    trainer = SFTTrainer(
        model=model,
        train_dataset=formatted_dataset,
        peft_config=peft_config,
        dataset_text_field="text",
        max_seq_length=2048, # Reduza se ocorrerem erros de memória
        tokenizer=tokenizer,
        args=training_arguments,
        packing=False,
    )
    print("SFTTrainer inicializado. Começando o treinamento...")

    # 8. Iniciar o Treinamento
    trainer.train()

    # 9. Salvar o Modelo Treinado (Apenas os adaptadores LoRA)
    trainer.save_model(output_dir)
    print(f"--- Treinamento Concluído! Adaptadores salvos em '{output_dir}' ---")
    print("Para usar o modelo treinado, você precisará carregar o modelo base e, em seguida, fundir esses adaptadores.")

if __name__ == "__main__":
    # Adicionar um prompt para garantir que o usuário sabe que precisa estar no WSL
    if os.name == 'nt':
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ATENÇÃO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("Este script de fine-tuning foi projetado para ser executado no ambiente WSL (Subsistema Windows para Linux).")
        print("Ele requer CUDA e dependências específicas do Linux para funcionar corretamente.")
        print("Por favor, execute este script a partir do seu terminal Ubuntu/WSL.")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    else:
        fine_tune_model()
