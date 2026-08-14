import type { ReactNode } from "react"

import { Header } from "./header"
import { Sidebar } from "./sidebar"

type DashboardShellProps = {
  children: ReactNode
}

export function DashboardShell({ children }: DashboardShellProps) {
  return (
    <div className="min-h-screen bg-muted/30">
      <div className="flex min-h-screen">
        <Sidebar />

        <div className="flex min-w-0 flex-1 flex-col">
          <Header />

          <main className="flex-1">{children}</main>
        </div>
      </div>
    </div>
  )
}
