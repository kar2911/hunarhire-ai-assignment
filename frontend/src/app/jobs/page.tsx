import Link from "next/link"

import { DashboardShell } from "@/components/layout/dashboard-shell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { getJobSummaries } from "@/lib/api"

export default async function JobsPage() {
  const jobs = await getJobSummaries()

  return (
    <DashboardShell>
      <div className="mx-auto max-w-7xl space-y-8 p-6 lg:p-8">
        <div>
          <p className="text-sm font-medium text-muted-foreground">
            Open Roles
          </p>

          <h1 className="mt-1 text-3xl font-bold tracking-tight">Jobs</h1>

          <p className="mt-2 text-muted-foreground">
            Roles tracked from your AI screening interviews.
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Active Roles</CardTitle>
          </CardHeader>

          <CardContent>
            {jobs.length === 0 ? (
              <div className="rounded-lg border border-dashed p-12 text-center">
                <p className="font-medium">No jobs yet</p>

                <p className="mt-1 text-sm text-muted-foreground">
                  Job roles will appear here once you start screening
                  interviews.
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
                    <TableHead>Job Title</TableHead>
                    <TableHead>Interviews</TableHead>
                    <TableHead>Completed</TableHead>
                    <TableHead>Avg Score</TableHead>
                  </TableRow>
                </TableHeader>

                <TableBody>
                  {jobs.map((job) => (
                    <TableRow key={job.title}>
                      <TableCell className="font-medium">{job.title}</TableCell>

                      <TableCell>{job.interview_count}</TableCell>

                      <TableCell>{job.completed_count}</TableCell>

                      <TableCell>
                        {job.average_score !== null ? (
                          <span className="font-semibold">
                            {job.average_score}
                            <span className="font-normal text-muted-foreground">
                              /100
                            </span>
                          </span>
                        ) : (
                          <span className="text-muted-foreground">Pending</span>
                        )}
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
