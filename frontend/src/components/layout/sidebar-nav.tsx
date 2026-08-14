"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  BriefcaseBusiness,
  LayoutDashboard,
  Settings,
  Users,
  Video,
} from "lucide-react"

import { cn } from "@/lib/utils"

const navigation = [
  {
    label: "Dashboard",
    href: "/",
    icon: LayoutDashboard,
    exact: true,
  },
  {
    label: "Candidates",
    href: "/candidates",
    icon: Users,
  },
  {
    label: "Interviews",
    href: "/interviews",
    icon: Video,
  },
  {
    label: "Jobs",
    href: "/jobs",
    icon: BriefcaseBusiness,
  },
  {
    label: "Settings",
    href: "/settings",
    icon: Settings,
  },
]

function isActive(pathname: string, href: string, exact?: boolean) {
  if (exact) {
    return pathname === href
  }

  return pathname === href || pathname.startsWith(`${href}/`)
}

export function SidebarNav() {
  const pathname = usePathname()

  return (
    <nav className="flex-1 space-y-1 p-4">
      {navigation.map((item) => {
        const Icon = item.icon
        const active = isActive(pathname, item.href, item.exact)

        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
              active
                ? "bg-foreground text-background"
                : "text-muted-foreground hover:bg-muted hover:text-foreground",
            )}
          >
            <Icon className="h-4 w-4 shrink-0" />
            <span>{item.label}</span>
          </Link>
        )
      })}
    </nav>
  )
}

export { navigation }
