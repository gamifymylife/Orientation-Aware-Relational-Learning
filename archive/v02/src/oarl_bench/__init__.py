"""Orientation-aware relational learning benchmark."""
from .config import BenchmarkConfig
from .world import RelationalWorld, generate_world
from .runner import run_episode, run_grid

__all__ = ["BenchmarkConfig", "RelationalWorld", "generate_world", "run_episode", "run_grid"]
__version__ = "0.1.0"
