import Link from "next/link"
import {
  ArrowLeft,
  Building2,
  ExternalLink,
  Mail,
  Phone,
} from "lucide-react"
import { notFound } from "next/navigation"

import { DashboardShell } from "@/components/layout/dashboard-shell"
import { ReachOutPanel } from "@/components/search/reach-out-panel"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { getPerson } from "@/lib/people-api"

type PersonProfilePageProps = {
  params: Promise<{ id: string }>
}

function displayValue(value: string | null | undefined) {
  return value?.trim() ? value : "Not available"
}

function formatPublicPhone(value: string) {
  const digits = value.replace(/\D/g, "")

  if (value.startsWith("+91") && digits.length === 12) {
    const national = digits.slice(2)
    return `+91 ${national.slice(0, 5)} ${national.slice(5)}`
  }

  return value
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

export default async function PersonProfilePage({
  params,
}: PersonProfilePageProps) {
  const { id } = await params
  const personId = decodeURIComponent(id)

  let person

  try {
    person = await getPerson(personId)
  } catch {
    notFound()
  }

  const isDemo = person.provider === "demo"

  return (
    <DashboardShell>
      <div className="mx-auto max-w-5xl space-y-8 p-6 lg:p-8">
        <div className="space-y-4">
          <Link
            href="/search"
            className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to People Search
          </Link>

          <div>
            <p className="text-sm font-medium text-muted-foreground">
              Candidate Profile
            </p>

            <h1 className="mt-1 text-3xl font-bold tracking-tight">
              {displayValue(person.full_name)}
            </h1>

            <p className="mt-2 text-lg text-muted-foreground">
              {displayValue(person.job_title)}
              {person.company_name ? ` · ${person.company_name}` : ""}
            </p>

            <p className="mt-2 text-sm text-muted-foreground">
              {displayValue(person.location)}
            </p>
          </div>

          <p className="text-sm text-muted-foreground">
            Source: {sourceLabel(person.provider)}
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Profile</CardTitle>
          </CardHeader>

          <CardContent className="space-y-4">
            <dl className="grid gap-3 text-sm sm:grid-cols-2">
              <div>
                <dt className="text-muted-foreground">Current role</dt>
                <dd className="font-medium">{displayValue(person.job_title)}</dd>
              </div>
              <div>
                <dt className="text-muted-foreground">Company</dt>
                <dd className="font-medium">
                  {displayValue(person.company_name)}
                </dd>
              </div>
              <div>
                <dt className="text-muted-foreground">Location</dt>
                <dd className="font-medium">{displayValue(person.location)}</dd>
              </div>
              <div>
                <dt className="text-muted-foreground">LinkedIn</dt>
                <dd className="font-medium">
                  {person.linkedin_url ? (
                    <a
                      href={person.linkedin_url}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1.5 hover:underline"
                    >
                      <ExternalLink className="h-3.5 w-3.5" />
                      Open profile
                    </a>
                  ) : (
                    "Not available"
                  )}
                </dd>
              </div>
            </dl>

            <Separator />

            <div>
              <p className="text-sm text-muted-foreground">Summary</p>
              <p className="mt-1 whitespace-pre-wrap text-sm leading-relaxed">
                {displayValue(person.summary || person.headline)}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Skills</CardTitle>
          </CardHeader>

          <CardContent>
            {person.skills.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {person.skills.map((skill) => (
                  <Badge key={skill} variant="secondary">
                    {skill}
                  </Badge>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">Not available</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Experience</CardTitle>
          </CardHeader>

          <CardContent className="space-y-4">
            {person.experience.length === 0 ? (
              <p className="text-sm text-muted-foreground">Not available</p>
            ) : (
              person.experience.map((item, index) => (
                <div key={`${item.company}-${index}`} className="space-y-1">
                  <p className="font-medium">{displayValue(item.title)}</p>
                  <p className="text-sm text-muted-foreground">
                    {item.company ? item.company : "Not available"}
                    {item.location ? ` · ${item.location}` : ""}
                    {item.start_date || item.end_date
                      ? ` · ${[item.start_date, item.end_date]
                          .filter(Boolean)
                          .join(" – ")}`
                      : ""}
                  </p>
                  {item.description ? (
                    <p className="text-sm text-muted-foreground">
                      {item.description}
                    </p>
                  ) : null}
                </div>
              ))
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Education</CardTitle>
          </CardHeader>

          <CardContent className="space-y-4">
            {person.education.length === 0 ? (
              <p className="text-sm text-muted-foreground">Not available</p>
            ) : (
              person.education.map((item, index) => (
                <div key={`${item.school}-${index}`} className="space-y-1">
                  <p className="font-medium">{displayValue(item.school)}</p>
                  <p className="text-sm text-muted-foreground">
                    {[item.degree, item.field].filter(Boolean).join(" · ") ||
                      "Not available"}
                    {item.start_date || item.end_date
                      ? ` · ${[item.start_date, item.end_date]
                          .filter(Boolean)
                          .join(" – ")}`
                      : ""}
                  </p>
                </div>
              ))
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Contact</CardTitle>
          </CardHeader>

          <CardContent className="space-y-4">
            <div className="flex items-start gap-3">
              <Mail className="mt-0.5 h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Email</p>
                <p className="font-medium">{displayValue(person.email)}</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <Phone className="mt-0.5 h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Phone</p>
                <p className="font-medium">
                  {isDemo && person.phone
                    ? formatPublicPhone(person.phone)
                    : person.public_phone
                      ? formatPublicPhone(person.public_phone)
                      : "Not available"}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
                  {isDemo && person.phone
                    ? "Source: Demo Data"
                    : person.public_phone
                      ? "Source: Public Web"
                      : "Not available"}
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <Building2 className="mt-0.5 h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">
                  Recruiter-provided phone
                </p>
                <p className="font-medium">
                  {person.phone_source === "recruiter_provided"
                    ? displayValue(person.phone)
                    : "Save a number below before outreach."}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <ReachOutPanel
          personId={person.id}
          publicPhone={person.public_phone}
          demoPhone={
            person.phone_source === "demo_data" ? person.phone : null
          }
          recruiterPhone={
            person.phone_source === "recruiter_provided" ? person.phone : null
          }
        />
      </div>
    </DashboardShell>
  )
}
