import Link from "next/link"
import {
  ArrowLeft,
  Calendar,
  Clock,
  Phone,
  User,
} from "lucide-react"
import { notFound } from "next/navigation"

import { StatusBadge } from "@/components/interviews/status-badge"
import { DashboardShell } from "@/components/layout/dashboard-shell"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { getInterview } from "@/lib/api"
import {
  formatDate,
  formatDuration,
  getInterestClasses,
  getRecommendationClasses,
} from "@/lib/format"

type InterviewDetailPageProps = {
  params: Promise<{ id: string }>
}

const scoreLabels: Record<string, string> = {
  technical: "Technical",
  communication: "Communication",
  experience: "Experience",
  problem_solving: "Problem Solving",
  role_fit: "Role Fit",
}

export default async function InterviewDetailPage({
  params,
}: InterviewDetailPageProps) {
  const { id } = await params
  const interviewId = Number(id)

  if (Number.isNaN(interviewId)) {
    notFound()
  }

  let interview

  try {
    interview = await getInterview(interviewId)
  } catch {
    notFound()
  }

  const scoreEntries = Object.entries(interview.scores).filter(
    ([key]) => key !== "overall",
  )

  return (
    <DashboardShell>
      <div className="mx-auto max-w-7xl space-y-8 p-6 lg:p-8">
        <div className="space-y-4">
          <Link
            href="/interviews"
            className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Interviews
          </Link>

          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Interview Details
              </p>

              <h1 className="mt-1 text-3xl font-bold tracking-tight">
                {interview.candidate.name}
              </h1>

              <p className="mt-2 text-lg text-muted-foreground">
                {interview.job_title}
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <StatusBadge status={interview.status} />

              <Badge
                className={getRecommendationClasses(interview.recommendation)}
              >
                {interview.recommendation ?? "Pending"}
              </Badge>

              <span
                className={`rounded-full border px-3 py-1 text-sm capitalize ${getInterestClasses(interview.interest_level)}`}
              >
                {interview.interest_level
                  ? `${interview.interest_level} interest`
                  : "Interest pending"}
              </span>
            </div>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle>Candidate Information</CardTitle>
            </CardHeader>

            <CardContent className="space-y-4">
              <div className="flex items-start gap-3">
                <User className="mt-0.5 h-4 w-4 text-muted-foreground" />

                <div>
                  <p className="text-sm text-muted-foreground">Name</p>
                  <p className="font-medium">{interview.candidate.name}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Phone className="mt-0.5 h-4 w-4 text-muted-foreground" />

                <div>
                  <p className="text-sm text-muted-foreground">Mobile</p>
                  <p className="font-medium">
                    {interview.candidate.mobile_number}
                  </p>
                </div>
              </div>

              <Separator />

              <div className="flex items-start gap-3">
                <Calendar className="mt-0.5 h-4 w-4 text-muted-foreground" />

                <div>
                  <p className="text-sm text-muted-foreground">Interview Date</p>
                  <p className="font-medium">
                    {formatDate(interview.created_at)}
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Clock className="mt-0.5 h-4 w-4 text-muted-foreground" />

                <div>
                  <p className="text-sm text-muted-foreground">Duration</p>
                  <p className="font-medium">
                    {formatDuration(interview.duration_seconds)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Score Breakdown</CardTitle>
            </CardHeader>

            <CardContent className="space-y-6">
              <div className="rounded-lg border bg-muted/30 p-4">
                <div className="flex items-end justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">
                      Overall Score
                    </p>

                    <p className="text-4xl font-bold tracking-tight">
                      {interview.scores.overall ?? "—"}
                      {interview.scores.overall !== null ? (
                        <span className="ml-1 text-lg font-normal text-muted-foreground">
                          /100
                        </span>
                      ) : null}
                    </p>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                {scoreEntries.map(([key, value]) => (
                  <div key={key} className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium">
                        {scoreLabels[key] ?? key}
                      </span>

                      <span className="text-muted-foreground">
                        {value ?? "—"}
                        {value !== null ? "/100" : ""}
                      </span>
                    </div>

                    <div className="relative h-2 w-full overflow-hidden rounded-full bg-muted">
                      <div
                        className="h-full rounded-full bg-primary transition-all"
                        style={{ width: `${value ?? 0}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Summary</CardTitle>
            </CardHeader>

            <CardContent>
              <p className="whitespace-pre-wrap text-sm leading-relaxed text-muted-foreground">
                {interview.summary ?? "No summary available yet."}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Strengths</CardTitle>
            </CardHeader>

            <CardContent>
              <p className="whitespace-pre-wrap text-sm leading-relaxed text-muted-foreground">
                {interview.strengths ?? "No strengths recorded yet."}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Concerns</CardTitle>
            </CardHeader>

            <CardContent>
              <p className="whitespace-pre-wrap text-sm leading-relaxed text-muted-foreground">
                {interview.concerns ?? "No concerns recorded yet."}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Next Steps</CardTitle>
            </CardHeader>

            <CardContent>
              <p className="whitespace-pre-wrap text-sm leading-relaxed text-muted-foreground">
                {interview.next_steps ?? "No next steps recorded yet."}
              </p>
            </CardContent>
          </Card>
        </div>

        {interview.recording_url ? (
          <Card>
            <CardHeader>
              <CardTitle>Recording</CardTitle>
            </CardHeader>

            <CardContent>
              <audio
                controls
                className="w-full"
                src={interview.recording_url}
                preload="metadata"
              >
                Your browser does not support the audio element.
              </audio>
            </CardContent>
          </Card>
        ) : null}

        <Card>
          <CardHeader>
            <CardTitle>Transcript</CardTitle>
          </CardHeader>

          <CardContent>
            {interview.transcript ? (
              <div className="max-h-96 overflow-y-auto rounded-lg border bg-muted/20 p-4">
                <p className="whitespace-pre-wrap text-sm leading-relaxed">
                  {interview.transcript}
                </p>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                Transcript not available yet.
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardShell>
  )
}
