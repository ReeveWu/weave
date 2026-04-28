"use client"

import { useCallback, useRef, useState } from "react"
import { UploadCloud } from "lucide-react"
import { cn } from "@/lib/utils"

interface FileUploadZoneProps {
  files: File[]
  onFilesChange: (files: File[]) => void
  disabled?: boolean
  labels: {
    ariaLabel: string
    prompt: string
    action: string
    hint: string
    selectedCount: (count: number) => string
  }
}

export function FileUploadZone({ files, onFilesChange, disabled, labels }: FileUploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const addFiles = useCallback(
    (incoming: FileList | null) => {
      if (!incoming) return
      const pdfs = Array.from(incoming).filter((f) => f.type === "application/pdf")
      if (pdfs.length === 0) return
      const existing = new Set(files.map((f) => f.name + f.size))
      const merged = [...files, ...pdfs.filter((f) => !existing.has(f.name + f.size))]
      onFilesChange(merged)
    },
    [files, onFilesChange]
  )

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragging(false)
      if (disabled) return
      addFiles(e.dataTransfer.files)
    },
    [disabled, addFiles]
  )

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    if (!disabled) setIsDragging(true)
  }, [disabled])

  const handleDragLeave = useCallback(() => setIsDragging(false), [])

  const handleClick = useCallback(() => {
    if (!disabled) inputRef.current?.click()
  }, [disabled])

  return (
    <div
      role="button"
      tabIndex={disabled ? -1 : 0}
      aria-label={labels.ariaLabel}
      onClick={handleClick}
      onKeyDown={(e) => e.key === "Enter" && handleClick()}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      className={cn(
        "flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed p-10 text-center transition-colors duration-150 select-none",
        isDragging
          ? "border-primary bg-accent"
          : "border-border hover:border-primary hover:bg-accent/50",
        disabled
          ? "cursor-not-allowed opacity-50"
          : "cursor-pointer"
      )}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,application/pdf"
        multiple
        className="sr-only"
        onChange={(e) => addFiles(e.target.files)}
        disabled={disabled}
      />
      <UploadCloud
        className={cn(
          "size-10 transition-colors",
          isDragging ? "text-primary" : "text-muted-foreground"
        )}
      />
      <div className="flex flex-col gap-1">
        <p className="text-sm font-medium text-foreground">
          {labels.prompt}<span className="text-primary"> {labels.action}</span>
        </p>
        <p className="text-xs text-muted-foreground">{labels.hint}</p>
      </div>
      {files.length > 0 && (
        <p className="text-xs text-primary font-medium">
          {labels.selectedCount(files.length)}
        </p>
      )}
    </div>
  )
}
