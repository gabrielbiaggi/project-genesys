"use client"

import React, { useState, useEffect } from 'react'
import { X, Clock, User, Hash, AlertCircle, CheckCircle2, Activity, MessageSquare, GitBranch, Target, Zap, ChevronRight, Edit, Save } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { cn } from '@/lib/utils'
import { apiClient, Task } from '@/lib/api'
import { useDataStore } from '@/lib/stores/data-store'
import { useAuthStore } from '@/lib/stores/auth-store'
import { useToast } from '@/hooks/use-toast'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Label } from '@/components/ui/label'

interface TaskDetailsPanelProps {
  task: Task | null
  onClose: () => void
}

export function TaskDetailsPanel({ task, onClose }: TaskDetailsPanelProps) {
  const { data, refreshData } = useDataStore()
  const { adminToken } = useAuthStore()
  const { toast } = useToast()
  
  const [activeTab, setActiveTab] = useState<'details' | 'history'>('details')
  const [isEditing, setIsEditing] = useState(false)
  const [editableTask, setEditableTask] = useState<Partial<Task>>({})

  useEffect(() => {
    if (task) {
      setEditableTask({
        title: task.title,
        description: task.description,
        status: task.status,
        priority: task.priority,
        assigned_to: task.assigned_to,
      })
      setIsEditing(false) // Reset edit mode when task changes
    }
  }, [task])
  
  const handleUpdate = async () => {
    if (!task || !adminToken) {
      toast({
        title: "Erro de Autenticação",
        description: "Você precisa estar logado como administrador para atualizar tarefas.",
        variant: "destructive"
      })
      return
    }

    try {
      const payload: Partial<Task> & { token: string } = {
        ...editableTask,
        token: adminToken,
      }
      
      await apiClient.updateTask(task.task_id, payload)
      
      toast({
        title: "Tarefa Atualizada",
        description: "As alterações na tarefa foram salvas com sucesso."
      })
      
      setIsEditing(false)
      refreshData() // Refresh all data to get the latest task state
    } catch (error) {
      toast({
        title: "Erro ao Atualizar",
        description: error instanceof Error ? error.message : "Não foi possível salvar as alterações.",
        variant: "destructive"
      })
    }
  }

  // Get task history and related actions
  const taskHistory = task ? (data?.actions || []).filter(action => 
    'task_id' in action && action.task_id === task.task_id
  ).sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()) : []

  // Get agent info if task is assigned
  const assignedAgent = task?.assigned_to ? data?.agents.find(a => a.agent_id === task.assigned_to) : null

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    
    if (diff < 60000) return 'Just now'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`
    return date.toLocaleDateString()
  }

  const getStatusColor = (status: Task['status']) => {
    const colors = {
      pending: 'bg-amber-500/15 text-amber-600 border-amber-500/30',
      in_progress: 'bg-blue-500/15 text-blue-600 border-blue-500/30',
      completed: 'bg-green-500/15 text-green-600 border-green-500/30',
      cancelled: 'bg-gray-500/15 text-gray-600 border-gray-500/30',
      failed: 'bg-red-500/15 text-red-600 border-red-500/30'
    }
    return colors[status] || colors.pending
  }

  const getPriorityColor = (priority: Task['priority']) => {
    const colors = {
      low: 'bg-slate-500/15 text-slate-600 border-slate-500/30',
      medium: 'bg-amber-500/15 text-amber-600 border-amber-500/30',
      high: 'bg-red-500/15 text-red-600 border-red-500/30'
    }
    return colors[priority] || colors.medium
  }

  const getActionIcon = (actionType: string) => {
    if (actionType.includes('create')) return <Target className="h-3.5 w-3.5 text-blue-500" />
    if (actionType.includes('start') || actionType.includes('begin')) return <Activity className="h-3.5 w-3.5 text-green-500" />
    if (actionType.includes('complete') || actionType.includes('finish')) return <CheckCircle2 className="h-3.5 w-3.5 text-green-500" />
    if (actionType.includes('fail') || actionType.includes('error')) return <AlertCircle className="h-3.5 w-3.5 text-red-500" />
    if (actionType.includes('update') || actionType.includes('modify')) return <Zap className="h-3.5 w-3.5 text-amber-500" />
    return <ChevronRight className="h-3.5 w-3.5 text-gray-500" />
  }

  // Parse JSON fields safely
  const parseJsonField = (field: unknown): unknown[] => {
    if (Array.isArray(field)) return field
    if (typeof field === 'string') {
      try {
        return JSON.parse(field)
      } catch {
        return []
      }
    }
    return []
  }

  const dependencies = task ? parseJsonField(task.depends_on_tasks) : []
  const childTasks = task ? parseJsonField(task.child_tasks) : []
  const notes = task ? parseJsonField(task.notes) : []

  return (
    <div className={cn(
      "fixed right-0 top-0 h-screen bg-background border-l transform transition-all duration-500 z-30",
      "shadow-lg",
      task ? "translate-x-0 w-[420px]" : "translate-x-full w-0"
    )}>
      {task && (
        <div className="h-full flex flex-col">
          {/* Header */}
          <div className="bg-card border-b px-4 py-3">
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <h2 className="text-base font-semibold truncate">{task.title}</h2>
                <div className="flex items-center gap-2 mt-1">
                  <Badge variant="outline" className={cn("text-xs", getStatusColor(task.status))}>
                    {task.status.replace('_', ' ')}
                  </Badge>
                  <Badge variant="outline" className={cn("text-xs", getPriorityColor(task.priority))}>
                    {task.priority}
                  </Badge>
                </div>
              </div>
              <div className="flex items-center">
                {isEditing ? (
                  <>
                    <Button variant="ghost" size="sm" onClick={() => setIsEditing(false)}>Cancel</Button>
                    <Button size="sm" onClick={handleUpdate} className="ml-2"><Save className="h-3.5 w-3.5 mr-1.5"/> Save</Button>
                  </>
                ) : (
                  <Button variant="outline" size="sm" onClick={() => setIsEditing(true)}><Edit className="h-3.5 w-3.5 mr-1.5"/> Edit</Button>
                )}
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={onClose}
                  className="h-7 w-7 flex-shrink-0 ml-2"
                >
                  <X className="h-3.5 w-3.5" />
                </Button>
              </div>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="flex border-b bg-muted/30">
            <button
              onClick={() => setActiveTab('details')}
              className={cn(
                "flex-1 px-4 py-2 text-sm font-medium transition-colors",
                activeTab === 'details' 
                  ? "text-foreground border-b-2 border-primary bg-background" 
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              Details
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={cn(
                "flex-1 px-4 py-2 text-sm font-medium transition-colors",
                activeTab === 'history' 
                  ? "text-foreground border-b-2 border-primary bg-background" 
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              History ({taskHistory.length})
            </button>
          </div>

          <ScrollArea className="flex-1">
            <div className="px-4 py-4 space-y-4">
              
              {activeTab === 'details' && (
                <div className="space-y-4">
                  {/* Basic Info */}
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <Label className="text-xs uppercase tracking-wider text-muted-foreground">Task ID</Label>
                      <p className="font-mono text-xs mt-1 break-all">{task.task_id}</p>
                    </div>
                    <div>
                      <Label className="text-xs uppercase tracking-wider text-muted-foreground">Status</Label>
                      {isEditing ? (
                        <Select
                          value={editableTask.status}
                          onValueChange={(value: Task['status']) => setEditableTask(prev => ({ ...prev, status: value }))}
                        >
                          <SelectTrigger className="mt-1 h-8 text-xs"><SelectValue /></SelectTrigger>
                          <SelectContent>
                            <SelectItem value="pending">Pending</SelectItem>
                            <SelectItem value="in_progress">In Progress</SelectItem>
                            <SelectItem value="completed">Completed</SelectItem>
                            <SelectItem value="cancelled">Cancelled</SelectItem>
                            <SelectItem value="failed">Failed</SelectItem>
                          </SelectContent>
                        </Select>
                      ) : (
                        <p className="text-sm mt-1 capitalize">{task.status.replace('_', ' ')}</p>
                      )}
                    </div>
                    <div>
                      <Label className="text-xs uppercase tracking-wider text-muted-foreground">Priority</Label>
                      {isEditing ? (
                        <Select
                          value={editableTask.priority}
                          onValueChange={(value: Task['priority']) => setEditableTask(prev => ({ ...prev, priority: value }))}
                        >
                          <SelectTrigger className="mt-1 h-8 text-xs"><SelectValue /></SelectTrigger>
                          <SelectContent>
                            <SelectItem value="low">Low</SelectItem>
                            <SelectItem value="medium">Medium</SelectItem>
                            <SelectItem value="high">High</SelectItem>
                          </SelectContent>
                        </Select>
                      ) : (
                        <p className="text-sm mt-1 capitalize">{task.priority}</p>
                      )}
                    </div>
                    <div>
                      <Label className="text-xs uppercase tracking-wider text-muted-foreground">Created</Label>
                      <p className="text-sm mt-1">{new Date(task.created_at).toLocaleDateString()}</p>
                    </div>
                  </div>

                  {/* Assigned Agent */}
                  <div>
                    <Label className="text-xs uppercase tracking-wider text-muted-foreground">Assigned Agent</Label>
                    {isEditing ? (
                       <Input 
                         value={editableTask.assigned_to || ''}
                         onChange={(e) => setEditableTask(prev => ({ ...prev, assigned_to: e.target.value }))}
                         placeholder="agent-id"
                         className="mt-1 h-8 text-xs"
                       />
                    ) : (
                      assignedAgent ? (
                        <div className="bg-muted rounded-lg p-3 mt-2">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <User className="h-4 w-4 text-muted-foreground" />
                              <span className="font-medium">{assignedAgent.agent_id}</span>
                            </div>
                            <Badge variant="outline" className="text-xs">
                              {assignedAgent.status}
                            </Badge>
                          </div>
                        </div>
                      ) : <p className="text-sm mt-1 text-muted-foreground">Unassigned</p>
                    )}
                  </div>

                  {/* Description */}
                  <div>
                    <Label className="text-xs uppercase tracking-wider text-muted-foreground">Description</Label>
                    {isEditing ? (
                      <Textarea 
                        value={editableTask.description || ''}
                        onChange={(e) => setEditableTask(prev => ({ ...prev, description: e.target.value }))}
                        className="mt-1 text-sm h-24"
                      />
                    ) : (
                      <p className="text-sm mt-2 whitespace-pre-wrap">{task.description || "N/A"}</p>
                    )}
                  </div>

                  {/* Dependencies */}
                  {dependencies.length > 0 && (
                    <div>
                      <Label className="text-xs uppercase tracking-wider text-muted-foreground">Dependencies</Label>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {dependencies.map((depId: unknown, index) => (
                          <Badge key={index} variant="outline" className="text-xs font-mono">
                            <GitBranch className="h-3 w-3 mr-1" />
                            {String(depId)}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Child Tasks */}
                  {childTasks.length > 0 && (
                    <div>
                      <Label className="text-xs uppercase tracking-wider text-muted-foreground">Subtasks</Label>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {childTasks.map((childId: unknown, index) => (
                          <Badge key={index} variant="outline" className="text-xs font-mono">
                            <Hash className="h-3 w-3 mr-1" />
                            {String(childId)}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Notes */}
                  {notes.length > 0 && (
                    <div>
                      <Label className="text-xs uppercase tracking-wider text-muted-foreground">Notes</Label>
                      <div className="space-y-2 mt-2">
                        {notes.map((note: unknown, index) => {
                          const noteObj = note as { author: string; timestamp: string; content: string };
                          return (
                            <div key={index} className="bg-muted/50 rounded-lg p-3">
                              <div className="flex items-center justify-between mb-2">
                                <span className="text-xs font-medium">{noteObj.author}</span>
                                <span className="text-xs text-muted-foreground">
                                  {new Date(noteObj.timestamp).toLocaleString()}
                                </span>
                              </div>
                              <p className="text-sm">{noteObj.content}</p>
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  )}

                  {/* Timestamps */}
                  <div className="pt-4 border-t space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Last Updated</span>
                      <span className="font-mono text-xs">{new Date(task.updated_at).toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'history' && (
                <div className="space-y-3">
                  {taskHistory.length > 0 ? (
                    taskHistory.map((action, index) => (
                      <div key={index} className="flex items-start gap-3 p-3 rounded-lg hover:bg-muted/30 transition-colors">
                        <div className="flex-shrink-0 mt-0.5">
                          {getActionIcon('action_type' in action ? action.action_type as string : '')}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <p className="font-medium text-sm capitalize">
                              {'action_type' in action ? (action.action_type as string).replace(/_/g, ' ') : ''}
                            </p>
                            <span className="text-xs text-muted-foreground flex-shrink-0">
                              {formatTimestamp(action.timestamp)}
                            </span>
                          </div>
                          {'agent_id' in action && (
                            <p className="text-xs text-muted-foreground mt-1">
                              Agent: {action.agent_id as string}
                            </p>
                          )}
                           {'details' in action && typeof action.details === 'string' && (
                            <p className="text-xs text-muted-foreground mt-1 break-words">
                              {action.details}
                            </p>
                          )}
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8">
                      <Clock className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                      <p className="text-sm text-muted-foreground">No history available</p>
                    </div>
                  )}
                </div>
              )}

            </div>
          </ScrollArea>
        </div>
      )}
    </div>
  )
}