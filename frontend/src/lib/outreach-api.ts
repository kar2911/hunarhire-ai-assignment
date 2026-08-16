const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"

export type OutreachStartResponse = {
  id: number
  call_id: string | null
  request_id: string
  status: string
  lifecycle_status: string
}

export type OutreachRecord = {
  id: number
  person_id: string
  person_name: string | null
  job_title: string | null
  phone_number: string
  call_id: string | null
  request_id: string
  status: string
  lifecycle_status: string
  result: unknown
  recording_url: string | null
  duration_seconds: number | null
  answered_by: string | null
  engagement_status: string | null
  created_at: string
  updated_at: string
}

const TERMINAL_STATUSES = new Set([
  "COMPLETED",
  "FAILED",
  "NO_ANSWER",
  "BUSY",
  "CANCELLED",
  "NOT_CONNECTED",
  "CANCELED",
])

export function isTerminalOutreachStatus(
  status: string | null | undefined,
  lifecycleStatus?: string | null,
) {
  const values = [status, lifecycleStatus]
    .filter((value): value is string => Boolean(value))
    .map((value) => value.toUpperCase())

  return values.some((value) => TERMINAL_STATUSES.has(value))
}

async function readError(response: Response): Promise<string> {
  const text = await response.text()

  try {
    const payload = JSON.parse(text) as { detail?: unknown }

    if (typeof payload.detail === "string") {
      return payload.detail
    }
  } catch {
    // Fall through.
  }

  if (response.status === 404) {
    return "This candidate is no longer available in the current search session."
  }

  if (response.status === 422) {
    return "Enter a valid E.164 phone number before starting outreach."
  }

  if (response.status === 503) {
    return "Outreach is not configured yet."
  }

  return "Unable to complete the outreach request."
}

export async function startOutreach(
  personId: string,
  phone: string,
): Promise<OutreachStartResponse> {
  const response = await fetch(`${API_URL}/api/outreach/call`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      person_id: personId,
      phone,
    }),
  })

  if (!response.ok) {
    throw new Error(await readError(response))
  }

  return response.json()
}

export async function getOutreach(id: number): Promise<OutreachRecord> {
  const response = await fetch(`${API_URL}/api/outreach/${id}`, {
    cache: "no-store",
  })

  if (!response.ok) {
    throw new Error(await readError(response))
  }

  return response.json()
}

export async function listOutreach(): Promise<OutreachRecord[]> {
  const response = await fetch(`${API_URL}/api/outreach`, {
    cache: "no-store",
  })

  if (!response.ok) {
    throw new Error(await readError(response))
  }

  const payload: unknown = await response.json()

  if (!Array.isArray(payload)) {
    return []
  }

  return payload as OutreachRecord[]
}
