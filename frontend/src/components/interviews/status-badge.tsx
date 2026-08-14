import { Badge } from "@/components/ui/badge"
import { formatStatus, getStatusClasses } from "@/lib/format"

type StatusBadgeProps = {
  status: string
}

export function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <Badge className={getStatusClasses(status)}>{formatStatus(status)}</Badge>
  )
}
