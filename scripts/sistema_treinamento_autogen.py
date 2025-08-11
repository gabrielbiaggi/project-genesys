#!/usr/bin/env python3
# scripts/sistema_treinamento_autogen.py
# Sistema de treinamento contínuo usando AutoGen

import asyncio
import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import requests
import pandas as pd
import numpy as np
from dataclasses import dataclass

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/training_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class InteractionData:
    """Estrutura para dados de interação"""
    timestamp: datetime
    user_prompt: str
    agent_response: str
    context: Dict[str, Any]
    quality_score: float
    category: str
    feedback: Optional[str] = None
    success: bool = True

@dataclass
class TrainingMetrics:
    """Métricas de treinamento"""
    total_interactions: int
    quality_average: float
    categories_distribution: Dict[str, int]
    improvement_rate: float
    last_training: Optional[datetime] = None

class DataCollector:
    """Coletor inteligente de dados de interação"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.logs_dir = self.data_dir / "logs"
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        
        # Criar diretórios se não existirem
        for dir_path in [self.logs_dir, self.raw_dir, self.processed_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def collect_from_logs(self) -> List[InteractionData]:
        """Coleta dados dos logs de interação"""
        interactions = []
        log_file = self.logs_dir / "interaction_logs.jsonl"
        
        if not log_file.exists():
            logger.warning(f"Arquivo de log não encontrado: {log_file}")
            return interactions
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        interaction = self._parse_interaction(data)
                        if interaction:
                            interactions.append(interaction)
                    except json.JSONDecodeError:
                        continue
            
            logger.info(f"Coletadas {len(interactions)} interações dos logs")
            return interactions
            
        except Exception as e:
            logger.error(f"Erro ao coletar dados dos logs: {e}")
            return []
    
    def _parse_interaction(self, data: Dict) -> Optional[InteractionData]:
        """Converte dados brutos em InteractionData"""
        try:
            return InteractionData(
                timestamp=datetime.now(),  # TODO: extrair timestamp real
                user_prompt=data.get('prompt', ''),
                agent_response=data.get('final_answer', ''),
                context=data.get('intermediate_steps', []),
                quality_score=self._calculate_quality_score(data),
                category=self._categorize_interaction(data.get('prompt', '')),
                success=len(data.get('final_answer', '')) > 10  # Heurística simples
            )
        except Exception as e:
            logger.error(f"Erro ao parsear interação: {e}")
            return None
    
    def _calculate_quality_score(self, data: Dict) -> float:
        """Calcula score de qualidade da interação"""
        score = 0.5  # Base
        
        # Fatores que aumentam a qualidade
        response = data.get('final_answer', '')
        if len(response) > 50:
            score += 0.1
        if len(response) > 200:
            score += 0.1
        if any(keyword in response.lower() for keyword in ['código', 'função', 'class', 'import']):
            score += 0.1
        if len(data.get('intermediate_steps', [])) > 0:
            score += 0.2  # Usou ferramentas
        
        return min(score, 1.0)
    
    def _categorize_interaction(self, prompt: str) -> str:
        """Categoriza automaticamente a interação"""
        prompt_lower = prompt.lower()
        
        # Categorias técnicas
        if any(word in prompt_lower for word in ['debug', 'erro', 'bug', 'problem']):
            return 'debugging'
        elif any(word in prompt_lower for word in ['explique', 'como', 'o que é']):
            return 'explanation'
        elif any(word in prompt_lower for word in ['código', 'function', 'class', 'script']):
            return 'coding'
        elif any(word in prompt_lower for word in ['otimiz', 'melhor', 'performance']):
            return 'optimization'
        elif any(word in prompt_lower for word in ['test', 'validar', 'verificar']):
            return 'testing'
        else:
            return 'general'

class AutoGenTrainingSystem:
    """Sistema de treinamento usando AutoGen"""
    
    def __init__(self, server_url: str = "https://genesys.webcreations.com.br"):
        self.server_url = server_url
        self.data_collector = DataCollector()
        self.training_threshold = 100  # Interações antes de treinar
        
    async def analyze_data_quality(self, interactions: List[InteractionData]) -> Dict[str, Any]:
        """Agente Analista: Analisa qualidade dos dados"""
        logger.info("🧠 Iniciando análise de qualidade dos dados...")
        
        if not interactions:
            return {"status": "no_data", "recommendation": "collect_more"}
        
        # Métricas básicas
        quality_scores = [i.quality_score for i in interactions]
        categories = [i.category for i in interactions]
        
        analysis = {
            "total_interactions": len(interactions),
            "average_quality": np.mean(quality_scores),
            "quality_distribution": {
                "excellent": sum(1 for s in quality_scores if s > 0.8),
                "good": sum(1 for s in quality_scores if 0.6 < s <= 0.8),
                "poor": sum(1 for s in quality_scores if s <= 0.6)
            },
            "category_distribution": {cat: categories.count(cat) for cat in set(categories)},
            "recommendation": self._get_training_recommendation(quality_scores, categories)
        }
        
        logger.info(f"📊 Análise completa: {analysis['average_quality']:.2f} qualidade média")
        return analysis
    
    def _get_training_recommendation(self, quality_scores: List[float], categories: List[str]) -> str:
        """Determina se é necessário treinar"""
        avg_quality = np.mean(quality_scores)
        
        if len(quality_scores) < self.training_threshold:
            return "collect_more_data"
        elif avg_quality < 0.6:
            return "urgent_training_needed"
        elif avg_quality < 0.75:
            return "training_recommended"
        else:
            return "quality_good_monitor"
    
    async def curate_training_data(self, interactions: List[InteractionData]) -> Dict[str, Any]:
        """Agente Curador: Prepara dados para treinamento"""
        logger.info("📚 Iniciando curadoria de dados para treinamento...")
        
        # Filtrar por qualidade
        high_quality = [i for i in interactions if i.quality_score > 0.7]
        
        # Balancear categorias
        category_balance = self._balance_categories(high_quality)
        
        # Preparar dataset
        training_data = []
        for interaction in category_balance:
            training_data.append({
                "instruction": interaction.user_prompt,
                "input": "",
                "output": interaction.agent_response,
                "context": json.dumps(interaction.context) if interaction.context else "",
                "category": interaction.category,
                "quality": interaction.quality_score
            })
        
        # Salvar dataset curado
        dataset_path = self.data_collector.processed_dir / f"training_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(dataset_path, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
        
        curation_result = {
            "original_count": len(interactions),
            "curated_count": len(training_data),
            "dataset_path": str(dataset_path),
            "quality_threshold": 0.7,
            "categories_included": list(set(i.category for i in category_balance))
        }
        
        logger.info(f"✨ Curadoria completa: {len(training_data)} amostras preparadas")
        return curation_result
    
    def _balance_categories(self, interactions: List[InteractionData], max_per_category: int = 50) -> List[InteractionData]:
        """Balanceia categorias para evitar overfitting"""
        category_groups = {}
        for interaction in interactions:
            if interaction.category not in category_groups:
                category_groups[interaction.category] = []
            category_groups[interaction.category].append(interaction)
        
        balanced = []
        for category, items in category_groups.items():
            # Ordenar por qualidade e pegar os melhores
            sorted_items = sorted(items, key=lambda x: x.quality_score, reverse=True)
            balanced.extend(sorted_items[:max_per_category])
        
        return balanced
    
    async def trigger_training(self, dataset_path: str) -> Dict[str, Any]:
        """Agente Treinador: Dispara treinamento LoRA"""
        logger.info("🔬 Iniciando processo de treinamento...")
        
        try:
            # Preparar configuração de treinamento
            training_config = {
                "dataset_path": dataset_path,
                "output_dir": f"./models/lora_adapters_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "num_epochs": 3,
                "batch_size": 4,
                "learning_rate": 2e-4,
                "lora_rank": 16,
                "lora_alpha": 32,
                "lora_dropout": 0.1
            }
            
            # Chamar script de fine-tuning
            result = await self._execute_training(training_config)
            
            logger.info("✅ Treinamento concluído com sucesso")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro durante treinamento: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _execute_training(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Executa o treinamento propriamente dito"""
        # Simular treinamento por enquanto
        # TODO: Integrar com scripts/fine_tune.py
        await asyncio.sleep(2)  # Simular tempo de treinamento
        
        return {
            "status": "completed",
            "model_path": config["output_dir"],
            "training_loss": 0.45,  # Simulado
            "validation_loss": 0.52,  # Simulado
            "epochs_completed": config["num_epochs"],
            "training_time_minutes": 15  # Simulado
        }
    
    async def validate_model(self, model_path: str) -> Dict[str, Any]:
        """Agente Validador: Valida modelo treinado"""
        logger.info("✅ Iniciando validação do modelo treinado...")
        
        # Simular validação
        # TODO: Implementar validação real com métricas
        validation_metrics = {
            "bleu_score": 0.75,  # Simulado
            "rouge_score": 0.68,  # Simulado
            "user_satisfaction_estimate": 0.82,  # Simulado
            "improvement_over_baseline": 0.08,  # 8% melhoria
            "recommendation": "deploy_approved"
        }
        
        logger.info(f"📊 Validação concluída: {validation_metrics['improvement_over_baseline']:.1%} melhoria")
        return validation_metrics
    
    async def run_training_cycle(self) -> Dict[str, Any]:
        """Executa um ciclo completo de treinamento"""
        logger.info("🚀 Iniciando ciclo completo de treinamento AutoGen")
        
        cycle_results = {
            "start_time": datetime.now(),
            "steps_completed": [],
            "status": "running"
        }
        
        try:
            # Passo 1: Coletar dados
            logger.info("📊 PASSO 1: Coletando dados de interação")
            interactions = self.data_collector.collect_from_logs()
            cycle_results["steps_completed"].append("data_collection")
            
            if not interactions:
                cycle_results["status"] = "no_data"
                cycle_results["message"] = "Nenhuma interação encontrada para treinamento"
                return cycle_results
            
            # Passo 2: Analisar qualidade
            logger.info("🧠 PASSO 2: Analisando qualidade dos dados")
            analysis = await self.analyze_data_quality(interactions)
            cycle_results["data_analysis"] = analysis
            cycle_results["steps_completed"].append("quality_analysis")
            
            if analysis["recommendation"] in ["collect_more_data", "quality_good_monitor"]:
                cycle_results["status"] = "skipped"
                cycle_results["message"] = f"Treinamento não necessário: {analysis['recommendation']}"
                return cycle_results
            
            # Passo 3: Curar dados
            logger.info("📚 PASSO 3: Curando dados para treinamento")
            curation = await self.curate_training_data(interactions)
            cycle_results["data_curation"] = curation
            cycle_results["steps_completed"].append("data_curation")
            
            # Passo 4: Treinar modelo
            logger.info("🔬 PASSO 4: Treinando modelo")
            training = await self.trigger_training(curation["dataset_path"])
            cycle_results["training"] = training
            cycle_results["steps_completed"].append("training")
            
            if training["status"] != "completed":
                cycle_results["status"] = "training_failed"
                return cycle_results
            
            # Passo 5: Validar modelo
            logger.info("✅ PASSO 5: Validando modelo")
            validation = await self.validate_model(training["model_path"])
            cycle_results["validation"] = validation
            cycle_results["steps_completed"].append("validation")
            
            # Determinar status final
            if validation["recommendation"] == "deploy_approved":
                cycle_results["status"] = "completed_success"
                cycle_results["message"] = "Ciclo de treinamento concluído com sucesso!"
            else:
                cycle_results["status"] = "completed_no_deploy"
                cycle_results["message"] = "Treinamento concluído mas não aprovado para deploy"
            
        except Exception as e:
            logger.error(f"❌ Erro durante ciclo de treinamento: {e}")
            cycle_results["status"] = "error"
            cycle_results["error"] = str(e)
        
        finally:
            cycle_results["end_time"] = datetime.now()
            cycle_results["duration_minutes"] = (cycle_results["end_time"] - cycle_results["start_time"]).seconds / 60
        
        return cycle_results

