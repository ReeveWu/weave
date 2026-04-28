/**
 * Weave API client — thin wrapper over the FastAPI backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface JobCreateParams {
  provider: string;
  model: string;
  api_key: string;
  language: string;
  export_pdf: boolean;
}

export interface JobCreateResponse {
  job_id: string;
}

export interface JobResultResponse {
  markdown: string;
  output_dir_name: string;
  has_pdf: boolean;
}

export interface SSEProgressEvent {
  type: "progress";
  step: string;
  detail: string;
}

export interface SSECompleteEvent {
  type: "complete";
  step: "done";
  detail: string; // output_dir_name / timestamp
}

export interface SSEErrorEvent {
  type: "error";
  step: "error";
  detail: string;
}

export type SSEEvent = SSEProgressEvent | SSECompleteEvent | SSEErrorEvent;

/** POST /jobs — upload PDFs and start a conversion job. */
export async function createJob(
  files: File[],
  params: JobCreateParams
): Promise<JobCreateResponse> {
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }
  formData.append("params", JSON.stringify(params));

  const res = await fetch(`${API_BASE}/jobs`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail ?? `Server error ${res.status}`);
  }

  return res.json() as Promise<JobCreateResponse>;
}

/** GET /jobs/:id/result — fetch the completed job result. */
export async function getJobResult(jobId: string): Promise<JobResultResponse> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/result`);
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail ?? `Server error ${res.status}`);
  }
  return res.json() as Promise<JobResultResponse>;
}

/** Returns the URL for downloading a file from a completed job. */
export function getDownloadUrl(jobId: string, fileType: "pdf" | "markdown"): string {
  return `${API_BASE}/jobs/${jobId}/download/${fileType}`;
}

/** Returns the URL for a generated output asset from a completed job. */
export function getJobFileUrl(jobId: string, filePath: string): string {
  const normalizedPath = filePath.replace(/^\.?\//, "");
  const encodedPath = normalizedPath.split("/").map(encodeURIComponent).join("/");

  return `${API_BASE}/jobs/${encodeURIComponent(jobId)}/files/${encodedPath}`;
}

/** Returns the SSE stream URL for a job. */
export function getStreamUrl(jobId: string): string {
  return `${API_BASE}/jobs/${jobId}/stream`;
}
