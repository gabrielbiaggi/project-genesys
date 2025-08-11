#!/usr/bin/env python3
# scripts/monitor_treinamento_notebook.py
# Script para monitorar e controlar treinamento via notebook

import requests
import json
import time
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

class GenesysTrainingMonitor:
    """Monitor de treinamento para uso em notebook"""
    
    def __init__(self, server_url: str = "https://genesys.webcreations.com.br"):
        self.server_url = server_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 30
        
    def check_server_status(self) -> Dict[str, any]:
        """Verifica status do servidor"""
        try:
            response = self.session.get(f"{self.server_url}/")
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "online",
                    "message": data.get("message", ""),
                    "agent_loaded": "carregado" not in data.get("message", "").lower()
                }
            else:
                return {
                    "status": "error",
                    "message": f"HTTP {response.status_code}",
                    "agent_loaded": False
                }
        except Exception as e:
            return {
                "status": "offline",
                "message": str(e),
                "agent_loaded": False
            }
    
    def get_interaction_stats(self) -> Dict[str, any]:
        """Obtém estatísticas de interações (simulado)"""
        # TODO: Implementar endpoint real no servidor
        # Por enquanto, simular dados baseados em logs locais
        try:
            logs_path = Path("data/logs/interaction_logs.jsonl")
            if not logs_path.exists():
                return {
                    "total_interactions": 0,
                    "last_24h": 0,
                    "categories": {},
                    "quality_avg": 0.0
                }
            
            # Simular estatísticas
            return {
                "total_interactions": 145,
                "last_24h": 23,
                "categories": {
                    "coding": 45,
                    "debugging": 32,
                    "explanation": 38,
                    "optimization": 20,
                    "general": 10
                },
                "quality_avg": 0.78,
                "ready_for_training": True
            }
            
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {e}")
            return {}
    
    def trigger_training_cycle(self) -> Dict[str, any]:
        """Dispara um ciclo de treinamento remotamente"""
        try:
            # Simular chamada para endpoint de treinamento
            print("🚀 Disparando ciclo de treinamento remoto...")
            
            # TODO: Implementar endpoint real
            # response = self.session.post(f"{self.server_url}/training/trigger")
            
            # Simular resposta
            time.sleep(2)
            return {
                "status": "initiated",
                "cycle_id": f"cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "estimated_duration": "10-15 minutos",
                "message": "Ciclo de treinamento iniciado com sucesso"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_training_status(self, cycle_id: str = None) -> Dict[str, any]:
        """Verifica status do treinamento em andamento"""
        try:
            # Simular status de treinamento
            return {
                "status": "running",
                "current_step": "data_curation",
                "progress": 0.65,
                "eta_minutes": 8,
                "steps_completed": ["data_collection", "quality_analysis"],
                "current_metrics": {
                    "interactions_processed": 145,
                    "quality_score": 0.78,
                    "training_samples": 89
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_model_performance_history(self) -> pd.DataFrame:
        """Obtém histórico de performance do modelo"""
        # Simular dados históricos
        dates = pd.date_range(start='2024-01-01', end=datetime.now(), freq='D')
        data = []
        
        base_quality = 0.65
        for i, date in enumerate(dates):
            # Simular melhoria gradual com ruído
            quality = base_quality + (i * 0.001) + (np.random.random() * 0.1 - 0.05)
            quality = max(0.5, min(1.0, quality))
            
            data.append({
                'date': date,
                'quality_score': quality,
                'interactions_count': np.random.randint(10, 50),
                'success_rate': quality * 0.9 + np.random.random() * 0.1
            })
        
        return pd.DataFrame(data)
    
    def plot_performance_dashboard(self):
        """Cria dashboard visual de performance"""
        try:
            import numpy as np
            
            # Obter dados
            df = self.get_model_performance_history()
            stats = self.get_interaction_stats()
            
            # Configurar matplotlib para notebook
            plt.style.use('seaborn-v0_8')
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('📊 Dashboard de Performance Genesys IA', fontsize=16, fontweight='bold')
            
            # Gráfico 1: Qualidade ao longo do tempo
            ax1.plot(df['date'], df['quality_score'], linewidth=2, color='#2E86AB')
            ax1.set_title('🎯 Evolução da Qualidade', fontweight='bold')
            ax1.set_ylabel('Score de Qualidade')
            ax1.grid(True, alpha=0.3)
            ax1.set_ylim(0.5, 1.0)
            
            # Gráfico 2: Distribuição de categorias
            categories = stats.get('categories', {})
            if categories:
                colors = ['#F24236', '#F6AE2D', '#2E86AB', '#A23B72', '#F18F01']
                ax2.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%', 
                       colors=colors[:len(categories)])
                ax2.set_title('📂 Distribuição por Categoria', fontweight='bold')
            
            # Gráfico 3: Interações por dia
            daily_interactions = df.groupby(df['date'].dt.date)['interactions_count'].sum()
            ax3.bar(range(len(daily_interactions[-30:])), daily_interactions[-30:], 
                   color='#A23B72', alpha=0.7)
            ax3.set_title('📈 Interações Diárias (Últimos 30 dias)', fontweight='bold')
            ax3.set_ylabel('Número de Interações')
            ax3.grid(True, alpha=0.3)
            
            # Gráfico 4: Taxa de sucesso
            ax4.plot(df['date'], df['success_rate'], linewidth=2, color='#F6AE2D')
            ax4.set_title('✅ Taxa de Sucesso', fontweight='bold')
            ax4.set_ylabel('Taxa de Sucesso (%)')
            ax4.grid(True, alpha=0.3)
            ax4.set_ylim(0.6, 1.0)
            
            plt.tight_layout()
            plt.show()
            
            # Estatísticas resumidas
            print("\n" + "="*60)
            print("📊 RESUMO DE PERFORMANCE ATUAL")
            print("="*60)
            print(f"🎯 Qualidade Média: {stats.get('quality_avg', 0):.2%}")
            print(f"📈 Total de Interações: {stats.get('total_interactions', 0)}")
            print(f"⏰ Últimas 24h: {stats.get('last_24h', 0)} interações")
            print(f"🚀 Pronto para Treinamento: {'✅ SIM' if stats.get('ready_for_training') else '❌ NÃO'}")
            print("="*60)
            
        except ImportError:
            print("⚠️ matplotlib não disponível. Instale com: pip install matplotlib")
        except Exception as e:
            print(f"❌ Erro ao criar dashboard: {e}")
    
    def start_training_with_monitoring(self):
        """Inicia treinamento e monitora progresso"""
        print("🚀 INICIANDO CICLO DE TREINAMENTO COM MONITORAMENTO")
        print("="*60)
        
        # Verificar servidor
        status = self.check_server_status()
        print(f"🌐 Status do Servidor: {status['status']}")
        print(f"🤖 Agente Carregado: {'✅' if status['agent_loaded'] else '❌'}")
        
        if status['status'] != 'online':
            print("❌ Servidor não está acessível. Verifique a conexão.")
            return
        
        # Obter estatísticas
        stats = self.get_interaction_stats()
        print(f"📊 Interações Disponíveis: {stats.get('total_interactions', 0)}")
        print(f"🎯 Qualidade Média: {stats.get('quality_avg', 0):.2%}")
        
        if not stats.get('ready_for_training', False):
            print("⚠️ Dados insuficientes para treinamento. Aguardando mais interações...")
            return
        
        # Disparar treinamento
        training_result = self.trigger_training_cycle()
        if training_result['status'] != 'initiated':
            print(f"❌ Falha ao iniciar treinamento: {training_result.get('message')}")
            return
        
        cycle_id = training_result['cycle_id']
        print(f"✅ Treinamento iniciado: {cycle_id}")
        print(f"⏱️ Tempo estimado: {training_result['estimated_duration']}")
        
        # Monitorar progresso
        print("\n🔄 Monitorando progresso...")
        while True:
            status = self.get_training_status(cycle_id)
            
            if status['status'] == 'running':
                progress = status.get('progress', 0) * 100
                step = status.get('current_step', 'unknown')
                eta = status.get('eta_minutes', 0)
                
                print(f"\r📊 {step}: {progress:.1f}% - ETA: {eta}min", end="", flush=True)
                time.sleep(10)  # Verificar a cada 10 segundos
                
            elif status['status'] == 'completed':
                print(f"\n✅ Treinamento concluído com sucesso!")
                break
                
            elif status['status'] == 'error':
                print(f"\n❌ Erro durante treinamento: {status.get('message')}")
                break
                
            else:
                print(f"\n⚠️ Status desconhecido: {status['status']}")
                break
        
        print("\n" + "="*60)
        print("🎯 TREINAMENTO FINALIZADO")
        print("="*60)

def main():
    """Função principal para uso em notebook"""
    monitor = GenesysTrainingMonitor()
    
    print("🤖 MONITOR DE TREINAMENTO GENESYS")
    print("="*50)
    print("Comandos disponíveis:")
    print("1. monitor.check_server_status() - Verificar servidor")
    print("2. monitor.get_interaction_stats() - Ver estatísticas")
    print("3. monitor.plot_performance_dashboard() - Dashboard visual")
    print("4. monitor.start_training_with_monitoring() - Iniciar treinamento")
    print("="*50)
    
    return monitor

# Para uso em notebook
if __name__ == "__main__":
    # Se executado como script, iniciar interface interativa
    monitor = main()
    
    # Menu interativo
    while True:
        print("\n" + "="*50)
        print("🎛️ MENU INTERATIVO")
        print("="*50)
        print("1. 📊 Verificar Status do Servidor")
        print("2. 📈 Ver Estatísticas de Interação")
        print("3. 🎯 Dashboard Visual")
        print("4. 🚀 Iniciar Treinamento Monitorado")
        print("5. ❌ Sair")
        
        try:
            choice = input("\n🔹 Escolha uma opção (1-5): ").strip()
            
            if choice == '1':
                status = monitor.check_server_status()
                print(f"\n🌐 Status: {status}")
                
            elif choice == '2':
                stats = monitor.get_interaction_stats()
                print(f"\n📊 Estatísticas: {stats}")
                
            elif choice == '3':
                monitor.plot_performance_dashboard()
                
            elif choice == '4':
                monitor.start_training_with_monitoring()
                
            elif choice == '5':
                print("👋 Saindo...")
                break
                
            else:
                print("⚠️ Opção inválida. Tente novamente.")
                
        except KeyboardInterrupt:
            print("\n👋 Saindo...")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")

# Para uso em Jupyter notebook, criar instância direta
try:
    # Detectar se está em notebook
    get_ipython()
    notebook_monitor = main()
    print("✅ Monitor carregado! Use 'notebook_monitor' para interagir.")
except NameError:
    # Não está em notebook, executar normalmente
    pass
