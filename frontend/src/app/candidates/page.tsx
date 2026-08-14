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
import { getCandidateSummaries } from "@/lib/api"
import {
  getRecommendationClasses,
} from "@/lib/format"

export default async function CandidatesPage() {
  const candidates = await getCandidateSummaries()

  return (
    <DashboardShell>
      <div className="mx-auto max-w-7xl space-y-8 p-6 lg:p-8">
        <div>
          <p className="text-sm font-medium text-muted-foreground">Talent Pool</p>

          <h1 className="mt-1 text-3xl font-bold tracking-tight">Candidates</h1>

          <p className="mt-2 text-muted-foreground">
            Candidates derived from your AI screening interviews.
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>All Candidates</CardTitle>
          </CardHeader>

          <CardContent>
            {candidates.length === 0 ? (
              <div className="rounded-lg border border-dashed p-12 text-center">
                <p className="font-medium">No candidates yet</p>

                <p className="mt-1 text-sm text-muted-foreground">
                  Start an interview to add candidates to your talent pool.
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
                    <TableHead>Mobile</TableHead>
                    <TableHead>Interviews</TableHead>
                    <TableHead>Latest Role</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Avg Score</TableHead>
                    <TableHead>Recommendation</TableHead>
                    <TableHead className="text-right">Action</TableHead>
                  </TableRow>
                </TableHeader>

                <TableBody>
                  {candidates.map((candidate) => (
                    <TableRow key={candidate.id}>
                      <TableCell>
                        <div className="font-medium">{candidate.name}</div>
                      </TableCell>

                      <TableCell className="text-muted-foreground">
                        {candidate.mobile_number}
                      </TableCell>

                      <TableCell>{candidate.interview_count}</TableCell>

                      <TableCell>{candidate.latest_job_title}</TableCell>

                      <TableCell>
                        <StatusBadge status={candidate.latest_status} />
                      </TableCell>

                      <TableCell>
                        {candidate.average_score !== null ? (
                          <span className="font-semibold">
                            {candidate.average_score}
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
                            candidate.latest_recommendation,
                          )}
                        >
                          {candidate.latest_recommendation ?? "Pending"}
                        </Badge>
                      </TableCell>

                      <TableCell className="text-right">
                        <Link
                          href={`/interviews/${candidate.latest_interview_id}`}
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
