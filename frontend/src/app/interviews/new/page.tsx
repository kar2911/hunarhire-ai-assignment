import Link from "next/link"
import { ArrowLeft } from "lucide-react"

import { StartInterviewForm } from "@/components/interviews/start-interview-form"
import { DashboardShell } from "@/components/layout/dashboard-shell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function NewInterviewPage() {
  return (
    <DashboardShell>
      <div className="mx-auto max-w-4xl space-y-8 p-6 lg:p-8">
        <div className="space-y-4">
          <Link
            href="/interviews"
            className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Interviews
          </Link>

          <div>
            <p className="text-sm font-medium text-muted-foreground">
              New Screening
            </p>

            <h1 className="mt-1 text-3xl font-bold tracking-tight">
              Start Interview
            </h1>

            <p className="mt-2 text-muted-foreground">
              Configure and launch an AI-powered candidate screening call.
            </p>
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Interview Configuration</CardTitle>
          </CardHeader>

          <CardContent>
            <StartInterviewForm />
          </CardContent>
        </Card>
      </div>
    </DashboardShell>
  )
}
