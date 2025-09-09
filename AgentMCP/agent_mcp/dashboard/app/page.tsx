"use client"

import { MainLayout } from "@/components/layout/main-layout"
import { DashboardWrapper } from "@/components/dashboard/dashboard-wrapper"
import { DashboardViewManager } from "@/components/dashboard/dashboard-view-manager"

export default function HomePage() {
  return (
    <MainLayout>
      <DashboardWrapper>
        <DashboardViewManager />
      </DashboardWrapper>
    </MainLayout>
  )
}
