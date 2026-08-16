import { DashboardShell } from "@/components/layout/dashboard-shell"
import { PeopleSearchPanel } from "@/components/search/people-search-panel"

const STEPS = [
  "Job description",
  "Find people",
  "Candidate profile",
  "Save phone",
  "Reach Out with Hunar AI",
]

export default function PeopleSearchPage() {
  return (
    <DashboardShell>
      <div className="mx-auto max-w-7xl space-y-8 p-6 lg:p-8">
        <div>
          <p className="text-sm font-medium text-muted-foreground">
            Assignment 2
          </p>

          <h1 className="mt-1 text-3xl font-bold tracking-tight">
            People Search & Reachout
          </h1>

          <p className="mt-2 max-w-3xl text-muted-foreground">
            Search public professional profiles from a job description, review
            education and experience when indexed, then reach out with Hunar AI
            using a recruiter-confirmed phone number.
          </p>
        </div>

        <ol className="flex flex-wrap gap-2 text-xs text-muted-foreground">
          {STEPS.map((step, index) => (
            <li
              key={step}
              className="rounded-full border bg-muted/40 px-3 py-1"
            >
              {index + 1}. {step}
            </li>
          ))}
        </ol>

        <PeopleSearchPanel />
      </div>
    </DashboardShell>
  )
}
