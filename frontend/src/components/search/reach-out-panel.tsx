"use client"

import { Loader2 } from "lucide-react"
import { useEffect, useRef, useState } from "react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { formatDate } from "@/lib/format"
import {
  getOutreach,
  isTerminalOutreachStatus,
  listOutreach,
  startOutreach,
  type OutreachRecord,
} from "@/lib/outreach-api"
import { savePersonPhone } from "@/lib/people-api"

type ReachOutPanelProps = {
  personId: string
  publicPhone: string | null
  recruiterPhone: string | null
  demoPhone?: string | null
}

const POLL_INTERVAL_MS = 4000
const MAX_POLLS = 45

function isValidPhone(value: string) {
  const digits = value.replace(/\D/g, "")
  return digits.length >= 10
}

function displayValue(value: string | number | null | undefined) {
  if (value === null || value === undefined) {
    return "Not available"
  }

  const text = String(value).trim()
  return text ? text : "Not available"
}

function callHeadline(status: string, lifecycleStatus: string) {
  const values = [status, lifecycleStatus].map((value) => value.toUpperCase())

  if (values.includes("FAILED")) {
    return "Call failed"
  }

  if (values.includes("COMPLETED")) {
    return "Call completed"
  }

  if (
    values.some((value) =>
      ["CANCELLED", "CANCELED", "NOT_CONNECTED", "NO_ANSWER", "BUSY"].includes(
        value,
      ),
    )
  ) {
    return "Call completed"
  }

  return "Call in progress"
}

function parseOutreachResult(result: unknown): Record<string, unknown> | null {
  if (!result) {
    return null
  }

  if (typeof result === "string") {
    try {
      return parseOutreachResult(JSON.parse(result))
    } catch {
      return null
    }
  }

  if (typeof result === "object" && !Array.isArray(result)) {
    return result as Record<string, unknown>
  }

  return null
}

function resultField(result: unknown, keys: string[]) {
  const record = parseOutreachResult(result)

  if (!record) {
    return null
  }

  for (const key of keys) {
    const value = record[key]

    if (value === null || value === undefined) {
      continue
    }

    const text = String(value).trim()

    if (text) {
      return text
    }
  }

  return null
}

