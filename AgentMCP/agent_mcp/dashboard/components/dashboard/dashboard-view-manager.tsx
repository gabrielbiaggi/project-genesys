"use client"

import React, { useEffect, useState } from 'react'
import { OverviewDashboard } from "@/components/dashboard/overview-dashboard"
import { AgentsDashboard } from "@/components/dashboard/agents-dashboard"
import { TasksDashboard } from "@/components/dashboard/tasks-dashboard"
import { MemoriesDashboard } from "@/components/dashboard/memories-dashboard"
import { PromptBookDashboard } from "@/components/dashboard/prompt-book-dashboard"
import { SystemDashboard } from "@/components/dashboard/system-dashboard"
import { useDashboard } from "@/lib/store"

export function DashboardViewManager() {
  const { currentView } = useDashboard()
  const [isClient, setIsClient] = useState(false)

  useEffect(() => {
    setIsClient(true)
  }, [])

  if (!isClient) {
    // Render a placeholder or nothing on the server
    return <OverviewDashboard />
  }

  const renderCurrentView = () => {
    switch (currentView) {
      case 'overview':
        return <OverviewDashboard />
      case 'agents':
        return <AgentsDashboard />
      case 'tasks':
        return <TasksDashboard />
      case 'memories':
        return <MemoriesDashboard />
      case 'prompts':
        return <PromptBookDashboard />
      case 'system':
        return <SystemDashboard />
      default:
        // Fallback to overview if view is unknown
        return <OverviewDashboard />
    }
  }

  return <>{renderCurrentView()}</>
}
