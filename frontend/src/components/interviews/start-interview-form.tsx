"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { Loader2 } from "lucide-react"
import { useState } from "react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { startInterview, type StartInterviewRequest } from "@/lib/api"

type FormErrors = Partial<Record<keyof StartInterviewRequest, string>>

const initialForm: StartInterviewRequest = {
  candidate_name: "",
  mobile_number: "",
  job_title: "",
  job_summary: "",
  company_name: "",
  required_skills: "",
  experience_range: "",
  interview_duration: "",
  interview_questions: "",
}

function validateForm(values: StartInterviewRequest): FormErrors {
  const errors: FormErrors = {}

  if (!values.candidate_name.trim()) {
    errors.candidate_name = "Candidate name is required"
  }

  if (!values.mobile_number.trim()) {
    errors.mobile_number = "Mobile number is required"
  } else if (values.mobile_number.trim().length < 10) {
    errors.mobile_number = "Mobile number must be at least 10 digits"
  }

  if (!values.job_title.trim()) {
    errors.job_title = "Job title is required"
  }

  if (!values.job_summary.trim()) {
    errors.job_summary = "Job summary is required"
  }

  if (!values.company_name.trim()) {
    errors.company_name = "Company name is required"
  }

  if (!values.required_skills.trim()) {
    errors.required_skills = "Required skills are required"
  }

  if (!values.experience_range.trim()) {
    errors.experience_range = "Experience range is required"
  }

  if (!values.interview_duration.trim()) {
    errors.interview_duration = "Interview duration is required"
  }

  if (!values.interview_questions.trim()) {
    errors.interview_questions = "Interview questions are required"
  }

  return errors
}

