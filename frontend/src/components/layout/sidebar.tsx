import Link from "next/link"

import { SidebarNav } from "./sidebar-nav"

export function Sidebar() {
  return (
    <aside className="hidden w-64 shrink-0 border-r bg-background md:flex md:flex-col">
      <div className="flex h-16 items-center border-b px-6">
        <Link href="/" className="text-xl font-bold tracking-tight">
          HunarHire
        </Link>
      </div>

      <SidebarNav />

      <div className="border-t p-4">
        <p className="text-xs text-muted-foreground">AI Hiring Assistant</p>

        <p className="mt-1 text-sm font-medium">Powered by Hunar AI</p>
      </div>
    </aside>
  )
}
