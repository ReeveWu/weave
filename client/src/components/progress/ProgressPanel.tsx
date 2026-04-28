"use client"

import { StepIndicator } from "./StepIndicator"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { AlertCircle } from "lucide-react"
import type { StepInfo, JobStatus, StepKey } from "@/hooks/usePipelineJob"

interface ProgressPanelProps {
  status: JobStatus
  steps: StepInfo[]
  error: string
  labels: {
    complete: string
    running: string
    steps: Record<StepKey, string>
  }
}

function calcProgress(steps: StepInfo[]): number {
  const done = steps.filter((s) => s.status === "done").length
  const active = steps.findIndex((s) => s.status === "active")
  if (active >= 0) return Math.round(((done + 0.5) / steps.length) * 100)
  return Math.round((done / steps.length) * 100)
}

export function ProgressPanel({ status, steps, error, labels }: ProgressPanelProps) {
  const progress = calcProgress(steps)

  return (
    <div className="flex flex-col gap-4">
      {/* Progress bar */}
      {(status === "running" || status === "complete") && (
        <div className="flex flex-col gap-1.5">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">
              {status === "complete" ? labels.complete : labels.running}
            </span>
            <span className="text-xs font-medium text-primary">{progress}%</span>
          </div>
          <Progress value={progress} className="h-1.5" />
        </div>
      )}

      {/* Steps */}
      <StepIndicator steps={steps} stepLabels={labels.steps} />

      {/* Error */}
      {status === "error" && error && (
        <Alert variant="destructive">
          <AlertCircle className="size-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
    </div>
  )
}
