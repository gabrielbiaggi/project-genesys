import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Cpu, MemoryStick, HardDrive } from 'lucide-react'
import { useDataStore } from '@/lib/stores/data-store'
import { apiClient } from '@/lib/api'
import { ServiceControlCard } from './service-control-card'

interface SystemUsage {
  cpu_percent: number;
  memory_percent: number;
  disk_percent: number;
}

export function SystemDashboard() {
  const [usage, setUsage] = useState<SystemUsage | null>(null)
  const [error, setError] = useState<string | null>(null)
  const adminToken = useDataStore((state) => state.getAdminToken())

  useEffect(() => {
    const fetchUsage = async () => {
      if (!adminToken) {
        setError("Admin token not available. Cannot fetch system stats.")
        return
      }
      try {
        const data = await apiClient.request<SystemUsage>('/api/system/usage', {
          headers: { 'Authorization': `Bearer ${adminToken}` }
        })
        setUsage(data)
        setError(null)
      } catch (err) {
        setError('Failed to fetch system usage data.')
        console.error(err)
      }
    };

    fetchUsage()
    const interval = setInterval(fetchUsage, 5000) // Poll every 5 seconds

    return () => clearInterval(interval)
  }, [adminToken])

  const getProgressColor = (value: number) => {
    if (value > 90) return "bg-red-500"
    if (value > 75) return "bg-yellow-500"
    return "bg-green-500"
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  if (!usage) {
    return <div>Loading system stats...</div>
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">CPU Usage</CardTitle>
          <Cpu className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{usage.cpu_percent.toFixed(1)}%</div>
          <Progress value={usage.cpu_percent} className="w-full mt-2" indicatorClassName={getProgressColor(usage.cpu_percent)} />
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Memory Usage</CardTitle>
          <MemoryStick className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{usage.memory_percent.toFixed(1)}%</div>
          <Progress value={usage.memory_percent} className="w-full mt-2" indicatorClassName={getProgressColor(usage.memory_percent)} />
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Disk Usage</CardTitle>
          <HardDrive className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{usage.disk_percent.toFixed(1)}%</div>
          <Progress value={usage.disk_percent} className="w-full mt-2" indicatorClassName={getProgressColor(usage.disk_percent)} />
        </CardContent>
      </Card>
      <ServiceControlCard />
    </div>
  )
}