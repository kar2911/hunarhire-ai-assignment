import { DashboardShell } from "@/components/layout/dashboard-shell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"

export default function SettingsPage() {
  return (
    <DashboardShell>
      <div className="mx-auto max-w-3xl space-y-8 p-6 lg:p-8">
        <div>
          <p className="text-sm font-medium text-muted-foreground">
            Configuration
          </p>

          <h1 className="mt-1 text-3xl font-bold tracking-tight">Settings</h1>

          <p className="mt-2 text-muted-foreground">
            Manage your HunarHire workspace preferences.
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Workspace</CardTitle>
          </CardHeader>

          <CardContent className="space-y-6">
            <div>
              <p className="text-sm font-medium">Organization</p>
              <p className="mt-1 text-sm text-muted-foreground">HunarHire</p>
            </div>

            <Separator />

            <div>
              <p className="text-sm font-medium">AI Provider</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Powered by Hunar AI for automated candidate screening.
              </p>
            </div>

            <Separator />

            <div>
              <p className="text-sm font-medium">API Connection</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Frontend connects to the FastAPI backend via{" "}
                <code className="rounded bg-muted px-1.5 py-0.5 text-xs">
                  NEXT_PUBLIC_API_URL
                </code>
                .
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardShell>
  )
}
