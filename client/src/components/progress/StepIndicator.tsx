"use client"

import { Check, Loader2, AlertCircle } from "lucide-react"
import { cn } from "@/lib/utils"
import type { StepInfo, StepKey } from "@/hooks/usePipelineJob"

interface StepIndicatorProps {
  steps: StepInfo[]
  stepLabels: Record<StepKey, string>
}

export function StepIndicator({ steps, stepLabels }: StepIndicatorProps) {
  return (
    <ol className="flex flex-col gap-3">
      {steps.map((step, i) => (
        <li key={step.key} className="flex items-start gap-3">
          {/* Icon */}
          <div
            className={cn(
              "flex size-6 shrink-0 items-center justify-center rounded-full border-2 transition-all duration-300",
              step.status === "done" &&
                "border-primary bg-primary text-primary-foreground",
              step.status === "active" &&
                "border-primary bg-background text-primary",
              step.status === "error" &&
                "border-destructive bg-destructive/10 text-destructive",
              step.status === "pending" &&
                "border-border bg-background text-muted-foreground"
            )}
          >
            {step.status === "done" && <Check className="size-3.5" />}
            {step.status === "active" && (
              <Loader2 className="size-3.5 animate-spin" />
            )}
            {step.status === "error" && <AlertCircle className="size-3.5" />}
            {step.status === "pending" && (
              <span className="text-xs font-medium leading-none">{i + 1}</span>
            )}
          </div>

          {/* Label */}
          <div className="flex flex-col gap-0.5 pt-0.5">
            <span
              className={cn(
                "text-sm font-medium transition-colors",
                step.status === "done" && "text-primary",
                step.status === "active" && "text-foreground",
                step.status === "error" && "text-destructive",
                step.status === "pending" && "text-muted-foreground"
              )}
            >
              {stepLabels[step.key]}
            </span>
            {step.detail && step.status === "active" && (
              <span className="text-xs text-muted-foreground">{step.detail}</span>
            )}
          </div>
        </li>
      ))}
    </ol>
  )
}
