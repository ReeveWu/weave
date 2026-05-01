"use client"

import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import rehypeHighlight from "rehype-highlight"
import "highlight.js/styles/github.css"
import { getJobFileUrl } from "@/lib/api"
import type { Components } from "react-markdown"

interface MarkdownViewerProps {
  content: string
  jobId?: string
}

function isAbsoluteUrl(src: string) {
  return /^(?:[a-z][a-z\d+.-]*:|\/\/)/i.test(src)
}

function resolveOutputAssetUrl(src: string | undefined, jobId: string | undefined) {
  if (!src || !jobId || isAbsoluteUrl(src) || src.startsWith("#")) {
    return src
  }

  return getJobFileUrl(jobId, src)
}

type MarkdownAstNode = {
  type?: string
  tagName?: string
  children?: unknown[]
}

function isMarkdownAstNode(value: unknown): value is MarkdownAstNode {
  return typeof value === "object" && value !== null
}

function containsImageNode(node: unknown): boolean {
  if (!isMarkdownAstNode(node) || !Array.isArray(node.children)) {
    return false
  }

  return node.children.some(
    (child) =>
      isMarkdownAstNode(child) &&
      child.type === "element" &&
      child.tagName === "img"
  )
}

export function MarkdownViewer({ content, jobId }: MarkdownViewerProps) {
  const components: Components = {
    h1: ({ children, ...props }) => (
      <h1
        className="mb-4 border-b border-border pb-3 text-3xl font-semibold leading-tight text-foreground"
        {...props}
      >
        {children}
      </h1>
    ),
    h2: ({ children, ...props }) => (
      <h2
        className="mb-3 mt-8 border-b border-border pb-2 text-2xl font-semibold leading-snug text-foreground first:mt-0"
        {...props}
      >
        {children}
      </h2>
    ),
    h3: ({ children, ...props }) => (
      <h3 className="mb-2 mt-6 text-xl font-semibold leading-snug text-foreground" {...props}>
        {children}
      </h3>
    ),
    h4: ({ children, ...props }) => (
      <h4 className="mb-2 mt-5 text-lg font-semibold leading-snug text-foreground" {...props}>
        {children}
      </h4>
    ),
    p: ({ children, node, ...props }) =>
      containsImageNode(node) ? (
        <div className="my-3 text-foreground" {...props}>
          {children}
        </div>
      ) : (
        <p className="my-3 leading-8 text-foreground" {...props}>
          {children}
        </p>
      ),
    a: ({ children, href, ...props }) => (
      <a
        href={href}
        target={href?.startsWith("#") ? undefined : "_blank"}
        rel={href?.startsWith("#") ? undefined : "noopener noreferrer"}
        className="font-medium text-primary underline underline-offset-4"
        {...props}
      >
        {children}
      </a>
    ),
    ul: ({ children, ...props }) => (
      <ul className="my-3 flex list-disc flex-col gap-2 pl-6" {...props}>
        {children}
      </ul>
    ),
    ol: ({ children, ...props }) => (
      <ol className="my-3 flex list-decimal flex-col gap-2 pl-6" {...props}>
        {children}
      </ol>
    ),
    li: ({ children, ...props }) => (
      <li className="pl-1 leading-8 marker:text-muted-foreground" {...props}>
        {children}
      </li>
    ),
    blockquote: ({ children, ...props }) => (
      <blockquote
        className="my-4 border-l-4 border-primary bg-muted px-4 py-3 text-muted-foreground"
        {...props}
      >
        {children}
      </blockquote>
    ),
    hr: (props) => <hr className="my-6 border-border" {...props} />,
    img: ({ src, alt, node: _node, ...props }) => {
      void _node
      const resolvedSrc = resolveOutputAssetUrl(typeof src === "string" ? src : undefined, jobId)

      return (
        <figure className="my-5">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={resolvedSrc}
            alt={alt ?? ""}
            loading="lazy"
            className="mx-auto max-h-[520px] w-auto max-w-full rounded-md border border-border bg-muted object-contain"
            {...props}
          />
          {alt ? (
            <figcaption className="mt-2 text-center text-sm text-muted-foreground">
              {alt}
            </figcaption>
          ) : null}
        </figure>
      )
    },
    table: ({ children, ...props }) => (
      <div className="my-5 overflow-x-auto rounded-md border border-border">
        <table className="w-full border-collapse text-sm" {...props}>
          {children}
        </table>
      </div>
    ),
    thead: ({ children, ...props }) => (
      <thead className="bg-muted text-left" {...props}>
        {children}
      </thead>
    ),
    th: ({ children, ...props }) => (
      <th className="border-b border-border px-3 py-2 font-semibold text-foreground" {...props}>
        {children}
      </th>
    ),
    td: ({ children, ...props }) => (
      <td className="border-t border-border px-3 py-2 align-top leading-7" {...props}>
        {children}
      </td>
    ),
    code: ({ children, className, ...props }) => (
      <code
        className={[
          "rounded bg-muted px-1.5 py-0.5 font-mono text-sm text-foreground",
          className,
        ]
          .filter(Boolean)
          .join(" ")}
        {...props}
      >
        {children}
      </code>
    ),
    pre: ({ children, ...props }) => (
      <pre
        className="my-4 overflow-x-auto rounded-md border border-border bg-muted p-4 text-sm leading-7 [&>code]:bg-transparent [&>code]:p-0"
        {...props}
      >
        {children}
      </pre>
    ),
    strong: ({ children, ...props }) => (
      <strong className="font-semibold text-foreground" {...props}>
        {children}
      </strong>
    ),
  }

  return (
    <div className="mx-auto max-w-5xl text-base text-foreground">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight]}
        components={components}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}
