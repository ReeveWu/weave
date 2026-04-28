"use client"

import { Eye, EyeOff } from "lucide-react"
import { useState } from "react"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import type { Messages } from "@/lib/i18n"
import type { JobCreateParams } from "@/lib/api"

// ---------------------------------------------------------------------------
// Provider → model catalogue
// ---------------------------------------------------------------------------

type Provider = "gemini" | "openai" | "claude"

interface ModelEntry {
  value: string
  label: string
  recommended?: boolean
}

const MODELS_BY_PROVIDER: Record<Provider, ModelEntry[]> = {
  gemini: [
    { value: "gemini-2.5-pro", label: "Gemini 2.5 Pro" },
    { value: "gemini-2.5-flash", label: "Gemini 2.5 Flash", recommended: true },
    { value: "gemini-2.5-flash-lite", label: "Gemini 2.5 Flash Lite" },
    { value: "gemini-3.1-pro-preview", label: "Gemini 3.1 Pro Preview" },
    { value: "gemini-3-flash-preview", label: "Gemini 3 Flash Preview" },
    { value: "gemini-3.1-flash-lite-preview", label: "Gemini 3.1 Flash Lite Preview" },
  ],
  openai: [
    { value: "gpt-5.4-pro", label: "gpt-5.4-pro" },
    { value: "gpt-5.4", label: "gpt-5.4" },
    { value: "gpt-5.4-mini", label: "gpt-5.4-mini" },
    { value: "gpt-5.1", label: "gpt-5.1" },
    { value: "gpt-5", label: "gpt-5" },
    { value: "gpt-5-mini", label: "gpt-5-mini" },
    { value: "gpt-4.1", label: "gpt-4.1" },
    { value: "gpt-4.1-mini", label: "gpt-4.1-mini" },
  ],
  claude: [
    { value: "claude-opus-4-7", label: "Claude Opus 4.7" },
    { value: "claude-sonnet-4-5", label: "Claude Sonnet 4.5", recommended: true },
    { value: "claude-haiku-3-5", label: "Claude Haiku 3.5" },
    { value: "claude-opus-4-5", label: "Claude Opus 4.5" },
  ],
}

const PROVIDERS: { value: Provider; label: string }[] = [
  { value: "gemini", label: "Google Gemini" },
  { value: "openai", label: "OpenAI" },
  { value: "claude", label: "Anthropic Claude" },
]

const LANGUAGES = [
  { value: "繁體中文", label: "繁體中文" },
  { value: "English", label: "English" },
  { value: "简体中文", label: "简体中文" },
  { value: "日本語", label: "日本語" },
  { value: "한국어", label: "한국어" },
]

// ---------------------------------------------------------------------------

export interface PipelineConfig extends JobCreateParams {
  model: string
}

interface PipelineConfigFormProps {
  value: PipelineConfig
  onChange: (value: PipelineConfig) => void
  disabled?: boolean
  labels: Messages["config"]
}

export function PipelineConfigForm({ value, onChange, disabled, labels }: PipelineConfigFormProps) {
  const [showKey, setShowKey] = useState(false)

  const set = <K extends keyof PipelineConfig>(key: K, val: PipelineConfig[K]) => {
    onChange({ ...value, [key]: val })
  }

  const handleProviderChange = (newProvider: string) => {
    const p = newProvider as Provider
    const defaultModel = MODELS_BY_PROVIDER[p].find((m) => m.recommended)?.value
      ?? MODELS_BY_PROVIDER[p][0]?.value
      ?? ""
    onChange({ ...value, provider: p, model: defaultModel })
  }

  const currentProvider = (value.provider as Provider) in MODELS_BY_PROVIDER
    ? (value.provider as Provider)
    : "gemini"

  const models = MODELS_BY_PROVIDER[currentProvider]
  const apiKeyHint = labels.apiKeyHint[currentProvider]
  const apiKeyLink = labels.apiKeyLinks[currentProvider]
  const apiKeyLinkText = labels.apiKeyLinkText[currentProvider]

  return (
    <div className="flex flex-col gap-4">
      {/* Provider */}
      <div className="flex flex-col gap-1.5">
        <Label className="text-sm font-medium">{labels.provider}</Label>
        <Select
          value={currentProvider}
          onValueChange={(v) => v && handleProviderChange(v)}
          disabled={disabled}
        >
          <SelectTrigger className="w-full">
            <SelectValue placeholder={labels.providerPlaceholder} />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              {PROVIDERS.map((p) => (
                <SelectItem key={p.value} value={p.value}>
                  {p.label}
                </SelectItem>
              ))}
            </SelectGroup>
          </SelectContent>
        </Select>
      </div>

      {/* API Key */}
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="api-key" className="text-sm font-medium">
          {labels.apiKey}
        </Label>
        <div className="relative flex items-center">
          <Input
            id="api-key"
            type={showKey ? "text" : "password"}
            placeholder={currentProvider === "gemini" ? "AIza..." : currentProvider === "openai" ? "sk-..." : "sk-ant-..."}
            value={value.api_key}
            onChange={(e) => set("api_key", e.target.value)}
            disabled={disabled}
            className="pr-9"
            autoComplete="off"
          />
          <Button
            type="button"
            variant="ghost"
            size="icon-xs"
            aria-label={showKey ? labels.hideApiKey : labels.showApiKey}
            onClick={() => setShowKey((v) => !v)}
            disabled={disabled}
            className="absolute right-1 cursor-pointer"
          >
            {showKey ? <EyeOff className="size-3.5" /> : <Eye className="size-3.5" />}
          </Button>
        </div>
        <p className="text-xs text-muted-foreground">
          <a
            href={apiKeyLink}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary underline-offset-2 hover:underline"
          >
            {apiKeyLinkText}
          </a>
          {" — "}
          {apiKeyHint}
        </p>
      </div>

      <Separator />

      <div className="grid grid-cols-2 gap-4">
        {/* Model */}
        <div className="flex flex-col gap-1.5">
          <Label className="text-sm font-medium">{labels.model}</Label>
          <Select
            value={value.model}
            onValueChange={(v) => v && set("model", v)}
            disabled={disabled}
          >
            <SelectTrigger className="w-full">
              <SelectValue placeholder={labels.modelPlaceholder} />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                {models.map((m) => (
                  <SelectItem key={m.value} value={m.value}>
                    {m.label}
                    {m.recommended && (
                      <span className="ml-1.5 text-xs text-muted-foreground">
                        ({labels.recommended})
                      </span>
                    )}
                  </SelectItem>
                ))}
              </SelectGroup>
            </SelectContent>
          </Select>
        </div>

        {/* Language */}
        <div className="flex flex-col gap-1.5">
          <Label className="text-sm font-medium">{labels.outputLanguage}</Label>
          <Select
            value={value.language}
            onValueChange={(v) => v && set("language", v)}
            disabled={disabled}
          >
            <SelectTrigger className="w-full">
              <SelectValue placeholder={labels.languagePlaceholder} />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                {LANGUAGES.map((l) => (
                  <SelectItem key={l.value} value={l.value}>
                    {l.label}
                  </SelectItem>
                ))}
              </SelectGroup>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Export PDF toggle */}
      <label className="flex cursor-pointer items-center gap-2.5">
        <input
          type="checkbox"
          checked={value.export_pdf}
          onChange={(e) => set("export_pdf", e.target.checked)}
          disabled={disabled}
          className="size-4 cursor-pointer accent-primary"
        />
        <span className="text-sm text-foreground">{labels.exportPdf}</span>
      </label>
    </div>
  )
}
