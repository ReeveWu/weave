"use client"

import { useState } from "react"
import { Copy, Check, Download, FileText, RotateCcw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { ScrollArea } from "@/components/ui/scroll-area"
import { MarkdownViewer } from "./MarkdownViewer"
import { getDownloadUrl } from "@/lib/api"
import { showToast } from "nextjs-toast-notify"
import type { Messages } from "@/lib/i18n"

interface ResultPanelProps {
  markdown: string
  jobId: string
  hasPdf: boolean
  onReset: () => void
  labels: {
    actions: Messages["actions"]
    toast: Messages["toast"]
    common: Messages["common"]
  }
}

export function ResultPanel({ markdown, jobId, hasPdf, onReset, labels }: ResultPanelProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(markdown)
      setCopied(true)
      showToast.success(labels.toast.copySuccess, { duration: 3000, position: "top-right" })
      setTimeout(() => setCopied(false), 2000)
    } catch {
      showToast.error(labels.toast.copyError, { duration: 3000, position: "top-right" })
    }
  }

  const handleDownload = (type: "markdown" | "pdf") => {
    const url = getDownloadUrl(jobId, type)
    const a = document.createElement("a")
    a.href = url
    a.download = type === "pdf" ? "handout.pdf" : "handout.md"
    a.click()
    showToast.success(
      type === "pdf" ? labels.toast.pdfDownload : labels.toast.markdownDownload,
      { duration: 3000, position: "top-right" }
    )
  }

  return (
    <div className="flex flex-col gap-4">
      {/* Toolbar */}
      <div className="flex items-center gap-2 flex-wrap">
        <Button
          variant="outline"
          size="sm"
          onClick={handleCopy}
          className="cursor-pointer"
          data-icon="inline-start"
        >
          {copied ? (
            <Check className="size-3.5 text-primary" data-icon="inline-start" />
          ) : (
            <Copy className="size-3.5" data-icon="inline-start" />
          )}
          {copied ? labels.common.copied : labels.actions.copyMarkdown}
        </Button>

        <Button
          variant="outline"
          size="sm"
          onClick={() => handleDownload("markdown")}
          className="cursor-pointer"
          data-icon="inline-start"
        >
          <FileText className="size-3.5" data-icon="inline-start" />
          {labels.actions.downloadMarkdown}
        </Button>

        {hasPdf && (
          <Button
            variant="default"
            size="sm"
            onClick={() => handleDownload("pdf")}
            className="cursor-pointer"
            data-icon="inline-start"
          >
            <Download className="size-3.5" data-icon="inline-start" />
            {labels.actions.downloadPdf}
          </Button>
        )}

        <div className="flex-1" />

        <Button
          variant="ghost"
          size="sm"
          onClick={onReset}
          className="cursor-pointer text-muted-foreground"
          data-icon="inline-start"
        >
          <RotateCcw className="size-3.5" data-icon="inline-start" />
          {labels.actions.restart}
        </Button>
      </div>

      <Separator />

      {/* Markdown preview */}
      <ScrollArea className="h-[480px] rounded-lg border border-border bg-card p-4">
        <MarkdownViewer content={markdown} jobId={jobId} />
      </ScrollArea>
    </div>
  )
}
