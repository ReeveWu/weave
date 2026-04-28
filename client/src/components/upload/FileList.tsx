"use client"

import { X, FileText } from "lucide-react"
import { Button } from "@/components/ui/button"

interface FileListProps {
  files: File[]
  onRemove: (index: number) => void
  disabled?: boolean
  labels: {
    removeFile: (name: string) => string
  }
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export function FileList({ files, onRemove, disabled, labels }: FileListProps) {
  if (files.length === 0) return null

  return (
    <ul className="flex flex-col gap-1.5">
      {files.map((file, i) => (
        <li
          key={`${file.name}-${file.size}-${i}`}
          className="flex items-center gap-2 rounded-lg border border-border bg-card px-3 py-2"
        >
          <FileText className="size-4 shrink-0 text-primary" />
          <span className="flex-1 truncate text-sm text-foreground">{file.name}</span>
          <span className="shrink-0 text-xs text-muted-foreground">{formatSize(file.size)}</span>
          <Button
            variant="ghost"
            size="icon-xs"
            aria-label={labels.removeFile(file.name)}
            disabled={disabled}
            onClick={() => onRemove(i)}
            className="shrink-0 cursor-pointer"
          >
            <X className="size-3.5" />
          </Button>
        </li>
      ))}
    </ul>
  )
}
