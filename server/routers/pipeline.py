"""Job store and pipeline orchestration for the Weave API server."""

import json
import queue
import shutil
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse

from ..models import JobCreateResponse, JobResultResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])

# ---------------------------------------------------------------------------
# Project paths (resolved relative to this file → server/ → project root)
# ---------------------------------------------------------------------------
_SERVER_DIR = Path(__file__).parent.parent          # server/
_PROJECT_ROOT = _SERVER_DIR.parent                   # Weave/
_OUTPUT_ROOT = _PROJECT_ROOT / "output"
_JOB_DATA_ROOT = _SERVER_DIR / "job_data"            # server/job_data/


# ---------------------------------------------------------------------------
# In-memory job store
# ---------------------------------------------------------------------------

@dataclass
class JobState:
    job_id: str
    status: str = "pending"          # pending | running | complete | error
    input_dir: Path = field(default_factory=Path)
    temp_dir: Path = field(default_factory=Path)
    output_dir: Path | None = None
    output_dir_name: str = ""
    params: Any = None
    event_queue: queue.Queue = field(default_factory=queue.Queue)
    thread: threading.Thread | None = None


_jobs: dict[str, JobState] = {}


# ---------------------------------------------------------------------------
# Pipeline orchestration (runs in a background thread)
# ---------------------------------------------------------------------------

def _run_pipeline_thread(job: JobState) -> None:
    """Execute the Weave pipeline in a worker thread, emitting SSE events."""

    def emit(event_type: str, step: str, detail: str = "") -> None:
        job.event_queue.put({"type": event_type, "step": step, "detail": detail})

    try:
        # ----------------------------------------------------------------
        # Lazy imports – weave package must be installed in the same venv
        # ----------------------------------------------------------------
        from datetime import datetime as dt

        from weave.ai import (
            cleanup_uploaded_files,
            create_provider,
            expand_all_chapters,
            generate_outline,
            parse_outline_chapters,
            upload_images,
        )
        from weave.config import PipelineConfig
        from weave.converter import convert_pdfs_to_images, ensure_directories
        from weave.export import convert_to_pdf, post_process

        # ----------------------------------------------------------------
        # Build output dir (mirrors run_pipeline logic)
        # ----------------------------------------------------------------
        timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
        output_dir = _OUTPUT_ROOT / timestamp
        job.output_dir = output_dir
        job.output_dir_name = timestamp

        config = PipelineConfig(
            input_dir=job.input_dir,
            output_dir=output_dir,
            temp_dir=job.temp_dir,
            provider=job.params.get("provider", "gemini"),
            model=job.params["model"],
            api_key=job.params["api_key"],
            language=job.params["language"],
            keep_temp=False,
            outline_only=False,
            pdf=job.params["export_pdf"],
        )

        ensure_directories(config)

        # ----------------------------------------------------------------
        # Step 1 — PDF → Images
        # ----------------------------------------------------------------
        emit("progress", "converting", "轉換 PDF 為圖片中...")
        image_filenames = convert_pdfs_to_images(config)
        emit("progress", "converting_done", f"已轉換 {len(image_filenames)} 頁投影片")

        # ----------------------------------------------------------------
        # Step 2 — Upload / prepare images via the selected provider
        # ----------------------------------------------------------------
        emit("progress", "uploading", f"準備圖片（{config.provider}）...")
        provider = create_provider(config.provider, config.api_key)
        uploaded_files = upload_images(provider, image_filenames, config)
        emit("progress", "uploading_done", f"已處理 {len(uploaded_files)} 個圖片")

        try:
            # ----------------------------------------------------------------
            # Step 3 — Pass 1: Generate outline
            # ----------------------------------------------------------------
            emit("progress", "outline", "分析講義結構（Pass 1）...")
            outline = generate_outline(provider, uploaded_files, image_filenames, config)
            emit("progress", "outline_done", "大綱生成完成")

            # ----------------------------------------------------------------
            # Step 4 — Parse chapters
            # ----------------------------------------------------------------
            chapters = parse_outline_chapters(outline)
            if not chapters:
                chapters = [
                    {
                        "title": "# Complete Handout",
                        "outline_section": outline,
                        "pages": image_filenames,
                    }
                ]
            total_chapters = len(chapters)

            # ----------------------------------------------------------------
            # Step 5 — Pass 2: Expand chapters
            # ----------------------------------------------------------------
            emit("progress", "expanding", f"展開 {total_chapters} 個章節（Pass 2）...")
            completed_count: list[int] = [0]

            def on_chapter_done(idx: int, content: str) -> None:
                completed_count[0] += 1
                emit(
                    "progress",
                    "chapter_done",
                    f"章節 {completed_count[0]}/{total_chapters} 完成",
                )

            full_markdown = expand_all_chapters(
                provider,
                chapters,
                outline,
                uploaded_files,
                config,
                on_chapter_done=on_chapter_done,
            )

            # ----------------------------------------------------------------
            # Step 6 — Post-processing
            # ----------------------------------------------------------------
            emit("progress", "postprocess", "後處理與整合...")
            post_process(full_markdown, image_filenames, config)

        except Exception:
            cleanup_uploaded_files(provider, uploaded_files)
            raise

        # Clean up uploaded files
        cleanup_uploaded_files(provider, uploaded_files)

        # ----------------------------------------------------------------
        # Step 7 — PDF export (optional)
        # ----------------------------------------------------------------
        if config.pdf:
            emit("progress", "pdf_export", "匯出 PDF...")
            convert_to_pdf(config)
            emit("progress", "pdf_done", "PDF 匯出完成")

        # ----------------------------------------------------------------
        # Done
        # ----------------------------------------------------------------
        job.status = "complete"
        emit("complete", "done", timestamp)

    except Exception as exc:  # noqa: BLE001
        job.status = "error"
        emit("error", "error", str(exc))

    finally:
        # Always clean up per-job temp data
        if job.temp_dir.exists():
            shutil.rmtree(str(job.temp_dir), ignore_errors=True)
        if job.input_dir.exists():
            shutil.rmtree(str(job.input_dir), ignore_errors=True)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("", response_model=JobCreateResponse, status_code=201)
