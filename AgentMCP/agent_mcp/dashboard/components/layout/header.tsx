"use client"

import React from "react"
import { Menu, KeyRound, LogOut } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ProjectPicker } from "@/components/server/project-picker"
import { useSidebar } from "@/lib/store"
import { useAuthStore } from "@/lib/stores/auth-store"
import { apiClient } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"

function AuthControl() {
  const { adminToken, setAdminToken, clearAdminToken } = useAuthStore()
  const { toast } = useToast()

  const handleLogin = async () => {
    try {
      const data = await apiClient.request<{ admin_token: string }>('/api/tokens')
      if (data.admin_token) {
        setAdminToken(data.admin_token)
        toast({
          title: "Autenticado",
          description: "Token de administrador carregado com sucesso.",
        })
      }
    } catch {
      toast({
        title: "Falha na Autenticação",
        description: "Não foi possível obter o token de administrador do servidor.",
        variant: "destructive",
      })
    }
  }

  if (adminToken) {
    return (
      <div className="flex items-center gap-2">
        <span className="text-xs text-muted-foreground font-mono">Admin: ...{adminToken.slice(-4)}</span>
        <Button variant="ghost" size="icon" onClick={clearAdminToken}>
          <LogOut className="h-4 w-4" />
        </Button>
      </div>
    )
  }

  return (
    <Button variant="outline" size="sm" onClick={handleLogin}>
      <KeyRound className="h-4 w-4 mr-2" />
      Admin Login
    </Button>
  )
}


export function Header() {
  const { toggleSidebar } = useSidebar()

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-16 items-center gap-4 px-[var(--space-fluid-lg)]">
        {/* Menu Toggle Button */}
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleSidebar}
          className="shrink-0 lg:hidden"
        >
          <Menu className="h-5 w-5" />
          <span className="sr-only">Toggle navigation menu</span>
        </Button>

        {/* Project Picker */}
        <div className="flex-1">
          <ProjectPicker />
        </div>
        
        <AuthControl />

        {/* Theme Toggle Removido */}
      </div>
    </header>
  )
}