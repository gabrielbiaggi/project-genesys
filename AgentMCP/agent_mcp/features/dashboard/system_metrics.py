import psutil
import logging
from typing import Dict, Any, Optional

# Configurar um logger básico para este módulo
logger = logging.getLogger(__name__)

# Tentar importar a biblioteca da NVIDIA
try:
    import pynvml

    pynvml.nvmlInit()
    NVIDIA_GPU_AVAILABLE = True
except (ImportError, pynvml.NVMLError) as e:
    logger.warning(
        f"Biblioteca NVIDIA (pynvml) não encontrada ou falhou ao iniciar. Monitoramento de GPU desabilitado. Erro: {e}"
    )
    NVIDIA_GPU_AVAILABLE = False


def get_gpu_metrics() -> Optional[Dict[str, Any]]:
    """
    Coleta métricas da GPU NVIDIA se a biblioteca pynvml estiver disponível.

    Retorna um dicionário com utilização da GPU e uso de memória, ou None se não for possível.
    """
    if not NVIDIA_GPU_AVAILABLE:
        return None

    try:
        device_count = pynvml.nvmlDeviceGetCount()
        if device_count == 0:
            return None

        # Foco na primeira GPU, comum para a maioria dos setups de desktop
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)

        # Coletar utilização da GPU
        utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)

        # Coletar uso de memória
        memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)

        return {
            "gpu_utilization": utilization.gpu,
            "memory_utilization": utilization.memory,
            "memory_total": memory_info.total,
            "memory_used": memory_info.used,
            "memory_free": memory_info.free,
        }
    except pynvml.NVMLError as e:
        logger.error(f"Erro ao coletar métricas da GPU: {e}")
        return None


def get_system_metrics() -> Dict[str, Any]:
    """
    Coleta métricas gerais do sistema (CPU, Memória) e da GPU.
    """
    # Métricas de CPU
    cpu_percent = psutil.cpu_percent(interval=1)

    # Métricas de Memória RAM
    memory = psutil.virtual_memory()

    # Métricas da GPU
    gpu_metrics = get_gpu_metrics()

    return {
        "cpu_utilization": cpu_percent,
        "memory_utilization": memory.percent,
        "memory_total": memory.total,
        "memory_used": memory.used,
        "gpu": gpu_metrics,
        "gpu_available": NVIDIA_GPU_AVAILABLE,
    }


def shutdown_gpu_monitoring():
    """
    Encerra a conexão com a biblioteca NVML de forma limpa.
    """
    if NVIDIA_GPU_AVAILABLE:
        try:
            pynvml.nvmlShutdown()
            logger.info("Monitoramento de GPU encerrado com sucesso.")
        except pynvml.NVMLError as e:
            logger.error(f"Erro ao encerrar o monitoramento de GPU: {e}")
