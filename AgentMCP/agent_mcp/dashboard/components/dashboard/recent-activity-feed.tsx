"use client"

import { useState, useEffect, useCallback } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { Clock, Terminal, FileText, Bot } from 'lucide-react'
import { apiClient } from '@/lib/api'
import { formatRelativeTime } from '@/lib/utils'

interface Activity {
  timestamp: string;
  agent_id: string;
  action_type: string;
  details: string | null;
}

const ActionIcon = ({ action_type }: { action_type: string }) => {
  if (action_type.includes('task')) return <FileText className="h-4 w-4" />
  if (action_type.includes('agent')) return <Bot className="h-4 w-4" />
  return <Terminal className="h-4 w-4" />
}

const ActivityItem = ({ activity }: { activity: Activity }) => {
  return (
    <div className="flex items-start gap-4 p-3 hover:bg-muted/50 rounded-lg">
      <div className="flex-shrink-0 mt-1">
        <ActionIcon action_type={activity.action_type} />
      </div>
      <div className="flex-1">
        <p className="text-sm">
          <span className="font-semibold text-primary">{activity.agent_id}</span>
          {' '}{activity.action_type.replace(/_/g, ' ')}
        </p>
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <p className="text-xs text-muted-foreground flex items-center gap-1.5 mt-1">
                <Clock className="h-3 w-3" />
                {formatRelativeTime(activity.timestamp)}
              </p>
            </TooltipTrigger>
            <TooltipContent>
              {new Date(activity.timestamp).toLocaleString()}
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>
    </div>
  )
}

export function RecentActivityFeed() {
  const [activities, setActivities] = useState<Activity[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const fetchActivities = useCallback(async () => {
    try {
      const data = await apiClient.request<Activity[]>('/api/dashboard/recent-activity?limit=50')
      setActivities(data)
    } catch (error) {
      console.error("Failed to fetch recent activities:", error)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchActivities()
    const interval = setInterval(fetchActivities, 15000) // Poll every 15 seconds
    return () => clearInterval(interval)
  }, [fetchActivities])

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-72">
          {isLoading ? (
            <p className="text-muted-foreground">Loading activities...</p>
          ) : activities.length > 0 ? (
            <div className="space-y-2">
              {activities.map((activity, index) => (
                <ActivityItem key={`${activity.timestamp}-${index}`} activity={activity} />
              ))}
            </div>
          ) : (
            <p className="text-muted-foreground">No recent activity found.</p>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
