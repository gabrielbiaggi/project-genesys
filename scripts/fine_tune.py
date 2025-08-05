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
from peft import LoraConfig
from trl import SFTTrainer
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv(dotenv_path='../.env')

def train():
    """
    Função principal para executar o fine-tuning do modelo.
    """
    # --- Configurações ---
    model_name = os.getenv("MODEL_NAME") # Ex: "Meta-Llama-3-8B-Instruct"
    # O dataset de treinamento
    dataset_name = os.path.join(os.path.dirname(__file__), '..', 'data', 'training_dataset.jsonl')
    # O nome do novo modelo adaptado (LoRA)
    new_model_name = f"{model_name}-finetuned"
    # Diretório para salvar os checkpoints e o modelo final
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'models', new_model_name)

    # --- Carregar Dataset ---
    print(f"Carregando dataset de: {dataset_name}")
    dataset = load_dataset('json', data_files=dataset_name, split="train")

    # --- Configuração de Quantização (QLoRA) ---
    # Isso permite treinar modelos grandes em hardware mais modesto
    compute_dtype = getattr(torch, "float16")
    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=compute_dtype,
        bnb_4bit_use_double_quant=False,
    )

    # --- Carregar Modelo e Tokenizer Base ---
    print(f"Carregando modelo base: {model_name}")
    # Nota: Para o fine-tuning, usamos o modelo original da Hugging Face, não o GGUF.
    # O `llama-cpp-python` é para inferência, `transformers` é para treinamento.
    base_model = AutoModelForCausalLM.from_pretrained(
        f"meta-llama/{model_name}",
        quantization_config=quant_config,
        device_map={"": 0} # Usa a primeira GPU disponível
    )
    base_model.config.use_cache = False
    base_model.config.pretraining_tp = 1

    tokenizer = AutoTokenizer.from_pretrained(f"meta-llama/{model_name}", trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    # --- Configuração do PEFT (LoRA) ---
    peft_parameters = LoraConfig(
        lora_alpha=16,
        lora_dropout=0.1,
        r=64,
        bias="none",
        task_type="CAUSAL_LM",
    )

    # --- Argumentos de Treinamento ---
    training_parameters = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=1,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=1,
        optim="paged_adamw_32bit",
        save_steps=25,
        logging_steps=25,
        learning_rate=2e-4,
        weight_decay=0.001,
        fp16=False,
        bf16=False,
        max_grad_norm=0.3,
        max_steps=-1,
        warmup_ratio=0.03,
        group_by_length=True,
        lr_scheduler_type="constant",
    )

    # --- Inicializar o Treinador ---
    trainer = SFTTrainer(
        model=base_model,
        train_dataset=dataset,
        peft_config=peft_parameters,
        dataset_text_field="text", # O nome da coluna no seu JSONL que contém o texto de treino
        max_seq_length=None,
        tokenizer=tokenizer,
        args=training_parameters,
        packing=False,
    )

    # --- Iniciar Treinamento ---
    print("Iniciando o processo de fine-tuning...")
    trainer.train()

    # --- Salvar o Modelo Treinado ---
    print(f"Salvando o modelo adaptado em: {output_dir}")
    trainer.model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print("Fine-tuning concluído com sucesso!")

if __name__ == "__main__":
    # É necessário ter o CUDA e as dependências corretas instaladas.
    # Este script é para ser executado no servidor com GPU.
    print("AVISO: Este script iniciará um processo de treinamento intensivo de GPU.")
    confirm = input("Você tem certeza que deseja continuar? (s/n): ")
    if confirm.lower() == 's':
        train()
    else:
        print("Treinamento cancelado.")