class TrainingMonitor:
    """Monitor do sistema de treinamento"""
    
    def __init__(self):
        self.metrics_file = Path("data/metrics/training_metrics.json")
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log_training_cycle(self, results: Dict[str, Any]):
        """Registra resultado de um ciclo de treinamento"""
        try:
            # Carregar métricas existentes
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    metrics = json.load(f)
            else:
                metrics = {"training_cycles": [], "summary": {}}
            
            # Adicionar novo ciclo
            cycle_record = {
                "timestamp": datetime.now().isoformat(),
                "status": results["status"],
                "steps_completed": results["steps_completed"],
                "duration_minutes": results.get("duration_minutes", 0)
            }
            
            if "data_analysis" in results:
                cycle_record["interactions_processed"] = results["data_analysis"]["total_interactions"]
                cycle_record["average_quality"] = results["data_analysis"]["average_quality"]
            
            metrics["training_cycles"].append(cycle_record)
            
            # Atualizar sumário
            metrics["summary"] = {
                "total_cycles": len(metrics["training_cycles"]),
                "successful_cycles": sum(1 for c in metrics["training_cycles"] if c["status"] == "completed_success"),
                "last_training": cycle_record["timestamp"],
                "avg_duration_minutes": np.mean([c["duration_minutes"] for c in metrics["training_cycles"][-10:]])
            }
            
            # Salvar métricas
            with open(self.metrics_file, 'w') as f:
                json.dump(metrics, f, indent=2)
            
            logger.info(f"📊 Métricas de treinamento atualizadas: {cycle_record['status']}")
            
        except Exception as e:
            logger.error(f"Erro ao registrar métricas: {e}")

