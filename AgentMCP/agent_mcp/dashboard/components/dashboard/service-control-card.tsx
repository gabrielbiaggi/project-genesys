// components/dashboard/service-control-card.tsx
import { useState, useEffect, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Power, PowerOff, Loader2, Server, RefreshCw } from 'lucide-react'
import { apiClient } from '@/lib/api'
import { useToast } from '@/hooks/use-toast'

type ServiceName = 'backend' | 'frontend'

interface ServiceStatus {
  status: 'running' | 'stopped' | 'error';
  pid: number | null;
}

interface ServiceStatusResponse {
  backend: ServiceStatus;
  frontend: ServiceStatus;
}

interface ServiceControlCardProps {
  serviceName: ServiceName;
  title: string;
  description: string;
}

export function ServiceControlCard({ serviceName, title, description }: ServiceControlCardProps) {
  const [serviceStatus, setServiceStatus] = useState<ServiceStatus | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isActionLoading, setActionLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { toast } = useToast()

  const fetchStatus = useCallback(async () => {
    // Don't show main loader during background refresh
    if (!isLoading) {
      // Small visual cue could be added here if desired
    }
    
    try {
      const data = await apiClient.request<ServiceStatusResponse>('/api/dashboard/service-status')
      setServiceStatus(data[serviceName])
      setError(null)
    } catch (err) {
      setError(`Falha ao buscar status do serviço ${serviceName}. API pode estar offline.`)
      setServiceStatus({ status: 'error', pid: null })
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }, [serviceName, isLoading])

  useEffect(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 5000) // Poll a cada 5 segundos
    return () => clearInterval(interval)
  }, [fetchStatus])

  const handleAction = async (action: 'start' | 'stop' | 'restart') => {
    setActionLoading(true)
    try {
      const result = await apiClient.request<{ message: string, status?: string }>('/api/dashboard/service-control', {
        method: 'POST',
        body: JSON.stringify({ action, service: serviceName }),
        headers: {
          'Content-Type': 'application/json'
        }
      })

      toast({
        title: `Ação '${action}' para ${serviceName} executada`,
        description: result.message || `O serviço está sendo ${action === 'start' ? 'iniciado' : action === 'stop' ? 'parado' : 'reiniciado'}.`,
        variant: result.status === 'error' ? 'destructive' : 'default'
      })

      // Give a moment for the process to start/stop before refreshing
      setTimeout(fetchStatus, 2000)

    } catch (err: unknown) {
      toast({
        title: `Erro ao executar '${action}' em ${serviceName}`,
        description: err instanceof Error ? err.message : 'Ocorreu um erro desconhecido.',
        variant: 'destructive',
      })
    } finally {
      setActionLoading(false)
    }
  }

  const getStatusIndicator = () => {
    if (isLoading) return <Loader2 className="w-4 h-4 text-muted-foreground animate-spin" />
    if (!serviceStatus || serviceStatus.status === 'error') return <div className="w-3 h-3 rounded-full bg-yellow-500" title="Status Desconhecido" />
    
    switch (serviceStatus.status) {
      case 'running':
        return <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse" title="Online" />
      case 'stopped':
        return <div className="w-3 h-3 rounded-full bg-red-500" title="Offline" />
      default:
        return <div className="w-3 h-3 rounded-full bg-gray-500" title="Estado inválido" />
    }
  }

  const statusText = isLoading ? 'Carregando...' : (serviceStatus?.status || 'desconhecido').replace('running', 'Online').replace('stopped', 'Offline').replace('error', 'Erro');

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Server className="w-5 h-5" />
          {title}
        </CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
          <div className="flex items-center gap-3">
            {getStatusIndicator()}
            <span className="font-medium capitalize">{statusText}</span>
          </div>
          {serviceStatus?.status === 'running' && serviceStatus.pid && (
            <div className="text-sm text-muted-foreground">
              PID: {serviceStatus.pid}
            </div>
          )}
        </div>

        {error && serviceStatus?.status === 'error' && <Alert variant="destructive"><AlertDescription>{error}</AlertDescription></Alert>}

        <div className="grid grid-cols-3 gap-2">
          <Button onClick={() => handleAction('start')} disabled={serviceStatus?.status === 'running' || isActionLoading} className="w-full flex-1">
            {isActionLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Power className="h-4 w-4" />}
          </Button>
          <Button onClick={() => handleAction('stop')} disabled={serviceStatus?.status !== 'running' || isActionLoading} variant="destructive" className="w-full flex-1">
            {isActionLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <PowerOff className="h-4 w-4" />}
          </Button>
          <Button onClick={() => handleAction('restart')} disabled={isActionLoading} variant="outline" className="w-full flex-1">
            {isActionLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
