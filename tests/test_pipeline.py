"""Tests for pipeline resume behavior."""

import json

from weave.config import PipelineConfig
from weave.pipeline import run_pipeline


def _config(tmp_path, resume_dir):
    return PipelineConfig(
        input_dir=tmp_path / "input",
        output_dir=tmp_path / "output",
        temp_dir=tmp_path / "temp",
        api_key="test-key",
        resume_dir=resume_dir,
    )


def _patch_pipeline_success(monkeypatch, calls):
    image_filenames = ["slide_01_page_001.jpg"]
    chapters = [
        {
            "title": "# Chapter",
            "outline_section": "### Section [來源: slide_01_page_001.jpg]",
            "pages": image_filenames,
        }
    ]

    monkeypatch.setattr(
        "weave.pipeline.convert_pdfs_to_images", lambda _config: image_filenames
    )
    monkeypatch.setattr(
        "weave.pipeline.upload_images",
        lambda _client, filenames, _config: {name: object() for name in filenames},
    )
    monkeypatch.setattr(
        "weave.pipeline.create_provider", lambda _provider, _api_key: object()
    )
    monkeypatch.setattr("weave.pipeline.cleanup_uploaded_files", lambda *_args: None)

    def generate_outline(*_args):
        calls.append("generate_outline")
        return "# Chapter\n### Section [來源: slide_01_page_001.jpg]"

    def parse_outline(outline):
        calls.append(("parse_outline", outline))
        return chapters

    def expand_all_chapters(*_args, **_kwargs):
        calls.append("expand_all_chapters")
        return "handout body"

    def post_process(markdown, filenames, config):
        calls.append(("post_process", markdown, filenames))
        config.output_dir.mkdir(parents=True, exist_ok=True)
        (config.output_dir / "handout.md").write_text(markdown, encoding="utf-8")

    monkeypatch.setattr("weave.pipeline.generate_outline", generate_outline)
    monkeypatch.setattr("weave.pipeline.parse_outline_chapters", parse_outline)
    monkeypatch.setattr("weave.pipeline.expand_all_chapters", expand_all_chapters)
    monkeypatch.setattr("weave.pipeline.post_process", post_process)


def test_resume_without_checkpoint_retries_outline_generation(tmp_path, monkeypatch):
    calls = []
    resume_dir = tmp_path / "run"
    resume_dir.mkdir()
    _patch_pipeline_success(monkeypatch, calls)

    run_pipeline(_config(tmp_path, resume_dir))

    assert "generate_outline" in calls
    assert "expand_all_chapters" in calls
    assert (resume_dir / "handout.md").read_text(encoding="utf-8") == "handout body"


def test_resume_with_outline_but_no_chapters_parses_outline(tmp_path, monkeypatch):
    calls = []
    resume_dir = tmp_path / "run"
    checkpoint_dir = resume_dir / ".checkpoint"
    checkpoint_dir.mkdir(parents=True)
    (checkpoint_dir / "state.json").write_text(
        json.dumps({"outline": "# Saved outline"}, ensure_ascii=False),
        encoding="utf-8",
    )
    _patch_pipeline_success(monkeypatch, calls)

    run_pipeline(_config(tmp_path, resume_dir))

    assert "generate_outline" not in calls
    assert ("parse_outline", "# Saved outline") in calls
    assert "expand_all_chapters" in calls
