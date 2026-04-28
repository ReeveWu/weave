"use client"

import { useState, useCallback, useRef } from "react"
import { createJob, getJobResult, getStreamUrl } from "@/lib/api"
import type { JobCreateParams, SSEEvent } from "@/lib/api"

export type JobStatus = "idle" | "uploading" | "running" | "complete" | "error"
export type StepKey =
  | "converting"
  | "uploading"
  | "outline"
  | "expanding"
  | "postprocess"
  | "pdf_export"

export interface StepInfo {
  key: StepKey
  status: "pending" | "active" | "done" | "error"
  detail?: string
}

const STEP_KEYS: StepKey[] = [
  "converting",
  "uploading",
  "outline",
  "expanding",
  "postprocess",
  "pdf_export",
]

const DEFAULT_ERROR_MESSAGES = {
  failed: "處理失敗",
  disconnected: "連線中斷，請重試",
}

function getInitialSteps(): StepInfo[] {
  return STEP_KEYS.map((key) => ({ key, status: "pending" as const }))
}

function stepIndexForEvent(step: string): number {
  if (step === "converting" || step === "converting_done") return 0
  if (step === "uploading" || step === "uploading_done") return 1
  if (step === "outline" || step === "outline_done") return 2
  if (step === "expanding" || step === "chapter_done") return 3
  if (step === "postprocess") return 4
  if (step === "pdf_export" || step === "pdf_done") return 5
  return -1
}

function isDoneEvent(step: string): boolean {
  return (
    step === "converting_done" ||
    step === "uploading_done" ||
    step === "outline_done" ||
    step === "pdf_done"
  )
}

export function usePipelineJob(errorMessages = DEFAULT_ERROR_MESSAGES) {
  const [status, setStatus] = useState<JobStatus>("idle")
  const [steps, setSteps] = useState<StepInfo[]>(getInitialSteps())
  const [jobId, setJobId] = useState<string>("")
  const [markdown, setMarkdown] = useState<string>("")
  const [outputDirName, setOutputDirName] = useState<string>("")
  const [hasPdf, setHasPdf] = useState<boolean>(false)
  const [error, setError] = useState<string>("")
  const eventSourceRef = useRef<EventSource | null>(null)

  const reset = useCallback(() => {
    eventSourceRef.current?.close()
    eventSourceRef.current = null
    setStatus("idle")
    setSteps(getInitialSteps())
    setJobId("")
    setMarkdown("")
    setOutputDirName("")
    setHasPdf(false)
    setError("")
  }, [])

  const updateStep = useCallback((index: number, patch: Partial<StepInfo>) => {
    if (index < 0) return
    setSteps((prev) =>
      prev.map((s, i) => (i === index ? { ...s, ...patch } : s))
    )
  }, [])

  const startJob = useCallback(
    async (files: File[], params: JobCreateParams) => {
      try {
        setStatus("uploading")
        setSteps(getInitialSteps())
        setMarkdown("")
        setError("")

        const { job_id } = await createJob(files, params)
        setJobId(job_id)
        setStatus("running")

        const url = getStreamUrl(job_id)
        const es = new EventSource(url)
        eventSourceRef.current = es

        es.onmessage = (ev) => {
          let event: SSEEvent
          try {
            event = JSON.parse(ev.data) as SSEEvent
          } catch {
            return
          }

          if (event.type === "progress") {
            const idx = stepIndexForEvent(event.step)
            if (isDoneEvent(event.step)) {
              updateStep(idx, { status: "done" })
            } else if (idx >= 0) {
              // Mark previous steps done
              setSteps((prev) =>
                prev.map((s, i) => {
                  if (i < idx && s.status === "pending") return { ...s, status: "done" }
                  if (i === idx) return { ...s, status: "active", detail: event.detail }
                  return s
                })
              )
            }
          } else if (event.type === "complete") {
            es.close()
            // Mark all steps done
            setSteps((prev) => prev.map((s) => ({ ...s, status: "done" as const })))
            // Fetch final result
            getJobResult(job_id)
              .then((result) => {
                setMarkdown(result.markdown)
                setOutputDirName(result.output_dir_name)
                setHasPdf(result.has_pdf)
                setStatus("complete")
              })
              .catch((e) => {
                setError(String(e))
                setStatus("error")
              })
          } else if (event.type === "error") {
            es.close()
            setSteps((prev) =>
              prev.map((s) =>
                s.status === "active" ? { ...s, status: "error" } : s
              )
            )
            setError(event.detail ?? errorMessages.failed)
            setStatus("error")
          }
        }

        es.onerror = () => {
          es.close()
          setError(errorMessages.disconnected)
          setStatus("error")
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : String(e))
        setStatus("error")
      }
    },
    [errorMessages, updateStep]
  )

  return {
    status,
    steps,
    jobId,
    markdown,
    outputDirName,
    hasPdf,
    error,
    startJob,
    reset,
  }
}
