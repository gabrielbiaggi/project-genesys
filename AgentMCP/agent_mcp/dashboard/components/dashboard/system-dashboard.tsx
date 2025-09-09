import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Cpu, MemoryStick, Zap } from 'lucide-react' // Adicionar Zap icon para GPU
import { apiClient } from '@/lib/api'
import { ServiceControlCard } from './service-control-card'

// Nova interface para corresponder à API de métricas do sistema
interface SystemMetrics {
  cpu_utilization: number;
  memory_utilization: number;
  gpu_available: boolean;
  gpu?: {
    gpu_utilization: number;
    memory_utilization: number;
    memory_total: number;
    memory_used: number;
  };
}

export function SystemDashboard() {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        // Usar o novo endpoint que não requer token
        const data = await apiClient.request<SystemMetrics>('/api/dashboard/system-metrics')
        setMetrics(data)
        setError(null)
      } catch (err) {
        setError('Falha ao buscar dados de métricas do sistema.')
        console.error(err)
      }
    };

    fetchMetrics()
    const interval = setInterval(fetchMetrics, 3000) // Poll a cada 3 segundos

    return () => clearInterval(interval)
  }, [])

  const getProgressColor = (value: number) => {
    if (value > 90) return "bg-red-500"
    if (value > 75) return "bg-yellow-500"
    return "bg-green-500"
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${parseFloat((bytes / Math.pow(1024, i)).toFixed(2))} ${['B', 'KB', 'MB', 'GB', 'TB'][i]}`;
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Erro de Conexão com API</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  if (!metrics) {
    return <div>Carregando estatísticas do sistema...</div>
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Uso de CPU</CardTitle>
          <Cpu className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{metrics.cpu_utilization.toFixed(1)}%</div>
          <Progress value={metrics.cpu_utilization} className="w-full mt-2" indicatorClassName={getProgressColor(metrics.cpu_utilization)} />
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Uso de Memória (RAM)</CardTitle>
          <MemoryStick className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{metrics.memory_utilization.toFixed(1)}%</div>
          <Progress value={metrics.memory_utilization} className="w-full mt-2" indicatorClassName={getProgressColor(metrics.memory_utilization)} />
        </CardContent>
      </Card>
      
      {/* Card da GPU - renderização condicional */}
      {metrics.gpu_available && metrics.gpu ? (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Uso de GPU</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.gpu.gpu_utilization.toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground mt-1">
              Memória GPU: {formatBytes(metrics.gpu.memory_used)} / {formatBytes(metrics.gpu.memory_total)}
            </p>
            <Progress value={metrics.gpu.gpu_utilization} className="w-full mt-2" indicatorClassName={getProgressColor(metrics.gpu.gpu_utilization)} />
          </CardContent>
        </Card>
      ) : (
        <Card className="flex items-center justify-center bg-muted/20 border-dashed">
            <CardContent className="text-center py-4">
                <Zap className="h-6 w-6 text-muted-foreground mx-auto mb-2" />
                <p className="text-sm font-medium text-muted-foreground">GPU não detectada</p>
                <p className="text-xs text-muted-foreground/70">pynvml não disponível</p>
            </CardContent>
        </Card>
      )}

      {/* Placeholder para outro card ou controle de serviço */}
      <ServiceControlCard 
        serviceName="backend" 
        title="Agent-MCP Backend" 
        description="Serviço principal da API e dos agentes."
      />
      <ServiceControlCard 
        serviceName="frontend" 
        title="Dashboard Frontend" 
        description="Interface de usuário para gerenciamento."
      />
    </div>
  )
}