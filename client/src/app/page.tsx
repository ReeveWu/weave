"use client"

import { useState, useEffect, useRef } from "react"
import Image from "next/image"
import { Languages, Loader2, Sparkles, Copy, Check, Download, FileText, RotateCcw } from "lucide-react"
import { Button, buttonVariants } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { FileUploadZone } from "@/components/upload/FileUploadZone"
import { FileList } from "@/components/upload/FileList"
import { PipelineConfigForm } from "@/components/config/PipelineConfigForm"
import { ProgressPanel } from "@/components/progress/ProgressPanel"
import { MarkdownViewer } from "@/components/result/MarkdownViewer"
import { usePipelineJob } from "@/hooks/usePipelineJob"
import { getDownloadUrl } from "@/lib/api"
import { DEFAULT_OUTPUT_LANGUAGE, messages } from "@/lib/i18n"
import { showToast } from "nextjs-toast-notify"
import type { PipelineConfig } from "@/components/config/PipelineConfigForm"
import type { Locale } from "@/lib/i18n"

const DEFAULT_CONFIG: PipelineConfig = {
  provider: "gemini",
  model: "gemini-2.5-flash",
  api_key: "",
  language: "繁體中文",
  export_pdf: true,
}

function GitHubLogo() {
  return (
    <svg
      viewBox="0 0 24 24"
      aria-hidden="true"
      className="size-4 fill-current"
    >
      <path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.11.79-.25.79-.56v-2.16c-3.2.7-3.87-1.36-3.87-1.36-.52-1.33-1.28-1.69-1.28-1.69-1.05-.72.08-.7.08-.7 1.16.08 1.77 1.19 1.77 1.19 1.03 1.76 2.7 1.25 3.36.96.1-.75.4-1.25.73-1.54-2.55-.29-5.23-1.28-5.23-5.68 0-1.25.45-2.28 1.18-3.08-.12-.29-.51-1.46.11-3.04 0 0 .97-.31 3.16 1.18A10.95 10.95 0 0 1 12 6.04c.98 0 1.94.13 2.85.39 2.19-1.49 3.15-1.18 3.15-1.18.63 1.58.24 2.75.12 3.04.74.8 1.18 1.83 1.18 3.08 0 4.42-2.69 5.38-5.25 5.67.42.36.78 1.07.78 2.16v3.15c0 .31.21.67.8.56A11.51 11.51 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5Z" />
    </svg>
  )
}

