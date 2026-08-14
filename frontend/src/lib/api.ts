const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"

export type InterviewListItem = {
  id: number
  candidate_id: number
  call_id: string
  job_title: string
  status: string
  overall_score: number | null
  recommendation: string | null
  interest_level: string | null
  created_at: string
}

export type InterviewDetails = {
  id: number
  candidate: {
    id: number
    name: string
    mobile_number: string
  }
  call_id: string
  job_title: string
  status: string
  scores: {
    overall: number | null
    technical: number | null
    communication: number | null
    experience: number | null
    problem_solving: number | null
    role_fit: number | null
  }
  recommendation: string | null
  interest_level: string | null
  summary: string | null
  strengths: string | null
  concerns: string | null
  next_steps: string | null
  transcript: string | null
  recording_url: string | null
  duration_seconds: number | null
  created_at: string
  updated_at: string
}

export type StartInterviewRequest = {
  candidate_name: string
  mobile_number: string
  job_title: string
  job_summary: string
  company_name: string
  required_skills: string
  experience_range: string
  interview_duration: string
  interview_questions: string
}

export type StartInterviewResponse = {
  success: boolean
  message: string
  candidate_id: number
  interview_id: number
  call: {
    id: string
    status?: string
  }
}

export type InterviewListItemEnriched = InterviewListItem & {
  candidate_name: string
}

export type CandidateSummary = {
  id: number
  name: string
  mobile_number: string
  interview_count: number
  latest_interview_id: number
  latest_job_title: string
  latest_status: string
  latest_recommendation: string | null
  average_score: number | null
  latest_interview_date: string
}

export type JobSummary = {
  title: string
  interview_count: number
  completed_count: number
  average_score: number | null
}

export async function getInterviews(): Promise<InterviewListItem[]> {
  const response = await fetch(`${API_URL}/api/dashboard/interviews`, {
    cache: "no-store",
  })

  if (!response.ok) {
    throw new Error("Failed to fetch interviews")
  }

  return response.json()
}

export async function getInterview(id: number): Promise<InterviewDetails> {
  const response = await fetch(`${API_URL}/api/dashboard/interviews/${id}`, {
    cache: "no-store",
  })

  if (!response.ok) {
    throw new Error("Failed to fetch interview")
  }

  return response.json()
}

export async function startInterview(
  data: StartInterviewRequest,
): Promise<StartInterviewResponse> {
  const response = await fetch(`${API_URL}/api/interviews/start`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const errorText = await response.text()

    throw new Error(errorText || "Failed to start interview")
  }

  return response.json()
}

export async function getInterviewsEnriched(): Promise<
  InterviewListItemEnriched[]
> {
  const interviews = await getInterviews()

  const details = await Promise.all(
    interviews.map((interview) =>
      getInterview(interview.id).catch(() => null),
    ),
  )

  return interviews.map((interview, index) => ({
    ...interview,
    candidate_name:
      details[index]?.candidate.name ??
      `Candidate #${interview.candidate_id}`,
  }))
}

export async function getCandidateSummaries(): Promise<CandidateSummary[]> {
  const interviews = await getInterviewsEnriched()
  const details = await Promise.all(
    interviews.map((interview) =>
      getInterview(interview.id).catch(() => null),
    ),
  )

  const candidateMap = new Map<
    number,
    CandidateSummary & { scoreSum: number; scoredCount: number }
  >()

  interviews.forEach((interview, index) => {
    const detail = details[index]
    const existing = candidateMap.get(interview.candidate_id)

    if (!existing) {
      candidateMap.set(interview.candidate_id, {
        id: interview.candidate_id,
        name: detail?.candidate.name ?? interview.candidate_name,
        mobile_number: detail?.candidate.mobile_number ?? "—",
        interview_count: 1,
        latest_interview_id: interview.id,
        latest_job_title: interview.job_title,
        latest_status: interview.status,
        latest_recommendation: interview.recommendation,
        average_score: null,
        latest_interview_date: interview.created_at,
        scoreSum: interview.overall_score ?? 0,
        scoredCount: interview.overall_score !== null ? 1 : 0,
      })

      return
    }

    const updated = {
      ...existing,
      interview_count: existing.interview_count + 1,
      scoreSum: existing.scoreSum + (interview.overall_score ?? 0),
      scoredCount:
        existing.scoredCount + (interview.overall_score !== null ? 1 : 0),
    }

    if (
      new Date(interview.created_at) > new Date(existing.latest_interview_date)
    ) {
      updated.latest_interview_id = interview.id
      updated.latest_job_title = interview.job_title
      updated.latest_status = interview.status
      updated.latest_recommendation = interview.recommendation
      updated.latest_interview_date = interview.created_at
    }

    candidateMap.set(interview.candidate_id, updated)
  })

  return Array.from(candidateMap.values())
    .map(({ scoreSum, scoredCount, ...candidate }) => ({
      ...candidate,
      average_score:
        scoredCount > 0 ? Math.round(scoreSum / scoredCount) : null,
    }))
    .sort(
      (a, b) =>
        new Date(b.latest_interview_date).getTime() -
        new Date(a.latest_interview_date).getTime(),
    )
}

export async function getJobSummaries(): Promise<JobSummary[]> {
  const interviews = await getInterviews()
  const jobMap = new Map<
    string,
    JobSummary & { scoreSum: number }
  >()

  for (const interview of interviews) {
    const existing = jobMap.get(interview.job_title) ?? {
      title: interview.job_title,
      interview_count: 0,
      completed_count: 0,
      average_score: null,
      scoreSum: 0,
    }

    existing.interview_count += 1

    if (interview.status === "COMPLETED" && interview.overall_score !== null) {
      existing.completed_count += 1
      existing.scoreSum += interview.overall_score
    }

    jobMap.set(interview.job_title, existing)
  }

  return Array.from(jobMap.values())
    .map(({ scoreSum, completed_count, ...job }) => ({
      ...job,
      completed_count,
      average_score:
        completed_count > 0 ? Math.round(scoreSum / completed_count) : null,
    }))
    .sort((a, b) => b.interview_count - a.interview_count)
}