export function ReachOutPanel({
  personId,
  publicPhone,
  recruiterPhone,
  demoPhone,
}: ReachOutPanelProps) {
  const confirmedPhone = recruiterPhone ?? ""
  const [phoneInput, setPhoneInput] = useState(
    recruiterPhone || demoPhone || publicPhone || "",
  )
  const [savedPhone, setSavedPhone] = useState(confirmedPhone)
  const [isSaving, setIsSaving] = useState(false)
  const [isStarting, setIsStarting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [outreach, setOutreach] = useState<OutreachRecord | null>(null)
  const pollCountRef = useRef(0)

  const canReachOut = isValidPhone(savedPhone)
  const outreachId = outreach?.id ?? null
  const isPolling = Boolean(
    outreach &&
      !isTerminalOutreachStatus(outreach.status, outreach.lifecycle_status),
  )

  useEffect(() => {
    let cancelled = false

    setOutreach(null)

    async function loadExistingOutreach() {
      try {
        const records = await listOutreach()

        if (cancelled) {
          return
        }

        const matches = records.filter(
          (record) => record.person_id === personId,
        )

        if (matches.length === 0) {
          return
        }

        matches.sort((left, right) => {
          const leftTime = Date.parse(left.created_at) || 0
          const rightTime = Date.parse(right.created_at) || 0

          if (rightTime !== leftTime) {
            return rightTime - leftTime
          }

          return right.id - left.id
        })

        setOutreach(matches[0])
      } catch {
        // Keep the existing UI if historical outreach cannot be loaded.
      }
    }

    void loadExistingOutreach()

    return () => {
      cancelled = true
    }
  }, [personId])

  useEffect(() => {
    if (outreachId === null) {
      return
    }

    let stopped = false
    let intervalId: number | undefined
    pollCountRef.current = 0
    const polledId = outreachId

    async function refreshOutreach() {
      if (stopped) {
        return true
      }

      pollCountRef.current += 1

      if (pollCountRef.current > MAX_POLLS) {
        setMessage(
          "Still waiting for call results. You can keep this page open or check again later.",
        )
        return true
      }

      try {
        const latest = await getOutreach(polledId)

        if (stopped) {
          return true
        }

        setOutreach(latest)

        return isTerminalOutreachStatus(
          latest.status,
          latest.lifecycle_status,
        )
      } catch {
        return false
      }
    }

    void (async () => {
      const terminal = await refreshOutreach()

      if (stopped || terminal) {
        return
      }

      intervalId = window.setInterval(async () => {
        const done = await refreshOutreach()

        if (done && intervalId !== undefined) {
          window.clearInterval(intervalId)
        }
      }, POLL_INTERVAL_MS)

      if (stopped) {
        window.clearInterval(intervalId)
      }
    })()

    return () => {
      stopped = true

      if (intervalId !== undefined) {
        window.clearInterval(intervalId)
      }
    }
  }, [outreachId])

  async function handleSave() {
    setIsSaving(true)
    setError(null)
    setMessage(null)

    try {
      const person = await savePersonPhone(personId, phoneInput)
      const nextPhone = person.phone ?? phoneInput.trim()
      setSavedPhone(nextPhone)
      setPhoneInput(nextPhone)
      setMessage("Phone number saved.")
    } catch (caught) {
      setError(
        caught instanceof Error
          ? caught.message
          : "Could not save the phone number.",
      )
    } finally {
      setIsSaving(false)
    }
  }

  async function handleReachOut() {
    if (!canReachOut || isStarting || isPolling) {
      return
    }

    setIsStarting(true)
    setError(null)
    setMessage(null)

    try {
      const started = await startOutreach(personId, savedPhone)
      const latest = await getOutreach(started.id)
      setOutreach(latest)
      setMessage("AI outreach call initiated")
    } catch (caught) {
      setError(
        caught instanceof Error
          ? caught.message
          : "Unable to start the AI outreach call.",
      )
    } finally {
      setIsStarting(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="rounded-lg border p-4 text-sm text-muted-foreground">
        Candidate → Contact → Phone saved → Reach Out with Hunar AI → Outreach
        status → Conversation result
      </div>

      <div className="space-y-4 rounded-lg border p-4">
        <div>
          <p className="text-sm font-medium">Contact information</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Confirm a phone number before outreach. Demo or public numbers are
            not used until you save them and click Reach Out.
          </p>
        </div>

        {demoPhone ? (
          <div className="rounded-md bg-muted/40 px-3 py-2">
            <p className="text-sm text-muted-foreground">Phone</p>
            <p className="font-medium">{demoPhone}</p>
            <p className="mt-1 text-xs text-muted-foreground">
              Source: Demo Data
            </p>
          </div>
        ) : (
          <div className="rounded-md bg-muted/40 px-3 py-2">
            <p className="text-sm text-muted-foreground">
              Public professional phone
            </p>
            <p className="font-medium">
              {publicPhone ? publicPhone : "Not available"}
            </p>
            <p className="mt-1 text-xs text-muted-foreground">
              {publicPhone ? "Source: Public Web" : ""}
            </p>
          </div>
        )}

        <div className="space-y-2">
          <label htmlFor="contact_phone" className="text-sm font-medium">
            Recruiter-provided phone
          </label>

          <Input
            id="contact_phone"
            type="tel"
            value={phoneInput}
            onChange={(event) => {
              setPhoneInput(event.target.value)
              setError(null)
              setMessage(null)
            }}
            placeholder="+91 9876543210"
          />
        </div>

        {error ? (
          <p className="text-sm text-destructive" role="alert">
            {error}
          </p>
        ) : null}

        {message ? (
          <p className="text-sm text-muted-foreground">{message}</p>
        ) : null}

        <div className="flex flex-col gap-2 sm:flex-row">
          <Button
            type="button"
            variant="outline"
            onClick={handleSave}
            disabled={isSaving || isStarting || !isValidPhone(phoneInput)}
          >
            {isSaving ? "Saving..." : "Save phone number"}
          </Button>

          <Button
            type="button"
            onClick={handleReachOut}
            disabled={!canReachOut || isStarting || isPolling}
          >
            {isStarting ? (
              <>
                <Loader2 className="animate-spin" />
                Starting AI outreach...
              </>
            ) : (
              "Reach Out with Hunar AI"
            )}
          </Button>
        </div>

        {!canReachOut ? (
          <p className="text-xs text-muted-foreground">
            Save a valid phone number to confirm it before starting outreach.
            A discovered public number is not used until you save it.
          </p>
        ) : (
          <p className="text-xs text-muted-foreground">
            Outreach starts only when you click Reach Out with Hunar AI.
          </p>
        )}
      </div>

      {outreach ? (
        <div className="space-y-4 rounded-lg border p-4">
          <div>
            <p className="text-sm font-medium">Outreach status</p>
            <p className="mt-1 text-sm text-muted-foreground">
              {callHeadline(outreach.status, outreach.lifecycle_status)}
            </p>
          </div>

          <dl className="grid gap-3 text-sm sm:grid-cols-2">
            <div>
              <dt className="text-muted-foreground">Status</dt>
              <dd className="font-medium">{displayValue(outreach.status)}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Lifecycle status</dt>
              <dd className="font-medium">
                {displayValue(outreach.lifecycle_status)}
              </dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Outreach ID</dt>
              <dd className="font-medium">{outreach.id}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Call ID</dt>
              <dd className="font-medium">{displayValue(outreach.call_id)}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Created</dt>
              <dd className="font-medium">
                {outreach.created_at
                  ? formatDate(outreach.created_at)
                  : "Not available"}
              </dd>
            </div>
          </dl>
        </div>
      ) : null}

      {outreach &&
      isTerminalOutreachStatus(outreach.status, outreach.lifecycle_status) ? (
        <div className="space-y-4 rounded-lg border p-4">
          <p className="text-sm font-medium">Conversation result</p>

          <dl className="grid gap-3 text-sm sm:grid-cols-2">
            <div>
              <dt className="text-muted-foreground">Open to opportunities</dt>
              <dd className="font-medium">
                {displayValue(
                  resultField(outreach.result, [
                    "open_to_opportunities",
                    "open_to_opportunity",
                  ]) ?? outreach.engagement_status,
                )}
              </dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Notice period</dt>
              <dd className="font-medium">
                {displayValue(
                  resultField(outreach.result, ["notice_period"]),
                )}
              </dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Salary expectation</dt>
              <dd className="font-medium">
                {displayValue(
                  resultField(outreach.result, [
                    "salary_expectation",
                    "expected_compensation",
                  ]),
                )}
              </dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Engagement status</dt>
              <dd className="font-medium">
                {displayValue(outreach.engagement_status)}
              </dd>
            </div>
          </dl>

          <div>
            <p className="text-sm text-muted-foreground">AI result / summary</p>
            <p className="mt-1 whitespace-pre-wrap text-sm">
              {displayValue(
                resultField(outreach.result, [
                  "candidate_summary",
                  "summary",
                  "recruiter_summary",
                ]),
              )}
            </p>
          </div>

          {outreach.recording_url ? (
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Recording</p>
              <audio
                controls
                className="w-full"
                src={outreach.recording_url}
                preload="metadata"
              >
                Your browser does not support the audio element.
              </audio>
              <a
                href={outreach.recording_url}
                target="_blank"
                rel="noreferrer"
                className="text-sm font-medium hover:underline"
              >
                Open recording
              </a>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              Recording: Not available
            </p>
          )}
        </div>
      ) : null}
    </div>
  )
}