export default function Home() {
  const [locale, setLocale] = useState<Locale>("zh-TW")
  const [files, setFiles] = useState<File[]>([])
  const [config, setConfig] = useState<PipelineConfig>(DEFAULT_CONFIG)
  const [copied, setCopied] = useState(false)
  const lastNotifiedRef = useRef({ status: "idle", error: "" })
  const t = messages[locale]

  const { status, steps, jobId, markdown, hasPdf, error, startJob, reset } =
    usePipelineJob(t.progress.errors)

  useEffect(() => {
    const last = lastNotifiedRef.current

    if (status === "complete" && last.status !== "complete") {
      showToast.success(t.toast.complete, { duration: 5000, position: "top-right" })
    } else if (status === "error" && error) {
      if (last.status === "error" && last.error === error) return
      showToast.error(error, { duration: 5000, position: "top-right" })
    }

    lastNotifiedRef.current = { status, error }
  }, [status, error, t.toast.complete])

  const isIdle = status === "idle"
  const isRunning = status === "uploading" || status === "running"
  const isComplete = status === "complete"
  const isError = status === "error"
  const canSubmit = files.length > 0 && config.api_key.trim().length > 0 && isIdle

  const showUpload = isIdle || (isError && steps.every((s) => s.status === "pending"))
  const showProgress = isRunning || (isError && steps.some((s) => s.status !== "pending"))

  const toggleLocale = () => {
    setLocale((current) => {
      const next = current === "zh-TW" ? "en" : "zh-TW"

      setConfig((currentConfig) =>
        currentConfig.language === DEFAULT_OUTPUT_LANGUAGE[current]
          ? { ...currentConfig, language: DEFAULT_OUTPUT_LANGUAGE[next] }
          : currentConfig
      )

      return next
    })
  }

  const handleSubmit = async () => {
    if (!canSubmit) {
      if (files.length === 0) {
        showToast.warning(t.toast.missingFile, { duration: 3000, position: "top-right" })
      } else if (!config.api_key.trim()) {
        showToast.warning(t.toast.missingApiKey, { duration: 3000, position: "top-right" })
      }
      return
    }
    showToast.info(t.toast.started, { duration: 4000, position: "top-right" })
    await startJob(files, {
      provider: config.provider,
      model: config.model,
      api_key: config.api_key,
      language: config.language,
      export_pdf: config.export_pdf,
    })
  }

  const handleReset = () => {
    reset()
    setFiles([])
  }

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(markdown)
      setCopied(true)
      showToast.success(t.toast.copySuccess, { duration: 3000, position: "top-right" })
      setTimeout(() => setCopied(false), 2000)
    } catch {
      showToast.error(t.toast.copyError, { duration: 3000, position: "top-right" })
    }
  }

  const handleDownload = (type: "markdown" | "pdf") => {
    const url = getDownloadUrl(jobId, type)
    const a = document.createElement("a")
    a.href = url
    a.download = type === "pdf" ? "handout.pdf" : "handout.md"
    a.click()
    showToast.success(
      type === "pdf" ? t.toast.pdfDownload : t.toast.markdownDownload,
      { duration: 3000, position: "top-right" }
    )
  }

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      {/* Header */}
      <header className="shrink-0 border-b border-border bg-background/80 backdrop-blur-sm">
        <div className="flex items-center justify-between px-6 py-3">
          <div className="flex items-center gap-2.5">
            <span className="bg-gradient-to-r from-[#d96b00] via-[#f5a623] to-[#ff6b2c] bg-clip-text text-xl font-extrabold tracking-normal text-transparent drop-shadow-[0_1px_0_rgba(255,190,96,0.35)]">
              Weave
            </span>
            <Image
              src="/logo.png"
              alt="Weave"
              width={121}
              height={28}
              priority
              className="h-8 w-auto"
            />
          </div>
          <div className="flex items-center gap-3">
            <a
              href="https://github.com/ReeveWu/weave"
              target="_blank"
              rel="noopener noreferrer"
              aria-label={t.header.githubAriaLabel}
              className={buttonVariants({
                variant: "outline",
                size: "icon",
                className: "rounded-full",
              })}
            >
              <GitHubLogo />
            </a>
            <Button
              type="button"
              variant="outline"
              size="sm"
              aria-label={t.header.switchAriaLabel}
              onClick={toggleLocale}
              className="h-8 cursor-pointer"
            >
              <Languages className="size-3.5" data-icon="inline-start" />
              {t.header.switchTo}
            </Button>
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="flex-1 min-h-0 p-4">

        {/* IDLE / ERROR-no-steps: two-column layout */}
        {showUpload && (
          <div className="grid grid-cols-2 gap-4 h-full">
            {/* Left: Upload */}
            <Card className="flex flex-col overflow-hidden">
              <CardHeader className="shrink-0 pb-3">
                <CardTitle>{t.upload.title}</CardTitle>
                <CardDescription>{t.upload.description}</CardDescription>
              </CardHeader>
              <CardContent className="flex-1 min-h-0 overflow-y-auto flex flex-col gap-4 pb-4">
                <FileUploadZone
                  files={files}
                  onFilesChange={setFiles}
                  disabled={isRunning}
                  labels={t.upload}
                />
                <FileList
                  files={files}
                  onRemove={(i) => setFiles((f) => f.filter((_, idx) => idx !== i))}
                  disabled={isRunning}
                  labels={t.upload}
                />
              </CardContent>
            </Card>

            {/* Right: Config + Submit */}
            <Card className="flex flex-col overflow-hidden">
              <CardHeader className="shrink-0 pb-3">
                <CardTitle>{t.config.title}</CardTitle>
                <CardDescription>{t.config.description}</CardDescription>
              </CardHeader>
              <CardContent className="flex-1 min-h-0 overflow-y-auto pb-4">
                <PipelineConfigForm
                  value={config}
                  onChange={setConfig}
                  disabled={isRunning}
                  labels={t.config}
                />
              </CardContent>
              <CardFooter className="shrink-0 border-t border-border pt-4">
                <Button
                  size="lg"
                  className="w-full cursor-pointer"
                  onClick={handleSubmit}
                  disabled={!canSubmit || isRunning}
                >
                  {isRunning ? (
                    <>
                      <Loader2 className="size-4 animate-spin" data-icon="inline-start" />
                      {t.actions.processing}
                    </>
                  ) : (
                    <>
                      <Sparkles className="size-4" data-icon="inline-start" />
                      {t.actions.start}
                    </>
                  )}
                </Button>
              </CardFooter>
            </Card>
          </div>
        )}

        {/* RUNNING / ERROR-with-steps: centered progress */}
        {showProgress && (
          <div className="flex items-center justify-center h-full">
            <Card className="w-full max-w-lg">
              <CardHeader>
                <CardTitle>{t.progress.title}</CardTitle>
                <CardDescription>
                  {isRunning ? t.progress.runningDescription : t.progress.errorDescription}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ProgressPanel
                  status={status}
                  steps={steps}
                  error={error}
                  labels={t.progress}
                />
              </CardContent>
              {isError && (
                <CardFooter>
                  <Button
                    variant="outline"
                    className="w-full cursor-pointer"
                    onClick={handleReset}
                  >
                    {t.actions.retry}
                  </Button>
                </CardFooter>
              )}
            </Card>
          </div>
        )}

        {/* COMPLETE: left action sidebar + right markdown viewer */}
        {isComplete && (
          <div className="grid h-full grid-cols-[240px_minmax(0,1fr)] gap-4">
            {/* Left: actions */}
            <Card className="flex h-full overflow-hidden bg-card/95">
              <CardHeader className="shrink-0 pb-2">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex min-w-0 flex-col gap-1">
                    <CardTitle className="text-lg">{t.result.title}</CardTitle>
                    <CardDescription className="leading-5">{t.result.description}</CardDescription>
                  </div>
                  <Badge variant="secondary" className="mt-0.5 shrink-0">
                    {t.progress.complete}
                  </Badge>
                </div>
              </CardHeader>

              <CardContent className="flex flex-1 flex-col gap-3">
                {hasPdf && (
                  <Button
                    variant="default"
                    size="lg"
                    className="w-full cursor-pointer justify-start"
                    onClick={() => handleDownload("pdf")}
                  >
                    <Download className="size-4" data-icon="inline-start" />
                    {t.actions.downloadPdf}
                  </Button>
                )}

                <div className="flex flex-col gap-2">
                  <Button
                    variant="outline"
                    size="default"
                    className="w-full cursor-pointer justify-start"
                    onClick={handleCopy}
                  >
                    {copied ? (
                      <Check className="size-4 text-primary" data-icon="inline-start" />
                    ) : (
                      <Copy className="size-4" data-icon="inline-start" />
                    )}
                    {copied ? t.common.copied : t.actions.copyMarkdown}
                  </Button>

                  <Button
                    variant="outline"
                    size="default"
                    className="w-full cursor-pointer justify-start"
                    onClick={() => handleDownload("markdown")}
                  >
                    <FileText className="size-4" data-icon="inline-start" />
                    {t.actions.downloadMarkdown}
                  </Button>
                </div>
              </CardContent>

              <CardFooter className="shrink-0 px-4 py-4">
                <Button
                  variant="ghost"
                  size="default"
                  className="w-full cursor-pointer justify-start text-muted-foreground"
                  onClick={handleReset}
                >
                  <RotateCcw className="size-4" data-icon="inline-start" />
                  {t.actions.restart}
                </Button>
              </CardFooter>
            </Card>

            {/* Right: markdown viewer */}
            <Card className="flex h-full min-w-0 flex-col overflow-hidden">
              <CardContent className="flex-1 min-h-0 overflow-y-auto p-6">
                <MarkdownViewer content={markdown} jobId={jobId} />
              </CardContent>
            </Card>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="shrink-0 border-t border-border py-3 text-center text-xs text-muted-foreground">
        {t.footer}
      </footer>
    </div>
  )
}
