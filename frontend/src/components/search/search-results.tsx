import { PersonCard } from "@/components/search/person-card"
import type { SearchCriteria, NormalizedPerson } from "@/lib/people-api"
import { Badge } from "@/components/ui/badge"

type SearchResultsProps = {
  provider: string
  source?: string
  isMock: boolean
  isDemo?: boolean
  criteria: SearchCriteria
  results: NormalizedPerson[]
}

export function SearchResults({
  provider,
  source,
  isMock,
  isDemo,
  criteria,
  results,
}: SearchResultsProps) {
  const sourceLabel = isDemo
    ? "Demo Data"
    : isMock
      ? "Mock provider"
      : source || "Publicly indexed web data"

  return (
    <div className="space-y-6">
      {isDemo ? (
        <div className="rounded-lg border border-dashed bg-muted/30 px-4 py-3 text-sm text-muted-foreground">
          Showing <span className="font-medium text-foreground">Demo Data</span>.
          These records are for demonstration only and are not SerpApi results.
        </div>
      ) : isMock ? (
        <div className="rounded-lg border border-dashed bg-muted/30 px-4 py-3 text-sm text-muted-foreground">
          Showing mock profiles for local UI testing. These are not real people.
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">
          Candidate results · Source: {sourceLabel}
        </p>
      )}

      <div className="flex flex-wrap gap-2">
        {criteria.job_title ? (
          <Badge variant="outline">{criteria.job_title}</Badge>
        ) : null}

        {criteria.location ? (
          <Badge variant="outline">{criteria.location}</Badge>
        ) : null}

        {criteria.seniority ? (
          <Badge variant="outline">{criteria.seniority}</Badge>
        ) : null}

        {criteria.years_experience !== null ? (
          <Badge variant="outline">
            {criteria.years_experience}+ years
          </Badge>
        ) : null}

        {criteria.skills.map((skill) => (
          <Badge key={skill} variant="secondary">
            {skill}
          </Badge>
        ))}
      </div>

      {results.length === 0 ? (
        <div className="rounded-lg border border-dashed p-12 text-center">
          <p className="font-medium">
            {isDemo ? "No demo records loaded" : "No public profiles found"}
          </p>

          <p className="mt-1 text-sm text-muted-foreground">
            {isDemo
              ? "Add candidates to backend/app/services/people/demo_records.json. See demo_records.example.json for the schema."
              : "Try a more detailed job description. This search uses publicly indexed web data."}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {results.map((person) => (
            <PersonCard key={person.id} person={person} />
          ))}
        </div>
      )}

      {provider === "serpapi" ? (
        <p className="text-xs text-muted-foreground">
          Source: Publicly indexed web data. Missing fields stay “Not
          available”. Private contact details are not invented.
        </p>
      ) : null}
    </div>
  )
}