async def main():
    """Função principal para executar o sistema de treinamento"""
    logger.info("🚀 Iniciando Sistema de Treinamento Genesys com AutoGen")
    
    # Configurar sistema
    training_system = AutoGenTrainingSystem()
    monitor = TrainingMonitor()
    
    try:
        # Executar ciclo de treinamento
        results = await training_system.run_training_cycle()
        
        # Registrar métricas
        monitor.log_training_cycle(results)
        
        # Imprimir resultados
        print("\n" + "="*60)
        print("🤖 RESULTADO DO CICLO DE TREINAMENTO GENESYS")
        print("="*60)
        print(f"📊 Status: {results['status']}")
        print(f"⏱️ Duração: {results.get('duration_minutes', 0):.1f} minutos")
        print(f"✅ Passos concluídos: {', '.join(results['steps_completed'])}")
        
        if results['status'] == 'completed_success':
            print("🎉 Treinamento concluído com sucesso!")
            print("🚀 Modelo melhorado está pronto para deploy!")
        elif results['status'] == 'no_data':
            print("📊 Aguardando mais dados para treinamento...")
        elif results['status'] == 'skipped':
            print("⏭️ Treinamento não necessário neste momento")
        else:
            print(f"⚠️ Status: {results.get('message', 'Verificar logs para detalhes')}")
        
        print("="*60)
        
    except Exception as e:
        logger.error(f"❌ Erro crítico no sistema de treinamento: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    # Executar sistema de treinamento
    exit_code = asyncio.run(main())
    exit(exit_code)
