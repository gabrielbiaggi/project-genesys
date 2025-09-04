// components/dashboard/service-control-card.tsx
import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Power, PowerOff, Loader2, Server } from 'lucide-react'
import { apiClient } from '@/lib/api'
import { useToast } from '@/hooks/use-toast'

type ServiceStatus = 'running' | 'stopped' | 'loading' | 'error'

interface StatusDetails {
  pid: number | null
  cpu_percent?: number
  memory_mb?: number
}

export function ServiceControlCard() {
  const [status, setStatus] = useState<ServiceStatus>('loading')
  const [details, setDetails] = useState<StatusDetails | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isActionLoading, setActionLoading] = useState(false)
  const { toast } = useToast()

  const fetchStatus = async () => {
    try {
      const data = await apiClient.getGenesysServiceStatus()
      setStatus(data.status)
      setDetails({ pid: data.pid, cpu_percent: data.cpu_percent, memory_mb: data.memory_mb })
    } catch (err) {
      setError('Falha ao comunicar com o servidor Agent-MCP.')
      setStatus('error')
    }
  }

  useEffect(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 5000) // Poll every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const handleStart = async () => {
    setActionLoading(true)
    try {
      const result = await apiClient.startGenesysService()
      if (result.status === 'started' || result.status === 'already_running') {
        toast({
          title: "Sucesso",
          description: result.message,
        })
        await fetchStatus()
      } else {
        throw new Error(result.message)
      }
    } catch (err: any) {
      toast({
        title: "Erro ao Iniciar Serviço",
        description: err.message || 'Ocorreu um erro desconhecido.',
        variant: 'destructive',
      })
    } finally {
      setActionLoading(false)
    }
  }

  const handleStop = async () => {
    setActionLoading(true)
    try {
      const result = await apiClient.stopGenesysService()
      if (result.status === 'stopped' || result.status === 'not_running') {
        toast({
          title: "Sucesso",
          description: result.message,
        })
        await fetchStatus()
      } else {
        throw new Error(result.message)
      }
    } catch (err: any) {
      toast({
        title: "Erro ao Parar Serviço",
        description: err.message || 'Ocorreu um erro desconhecido.',
        variant: 'destructive',
      })
    } finally {
      setActionLoading(false)
    }
  }

  const getStatusIndicator = () => {
    switch (status) {
      case 'running':
        return <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
      case 'stopped':
        return <div className="w-3 h-3 rounded-full bg-red-500" />
      case 'loading':
        return <Loader2 className="w-3 h-3 animate-spin" />
      default:
        return <div className="w-3 h-3 rounded-full bg-yellow-500" />
    }
  }
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Server className="w-5 h-5" />
          Controle do Agente Genesys
        </CardTitle>
        <CardDescription>
          Inicie ou pare o serviço do Genesys Agent remotamente.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
          <div className="flex items-center gap-3">
            {getStatusIndicator()}
            <span className="font-medium capitalize">{status}</span>
          </div>
          {status === 'running' && details?.pid && (
            <div className="text-sm text-muted-foreground">
              PID: {details.pid} | CPU: {details.cpu_percent?.toFixed(1)}% | Mem: {details.memory_mb?.toFixed(0)} MB
            </div>
          )}
        </div>

        {error && <Alert variant="destructive"><AlertDescription>{error}</AlertDescription></Alert>}

        <div className="flex gap-4">
          <Button onClick={handleStart} disabled={status === 'running' || isActionLoading} className="w-full">
            {isActionLoading && status !== 'running' ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Power className="mr-2 h-4 w-4" />}
            Iniciar Genesys
          </Button>
          <Button onClick={handleStop} disabled={status === 'stopped' || isActionLoading} variant="destructive" className="w-full">
            {isActionLoading && status === 'running' ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <PowerOff className="mr-2 h-4 w-4" />}
            Parar Genesys
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
