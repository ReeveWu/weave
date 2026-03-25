"""Weave.

Transform PDF slides into structured Markdown handouts using AI.
"""

__version__ = "0.1.0"

from .config import PipelineConfig
from .pipeline import run_pipeline

__all__ = ["PipelineConfig", "run_pipeline", "__version__"]
