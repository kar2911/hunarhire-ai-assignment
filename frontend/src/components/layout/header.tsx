"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Bell, Menu, Search, X } from "lucide-react"
import { useState } from "react"

import { navigation } from "@/components/layout/sidebar-nav"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

function isActive(pathname: string, href: string, exact?: boolean) {
  if (exact) {
    return pathname === href
  }

  return pathname === href || pathname.startsWith(`${href}/`)
}

export function Header() {
  const pathname = usePathname()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <>
      <header className="flex h-16 items-center justify-between border-b bg-background px-4 sm:px-6">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            aria-label={mobileMenuOpen ? "Close menu" : "Open menu"}
            onClick={() => setMobileMenuOpen((open) => !open)}
          >
            {mobileMenuOpen ? (
              <X className="h-4 w-4" />
            ) : (
              <Menu className="h-4 w-4" />
            )}
          </Button>

          <Link
            href="/"
            className="text-lg font-bold tracking-tight md:hidden"
          >
            HunarHire
          </Link>

          <div className="relative hidden md:block">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />

            <input
              type="text"
              placeholder="Search interviews..."
              className="h-9 w-72 rounded-md border bg-muted/30 pl-9 pr-3 text-sm outline-none transition focus:bg-background focus:ring-2 focus:ring-ring/50"
            />
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" aria-label="Notifications">
            <Bell className="h-4 w-4" />
          </Button>

          <Avatar className="h-8 w-8">
            <AvatarFallback>KJ</AvatarFallback>
          </Avatar>
        </div>
      </header>

      {mobileMenuOpen ? (
        <div className="border-b bg-background p-4 md:hidden">
          <nav className="space-y-1">
            {navigation.map((item) => {
              const Icon = item.icon
              const active = isActive(pathname, item.href, item.exact)

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
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
        </div>
      ) : null}
    </>
  )
}
