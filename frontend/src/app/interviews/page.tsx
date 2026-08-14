import Link from "next/link"

import { StatusBadge } from "@/components/interviews/status-badge"
import { DashboardShell } from "@/components/layout/dashboard-shell"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { getInterviewsEnriched } from "@/lib/api"
import {
  formatDate,
  getInterestClasses,
  getRecommendationClasses,
} from "@/lib/format"

export default async function InterviewsPage() {
  const interviews = await getInterviewsEnriched()

  return (
    <DashboardShell>
      <div className="mx-auto max-w-7xl space-y-8 p-6 lg:p-8">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">
              Recruitment
            </p>

            <h1 className="mt-1 text-3xl font-bold tracking-tight">
              Interviews
            </h1>

            <p className="mt-2 text-muted-foreground">
              Review AI-powered candidate screening interviews.
            </p>
          </div>

          <Link
            href="/interviews/new"
            className="inline-flex h-9 items-center justify-center rounded-md bg-foreground px-4 text-sm font-medium text-background transition-colors hover:bg-foreground/90"
          >
            Start Interview
          </Link>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>All Interviews</CardTitle>
          </CardHeader>

          <CardContent>
            {interviews.length === 0 ? (
              <div className="rounded-lg border border-dashed p-12 text-center">
                <p className="font-medium">No interviews found</p>

                <p className="mt-1 text-sm text-muted-foreground">
                  Start an AI screening interview to get started.
                </p>

                <Link
                  href="/interviews/new"
                  className="mt-4 inline-flex h-9 items-center justify-center rounded-md bg-foreground px-4 text-sm font-medium text-background transition-colors hover:bg-foreground/90"
                >
                  Start Interview
                </Link>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Candidate</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Score</TableHead>
                    <TableHead>Recommendation</TableHead>
                    <TableHead>Interest</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead className="text-right">Action</TableHead>
                  </TableRow>
                </TableHeader>

                <TableBody>
                  {interviews.map((interview) => (
                    <TableRow key={interview.id}>
                      <TableCell>
                        <div className="font-medium">
                          {interview.candidate_name}
                        </div>
                      </TableCell>

                      <TableCell>
                        <div>{interview.job_title}</div>

                        <div className="mt-1 text-xs text-muted-foreground">
                          #{interview.id}
                        </div>
                      </TableCell>

                      <TableCell>
                        <StatusBadge status={interview.status} />
                      </TableCell>

                      <TableCell>
                        {interview.overall_score !== null ? (
                          <span className="font-semibold">
                            {interview.overall_score}
                            <span className="font-normal text-muted-foreground">
                              /100
                            </span>
                          </span>
                        ) : (
                          <span className="text-muted-foreground">Pending</span>
                        )}
                      </TableCell>

                      <TableCell>
                        <Badge
                          className={getRecommendationClasses(
                            interview.recommendation,
                          )}
                        >
                          {interview.recommendation ?? "Pending"}
                        </Badge>
                      </TableCell>

                      <TableCell
                        className={`capitalize ${getInterestClasses(interview.interest_level)}`}
                      >
                        {interview.interest_level ?? "Pending"}
                      </TableCell>

                      <TableCell className="text-muted-foreground">
                        {formatDate(interview.created_at)}
                      </TableCell>

                      <TableCell className="text-right">
                        <Link
                          href={`/interviews/${interview.id}`}
                          className="inline-flex h-8 items-center justify-center rounded-md border bg-background px-3 text-xs font-medium transition-colors hover:bg-muted"
                        >
                          View
                        </Link>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardShell>
  )
}
