import Link from "next/link"
import {
  CheckCircle2,
  Star,
  TrendingUp,
  Video,
} from "lucide-react"

import { StatCard } from "@/components/dashboard/stat-card"
import { StatusBadge } from "@/components/interviews/status-badge"
import { DashboardShell } from "@/components/layout/dashboard-shell"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { getInterviewsEnriched } from "@/lib/api"
import { formatDate, getRecommendationClasses } from "@/lib/format"

export default async function Home() {
  const interviews = await getInterviewsEnriched()

  const completed = interviews.filter(
    (interview) => interview.status === "COMPLETED",
  )

  const recommended = interviews.filter(
    (interview) => interview.recommendation?.toLowerCase() === "hire",
  )

  const scores = completed
    .map((interview) => interview.overall_score)
    .filter((score): score is number => typeof score === "number")

  const averageScore =
    scores.length > 0
      ? Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length)
      : 0

  const recentInterviews = interviews.slice(0, 5)

  return (
    <DashboardShell>
      <div className="mx-auto max-w-7xl space-y-8 p-6 lg:p-8">
        <div>
          <p className="text-sm font-medium text-muted-foreground">Overview</p>

          <h1 className="mt-1 text-3xl font-bold tracking-tight">
            Hiring Dashboard
          </h1>

          <p className="mt-2 text-muted-foreground">
            Monitor AI-powered candidate screening and interview results.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard
            title="Total Interviews"
            value={interviews.length}
            icon={Video}
          />

          <StatCard
            title="Completed Interviews"
            value={completed.length}
            icon={CheckCircle2}
          />

          <StatCard
            title="Recommended Candidates"
            value={recommended.length}
            icon={Star}
          />

          <StatCard
            title="Average Score"
            value={scores.length > 0 ? `${averageScore}/100` : "—"}
            subtitle={
              scores.length > 0
                ? `Based on ${scores.length} completed interviews`
                : "No completed scores yet"
            }
            icon={TrendingUp}
          />
        </div>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Recent Interviews</CardTitle>

              <p className="mt-1 text-sm text-muted-foreground">
                Latest AI screening activity.
              </p>
            </div>

            <Link
              href="/interviews"
              className="text-sm font-medium hover:underline"
            >
              View all
            </Link>
          </CardHeader>

          <CardContent>
            {recentInterviews.length === 0 ? (
              <div className="rounded-lg border border-dashed p-10 text-center">
                <p className="font-medium">No interviews yet</p>

                <p className="mt-1 text-sm text-muted-foreground">
                  Start an AI screening interview to see candidates here.
                </p>

                <Link
                  href="/interviews/new"
                  className="mt-4 inline-flex h-9 items-center justify-center rounded-md bg-foreground px-4 text-sm font-medium text-background transition-colors hover:bg-foreground/90"
                >
                  Start Interview
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                {recentInterviews.map((interview) => (
                  <Link
                    key={interview.id}
                    href={`/interviews/${interview.id}`}
                    className="block rounded-lg border p-4 transition-colors hover:bg-muted/50"
                  >
                    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                      <div>
                        <div className="font-semibold">
                          {interview.candidate_name}
                        </div>

                        <div className="mt-1 text-sm text-muted-foreground">
                          {interview.job_title} · {formatDate(interview.created_at)}
                        </div>
                      </div>

                      <div className="flex flex-wrap items-center gap-2">
                        <StatusBadge status={interview.status} />

                        <Badge
                          className={getRecommendationClasses(
                            interview.recommendation,
                          )}
                        >
                          {interview.recommendation ?? "Pending"}
                        </Badge>

                        {interview.overall_score !== null ? (
                          <span className="font-semibold">
                            {interview.overall_score}/100
                          </span>
                        ) : null}
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardShell>
  )
}