async def create_job(
    files: list[UploadFile] = File(..., description="One or more PDF files"),
    params: str = Form(..., description="JSON string of JobCreateParams"),
) -> JobCreateResponse:
    """Upload PDFs and start a conversion job. Returns a job_id immediately."""

    # Parse params JSON
    try:
        params_dict = json.loads(params)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid params JSON: {exc}") from exc

    required = {"model", "api_key", "language", "export_pdf"}
    if missing := required - params_dict.keys():
        raise HTTPException(status_code=422, detail=f"Missing params fields: {missing}")

    # Validate files
    if not files:
        raise HTTPException(status_code=422, detail="At least one PDF file is required.")
    for f in files:
        if f.content_type not in ("application/pdf", "application/octet-stream"):
            if not (f.filename or "").lower().endswith(".pdf"):
                raise HTTPException(
                    status_code=422,
                    detail=f"File '{f.filename}' does not appear to be a PDF.",
                )

    # Create job
    job_id = str(uuid.uuid4())
    input_dir = _JOB_DATA_ROOT / job_id / "input"
    temp_dir = _JOB_DATA_ROOT / job_id / "temp"
    input_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Save uploaded PDFs
    for upload in files:
        filename = upload.filename or f"slide_{uuid.uuid4().hex[:8]}.pdf"
        safe_name = Path(filename).name  # strip any path components
        dest = input_dir / safe_name
        content = await upload.read()
        dest.write_bytes(content)

    job = JobState(
        job_id=job_id,
        status="running",
        input_dir=input_dir,
        temp_dir=temp_dir,
        params=params_dict,
    )
    _jobs[job_id] = job

    # Start background thread
    thread = threading.Thread(target=_run_pipeline_thread, args=(job,), daemon=True)
    thread.start()
    job.thread = thread

    return JobCreateResponse(job_id=job_id)


@router.get("/{job_id}/stream")
async def stream_job(job_id: str) -> StreamingResponse:
    """SSE endpoint — streams progress events until job completes or errors."""

    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found.")

    job = _jobs[job_id]

    async def event_generator():
        # If job already finished before the client connects, emit final state
        if job.status == "complete":
            payload = json.dumps(
                {"type": "complete", "step": "done", "detail": job.output_dir_name},
                ensure_ascii=False,
            )
            yield f"data: {payload}\n\n"
            return
        if job.status == "error":
            # Drain any error event from queue
            try:
                ev = job.event_queue.get_nowait()
                payload = json.dumps(ev, ensure_ascii=False)
                yield f"data: {payload}\n\n"
            except queue.Empty:
                payload = json.dumps(
                    {"type": "error", "step": "error", "detail": "Unknown error"},
                    ensure_ascii=False,
                )
                yield f"data: {payload}\n\n"
            return

        import asyncio

        while True:
            try:
                event = job.event_queue.get_nowait()
            except queue.Empty:
                # Keep connection alive
                yield ": keepalive\n\n"
                await asyncio.sleep(0.3)
                continue

            payload = json.dumps(event, ensure_ascii=False)
            yield f"data: {payload}\n\n"

            if event.get("type") in ("complete", "error"):
                break

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{job_id}/result", response_model=JobResultResponse)
async def get_job_result(job_id: str) -> JobResultResponse:
    """Return the generated Markdown and metadata once a job is complete."""

    job = _jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.status != "complete":
        raise HTTPException(status_code=409, detail=f"Job is not complete (status: {job.status}).")

    md_path = job.output_dir / "handout.md"
    if not md_path.exists():
        raise HTTPException(status_code=500, detail="handout.md not found in output.")

    markdown = md_path.read_text(encoding="utf-8")
    has_pdf = (job.output_dir / "handout.pdf").exists()

    return JobResultResponse(
        markdown=markdown,
        output_dir_name=job.output_dir_name,
        has_pdf=has_pdf,
    )


@router.get("/{job_id}/download/{file_type}")
async def download_file(job_id: str, file_type: str) -> FileResponse:
    """Download handout.pdf or handout.md from a completed job."""

    job = _jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.status != "complete":
        raise HTTPException(status_code=409, detail="Job is not complete yet.")

    if file_type == "pdf":
        path = job.output_dir / "handout.pdf"
        media = "application/pdf"
        filename = "handout.pdf"
    elif file_type == "markdown":
        path = job.output_dir / "handout.md"
        media = "text/markdown; charset=utf-8"
        filename = "handout.md"
    else:
        raise HTTPException(status_code=404, detail=f"Unknown file type: {file_type}")

    if not path.exists():
        raise HTTPException(status_code=404, detail=f"{filename} not found.")

    return FileResponse(path=str(path), media_type=media, filename=filename)


@router.get("/{job_id}/files/{file_path:path}")
async def serve_output_file(job_id: str, file_path: str) -> FileResponse:
    """Serve arbitrary files from a job's output directory (e.g. images)."""

    job = _jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.output_dir is None:
        raise HTTPException(status_code=409, detail="Job output not ready.")

    # Prevent path traversal
    target = (job.output_dir / file_path).resolve()
    if not target.is_relative_to(job.output_dir.resolve()):
        raise HTTPException(status_code=403, detail="Access denied.")

    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="File not found.")

    return FileResponse(path=str(target))
