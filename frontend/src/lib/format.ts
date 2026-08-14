export function formatStatus(status: string) {
  return status.replaceAll("_", " ")
}

export function formatDate(dateString: string) {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(dateString))
}

export function formatDuration(seconds: number | null) {
  if (seconds === null) {
    return "—"
  }

  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60

  if (minutes === 0) {
    return `${remainingSeconds}s`
  }

  return `${minutes}m ${remainingSeconds}s`
}

export function getStatusClasses(status: string) {
  switch (status) {
    case "COMPLETED":
      return "bg-foreground text-background"

    case "IN_PROGRESS":
      return "bg-secondary text-secondary-foreground"

    case "FAILED":
      return "bg-destructive text-white"

    default:
      return "bg-secondary text-secondary-foreground"
  }
}

export function getRecommendationClasses(recommendation: string | null) {
  if (!recommendation) {
    return "bg-secondary text-secondary-foreground"
  }

  switch (recommendation.toLowerCase()) {
    case "hire":
      return "bg-foreground text-background"

    case "maybe":
      return "bg-secondary text-secondary-foreground"

    case "no hire":
    case "reject":
      return "bg-destructive/10 text-destructive"

    default:
      return "bg-secondary text-secondary-foreground"
  }
}

export function getInterestClasses(interest: string | null) {
  if (!interest) {
    return "text-muted-foreground"
  }

  switch (interest.toLowerCase()) {
    case "high":
      return "font-medium text-foreground"

    case "medium":
      return "text-muted-foreground"

    case "low":
      return "text-muted-foreground"

    default:
      return "text-muted-foreground"
  }
}
