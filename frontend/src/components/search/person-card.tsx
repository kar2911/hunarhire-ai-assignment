import Link from "next/link"
import { ExternalLink, MapPin } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import type { NormalizedPerson } from "@/lib/people-api"

type PersonCardProps = {
  person: NormalizedPerson
}

function displayValue(value: string | null) {
  return value?.trim() ? value : "Not available"
}

function sourceLabel(provider: string) {
  if (provider === "demo") {
    return "Demo Data"
  }

  if (provider === "mock") {
    return "Mock provider"
  }

  return "Publicly indexed web data"
}

export function PersonCard({ person }: PersonCardProps) {
  const profileHref = `/search/${encodeURIComponent(person.id)}`

  return (
    <Card>
      <CardContent className="space-y-4 p-5">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h3 className="text-lg font-semibold tracking-tight">
              {displayValue(person.full_name)}
            </h3>

            <p className="mt-1 text-sm text-muted-foreground">
              {displayValue(person.job_title)}
              {person.company_name ? ` · ${person.company_name}` : ""}
            </p>

            <p className="mt-2 flex items-center gap-1.5 text-sm text-muted-foreground">
              <MapPin className="h-3.5 w-3.5" />
              {displayValue(person.location)}
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <Link
              href={profileHref}
              className="inline-flex h-8 items-center justify-center rounded-md border bg-background px-3 text-xs font-medium transition-colors hover:bg-muted"
            >
              View Profile
            </Link>

            <Link
              href={profileHref}
              className="inline-flex h-8 items-center justify-center rounded-md bg-foreground px-3 text-xs font-medium text-background transition-colors hover:bg-foreground/90"
            >
              Reach Out
            </Link>
          </div>
        </div>

        {person.headline ? (
          <p className="text-sm leading-relaxed text-muted-foreground">
            {person.headline}
          </p>
        ) : null}

        {person.skills.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {person.skills.slice(0, 8).map((skill) => (
              <Badge key={skill} variant="secondary">
                {skill}
              </Badge>
            ))}
          </div>
        ) : null}

        {person.linkedin_url ? (
          <a
            href={person.linkedin_url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 text-sm font-medium hover:underline"
          >
            <ExternalLink className="h-3.5 w-3.5" />
            LinkedIn
          </a>
        ) : null}

        <p className="text-xs text-muted-foreground">
          Source: {sourceLabel(person.provider)}
        </p>
      </CardContent>
    </Card>
  )
}
