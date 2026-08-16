const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"

export type SearchCriteria = {
  job_title: string | null
  skills: string[]
  location: string | null
  seniority: string | null
  years_experience: number | null
  company: string | null
  keywords: string[]
}

export type ExperienceItem = {
  title: string | null
  company: string | null
  location: string | null
  start_date: string | null
  end_date: string | null
  description: string | null
}

export type EducationItem = {
  school: string | null
  degree: string | null
  field: string | null
  start_date: string | null
  end_date: string | null
}

export type NormalizedPerson = {
  id: string
  provider: string
  provider_id: string
  full_name: string | null
  first_name: string | null
  last_name: string | null
  job_title: string | null
  company_name: string | null
  company_website: string | null
  location: string | null
  linkedin_url: string | null
  skills: string[]
  headline: string | null
  summary: string | null
  email: string | null
  phone: string | null
  phone_source: "public_web" | "recruiter_provided" | "demo_data" | null
  public_phone: string | null
  experience: ExperienceItem[]
  education: EducationItem[]
}

export type SearchPeopleResponse = {
  search_criteria: SearchCriteria
  provider: string
  source?: string
  is_mock: boolean
  is_demo?: boolean
  total: number
  results: NormalizedPerson[]
}

async function readError(response: Response): Promise<string> {
  const text = await response.text()

  try {
    const payload = JSON.parse(text) as { detail?: unknown }

    if (typeof payload.detail === "string") {
      return payload.detail
    }

    if (Array.isArray(payload.detail)) {
      return payload.detail
        .map((item) => {
          if (typeof item === "string") {
            return item
          }

          if (
            item &&
            typeof item === "object" &&
            "msg" in item &&
            typeof item.msg === "string"
          ) {
            return item.msg
          }

          return ""
        })
        .filter(Boolean)
        .join(" ")
    }
  } catch {
    // Fall through to raw text.
  }

  return text || `Request failed with status ${response.status}`
}

export async function searchPeople(
  jobDescription: string,
): Promise<SearchPeopleResponse> {
  const response = await fetch(`${API_URL}/api/search/people`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      job_description: jobDescription,
    }),
  })

  if (!response.ok) {
    throw new Error(await readError(response))
  }

  return response.json()
}

export async function getPerson(id: string): Promise<NormalizedPerson> {
  const response = await fetch(
    `${API_URL}/api/people/${encodeURIComponent(id)}`,
    {
      cache: "no-store",
    },
  )

  if (!response.ok) {
    throw new Error(await readError(response))
  }

  return response.json()
}

export async function savePersonPhone(
  id: string,
  phone: string,
): Promise<NormalizedPerson> {
  const response = await fetch(
    `${API_URL}/api/people/${encodeURIComponent(id)}/phone`,
    {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ phone }),
    },
  )

  if (!response.ok) {
    throw new Error(await readError(response))
  }

  return response.json()
}
