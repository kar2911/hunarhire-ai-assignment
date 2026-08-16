"use client"

import { useState } from "react"

import { SearchForm } from "@/components/search/search-form"
import { SearchResults } from "@/components/search/search-results"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  searchPeople,
  type SearchPeopleResponse,
} from "@/lib/people-api"

export function PeopleSearchPanel() {
  const [jobDescription, setJobDescription] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hasSearched, setHasSearched] = useState(false)
  const [result, setResult] = useState<SearchPeopleResponse | null>(null)

  async function handleSearch() {
    setIsLoading(true)
    setError(null)

    try {
      const response = await searchPeople(jobDescription)
      setResult(response)
      setHasSearched(true)
    } catch (caught) {
      setHasSearched(true)
      setResult(null)
      setError(
        caught instanceof Error
          ? caught.message
          : "People search failed. Please try again.",
      )
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      <Card>
        <CardHeader>
          <CardTitle>Job Description</CardTitle>
        </CardHeader>

        <CardContent>
          <SearchForm
            value={jobDescription}
            onChange={setJobDescription}
            onSubmit={handleSearch}
            isLoading={isLoading}
          />
        </CardContent>
      </Card>

      {error ? (
        <div
          role="alert"
          className="rounded-lg border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive"
        >
          {error}
        </div>
      ) : null}

      {!hasSearched && !isLoading ? (
        <div className="rounded-lg border border-dashed p-12 text-center">
          <p className="font-medium">No search yet</p>

          <p className="mt-1 text-sm text-muted-foreground">
            Paste a job description. We search public professional profiles.
          </p>
        </div>
      ) : null}

      {result ? (
        <SearchResults
          provider={result.provider}
          source={result.source}
          isMock={result.is_mock}
          isDemo={result.is_demo}
          criteria={result.search_criteria}
          results={result.results}
        />
      ) : null}
    </div>
  )
}
