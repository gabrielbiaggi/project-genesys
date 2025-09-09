"use client"

import React from 'react'
import { cn } from '@/lib/utils'
import { useSidebar } from '@/lib/store'
import { Navigation } from './navigation'

export function AppSidebar() {
  const { isCollapsed } = useSidebar()

  return (
    <aside
      className={cn(
        "hidden lg:flex flex-col border-r bg-background transition-all duration-300 ease-in-out",
        isCollapsed ? "w-20" : "w-64"
      )}
    >
      <div className="flex h-16 items-center justify-center border-b">
        {/* Pode adicionar um logo aqui */}
        <h1 className={cn("font-bold text-lg", isCollapsed && "hidden")}>Genesys</h1>
        <div className={cn("p-2", !isCollapsed && "hidden")}>
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-6 w-6"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
        </div>
      </div>
      <div className="flex-1 overflow-y-auto">
        <Navigation />
      </div>
    </aside>
  )
}
