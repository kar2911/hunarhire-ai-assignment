"use client"

import { Loader2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"

const EXAMPLE_JOB_DESCRIPTION = `We are looking for a Senior Python Developer with 5+ years of experience building backend systems. Strong Python, FastAPI, PostgreSQL, AWS and React experience preferred. Candidate should be based in Bangalore or willing to relocate.`

type SearchFormProps = {
  value: string
  onChange: (value: string) => void
  onSubmit: () => void
  isLoading: boolean
}

export function SearchForm({
  value,
  onChange,
  onSubmit,
  isLoading,
}: SearchFormProps) {
  return (
    <form
      className="space-y-4"
      onSubmit={(event) => {
        event.preventDefault()
        onSubmit()
      }}
    >
      <div className="space-y-2">
        <label htmlFor="job_description" className="text-sm font-medium">
          Job Description
        </label>

        <Textarea
          id="job_description"
          value={value}
          onChange={(event) => onChange(event.target.value)}
          placeholder={EXAMPLE_JOB_DESCRIPTION}
          rows={8}
          className="min-h-40"
          disabled={isLoading}
        />

        <p className="text-xs text-muted-foreground">
          Paste a full job description. We extract search criteria and find
          public professional profiles.
        </p>
      </div>

      <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
        <Button
          type="button"
          variant="outline"
          disabled={isLoading}
          onClick={() => onChange(EXAMPLE_JOB_DESCRIPTION)}
        >
          Use example
        </Button>

        <Button type="submit" size="lg" disabled={isLoading}>
          {isLoading ? (
            <>
              <Loader2 className="animate-spin" />
              Finding people...
            </>
          ) : (
            "Find People"
          )}
        </Button>
      </div>
    </form>
  )
}
