"use client"

import React, { useState, useEffect } from "react"
import { Server } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { useServerStore } from "@/lib/stores/server-store"
import { useDataStore } from "@/lib/stores/data-store"
import { VisGraph } from "./vis-graph"
import { NodeDetailPanel } from "./node-detail-panel"
import { CORSDiagnostic } from "../debug/cors-diagnostic"
import { RecentActivityFeed } from './recent-activity-feed' // Importar o novo componente

export function OverviewDashboard() {
  const { servers, activeServerId } = useServerStore()
  const activeServer = servers.find(s => s.id === activeServerId)
  const { fetchAllData } = useDataStore()
  
  // Selected node state for detail panel
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null)
  const [selectedNodeType, setSelectedNodeType] = useState<'agent' | 'task' | 'context' | 'file' | 'admin' | null>(null)
  const [selectedNodeData, setSelectedNodeData] = useState<unknown>(null)
  const [isPanelOpen, setIsPanelOpen] = useState(false)
  
  useEffect(() => {
    // Fetch data on mount
    if (activeServerId && activeServer?.status === 'connected') {
      fetchAllData()
    }
  }, [activeServerId, activeServer?.status, fetchAllData])
  
  const isConnected = !!activeServerId && activeServer?.status === 'connected'

  // Show connection prompt if no server is selected
  if (!isConnected) {
    return (
      <div className="h-full flex items-center justify-center p-4">
        <Card className="max-w-md">
          <CardContent className="flex flex-col items-center justify-center py-12 px-8 text-center">
            <Server className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium text-foreground mb-2">Connect to an MCP Server</h3>
            <p className="text-muted-foreground text-sm">
              Select an MCP server from the project picker in the header to view the system graph and manage agents.
            </p>
            {activeServer && activeServer.status === 'error' && (
              <div className="text-sm text-destructive mt-4">
                Failed to connect to {activeServer.name} ({activeServer.host}:{activeServer.port})
                <div className="mt-4">
                  <CORSDiagnostic />
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    )
  }

  const handleClosePanel = () => {
    setIsPanelOpen(false)
    setSelectedNodeId(null)
    setSelectedNodeType(null)
    setSelectedNodeData(null)
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 h-full">
      <div className="lg:col-span-2 h-full">
        {/* Gráfico principal aqui */}
        <div className="bg-card/30 border border-border/50 rounded-lg h-full">
          <VisGraph 
            fullscreen 
            onNodeSelect={(nodeId, nodeType, nodeData) => {
              setSelectedNodeId(nodeId)
              setSelectedNodeType(nodeType)
              setSelectedNodeData(nodeData)
              setIsPanelOpen(true)
            }}
          />
        </div>
      </div>
      <div className="h-full">
        {/* Feed de atividade recente */}
        <RecentActivityFeed />
      </div>

      {/* Painel de detalhes do nó */}
      <NodeDetailPanel
        nodeId={selectedNodeId}
        nodeType={selectedNodeType}
        nodeData={selectedNodeData as unknown}
        isOpen={isPanelOpen}
        onClose={handleClosePanel}
      />
    </div>
  )
}