export function StartInterviewForm() {
  const router = useRouter()
  const [form, setForm] = useState(initialForm)
  const [errors, setErrors] = useState<FormErrors>({})
  const [submitError, setSubmitError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)

  function updateField(field: keyof StartInterviewRequest, value: string) {
    setForm((current) => ({ ...current, [field]: value }))

    if (errors[field]) {
      setErrors((current) => ({ ...current, [field]: undefined }))
    }

    if (submitError) {
      setSubmitError(null)
    }
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()

    const validationErrors = validateForm(form)
    setErrors(validationErrors)

    if (Object.keys(validationErrors).length > 0) {
      return
    }

    setIsSubmitting(true)
    setSubmitError(null)

    try {
      const response = await startInterview(form)
      setIsSuccess(true)

      setTimeout(() => {
        router.push(`/interviews/${response.interview_id}`)
      }, 1200)
    } catch (error) {
      setSubmitError(
        error instanceof Error
          ? error.message
          : "Failed to start interview. Please try again.",
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isSuccess) {
    return (
      <div className="rounded-lg border border-dashed bg-muted/20 p-10 text-center">
        <p className="text-lg font-semibold">Interview started successfully</p>

        <p className="mt-2 text-sm text-muted-foreground">
          Redirecting to interview details...
        </p>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      {submitError ? (
        <div
          role="alert"
          className="rounded-lg border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive"
        >
          {submitError}
        </div>
      ) : null}

      <div className="grid gap-6 md:grid-cols-2">
        <div className="space-y-2">
          <label htmlFor="candidate_name" className="text-sm font-medium">
            Candidate Name
          </label>

          <Input
            id="candidate_name"
            value={form.candidate_name}
            onChange={(event) =>
              updateField("candidate_name", event.target.value)
            }
            aria-invalid={Boolean(errors.candidate_name)}
            placeholder="Jane Doe"
          />

          {errors.candidate_name ? (
            <p className="text-xs text-destructive">{errors.candidate_name}</p>
          ) : null}
        </div>

        <div className="space-y-2">
          <label htmlFor="mobile_number" className="text-sm font-medium">
            Mobile Number
          </label>

          <Input
            id="mobile_number"
            type="tel"
            value={form.mobile_number}
            onChange={(event) =>
              updateField("mobile_number", event.target.value)
            }
            aria-invalid={Boolean(errors.mobile_number)}
            placeholder="+91 9876543210"
          />

          {errors.mobile_number ? (
            <p className="text-xs text-destructive">{errors.mobile_number}</p>
          ) : null}
        </div>

        <div className="space-y-2">
          <label htmlFor="job_title" className="text-sm font-medium">
            Job Title
          </label>

          <Input
            id="job_title"
            value={form.job_title}
            onChange={(event) => updateField("job_title", event.target.value)}
            aria-invalid={Boolean(errors.job_title)}
            placeholder="Software Developer"
          />

          {errors.job_title ? (
            <p className="text-xs text-destructive">{errors.job_title}</p>
          ) : null}
        </div>

        <div className="space-y-2">
          <label htmlFor="company_name" className="text-sm font-medium">
            Company Name
          </label>

          <Input
            id="company_name"
            value={form.company_name}
            onChange={(event) =>
              updateField("company_name", event.target.value)
            }
            aria-invalid={Boolean(errors.company_name)}
            placeholder="Acme Corp"
          />

          {errors.company_name ? (
            <p className="text-xs text-destructive">{errors.company_name}</p>
          ) : null}
        </div>

        <div className="space-y-2">
          <label htmlFor="experience_range" className="text-sm font-medium">
            Experience Range
          </label>

          <Input
            id="experience_range"
            value={form.experience_range}
            onChange={(event) =>
              updateField("experience_range", event.target.value)
            }
            aria-invalid={Boolean(errors.experience_range)}
            placeholder="2-4 years"
          />

          {errors.experience_range ? (
            <p className="text-xs text-destructive">
              {errors.experience_range}
            </p>
          ) : null}
        </div>

        <div className="space-y-2">
          <label htmlFor="interview_duration" className="text-sm font-medium">
            Interview Duration
          </label>

          <Input
            id="interview_duration"
            value={form.interview_duration}
            onChange={(event) =>
              updateField("interview_duration", event.target.value)
            }
            aria-invalid={Boolean(errors.interview_duration)}
            placeholder="15 minutes"
          />

          {errors.interview_duration ? (
            <p className="text-xs text-destructive">
              {errors.interview_duration}
            </p>
          ) : null}
        </div>
      </div>

      <div className="space-y-2">
        <label htmlFor="job_summary" className="text-sm font-medium">
          Job Summary
        </label>

        <Textarea
          id="job_summary"
          value={form.job_summary}
          onChange={(event) => updateField("job_summary", event.target.value)}
          aria-invalid={Boolean(errors.job_summary)}
          placeholder="Brief overview of the role and responsibilities..."
          rows={4}
        />

        {errors.job_summary ? (
          <p className="text-xs text-destructive">{errors.job_summary}</p>
        ) : null}
      </div>

      <div className="space-y-2">
        <label htmlFor="required_skills" className="text-sm font-medium">
          Required Skills
        </label>

        <Textarea
          id="required_skills"
          value={form.required_skills}
          onChange={(event) =>
            updateField("required_skills", event.target.value)
          }
          aria-invalid={Boolean(errors.required_skills)}
          placeholder="React, TypeScript, Node.js..."
          rows={3}
        />

        {errors.required_skills ? (
          <p className="text-xs text-destructive">{errors.required_skills}</p>
        ) : null}
      </div>

      <div className="space-y-2">
        <label htmlFor="interview_questions" className="text-sm font-medium">
          Interview Questions
        </label>

        <Textarea
          id="interview_questions"
          value={form.interview_questions}
          onChange={(event) =>
            updateField("interview_questions", event.target.value)
          }
          aria-invalid={Boolean(errors.interview_questions)}
          placeholder="List the questions the AI should ask during the screening..."
          rows={6}
        />

        {errors.interview_questions ? (
          <p className="text-xs text-destructive">
            {errors.interview_questions}
          </p>
        ) : null}
      </div>

      <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
        <Link
          href="/interviews"
          className="inline-flex h-9 items-center justify-center rounded-lg border bg-background px-4 text-sm font-medium transition-colors hover:bg-muted"
        >
          Cancel
        </Link>

        <Button type="submit" disabled={isSubmitting} size="lg">
          {isSubmitting ? (
            <>
              <Loader2 className="animate-spin" />
              Starting Interview...
            </>
          ) : (
            "Start Interview"
          )}
        </Button>
      </div>
    </form>
  )
}
