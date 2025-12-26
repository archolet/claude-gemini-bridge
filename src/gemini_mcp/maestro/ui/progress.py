"""
Progress Indicator - Visual progress bars for MAESTRO.

Provides text-based progress indicators for:
- Interview flow (questions answered / total)
- Execution stages (agents, validation, completion)
"""
from __future__ import annotations

from typing import Any


def generate_progress_bar(
    progress: float,
    width: int = 30,
    filled_char: str = "█",
    empty_char: str = "░",
) -> str:
    """
    Generate a text-based progress bar.

    Args:
        progress: Progress value between 0.0 and 1.0
        width: Bar width in characters (default: 30)
        filled_char: Character for filled portion
        empty_char: Character for empty portion

    Returns:
        Formatted progress bar string with percentage
    """
    # Clamp progress to valid range
    progress = max(0.0, min(1.0, progress))

    filled = int(progress * width)
    empty = width - filled
    bar = f"{filled_char * filled}{empty_char * empty}"
    percent = int(progress * 100)
    return f"[{bar}] %{percent}"


def generate_interview_progress(
    current_step: int,
    total_steps: int,
    current_category: str = "",
) -> dict[str, Any]:
    """
    Generate interview progress indicator.

    Args:
        current_step: Current question number (1-based)
        total_steps: Total expected questions
        current_category: Current question category (optional)

    Returns:
        Dict with progress data and formatted display
    """
    progress = current_step / total_steps if total_steps > 0 else 0.0

    return {
        "type": "interview_progress",
        "current_step": current_step,
        "total_steps": total_steps,
        "progress": round(progress, 2),
        "progress_bar": generate_progress_bar(progress),
        "current_category": current_category,
        "message": f"Soru {current_step}/{total_steps}",
    }


def generate_execution_progress(
    stage: str,
    stage_progress: float = 0.0,
) -> dict[str, Any]:
    """
    Generate execution progress indicator.

    Tracks progress through Trifecta pipeline stages:
    1. Başlatılıyor (Initializing)
    2. Agent'lar Çalışıyor (Agents Running)
    3. Doğrulama (Validation)
    4. Tamamlandı (Complete)

    Args:
        stage: Current stage name
        stage_progress: Progress within current stage (0.0-1.0)

    Returns:
        Dict with stage-aware progress data
    """
    stages = ["Başlatılıyor", "Agent'lar Çalışıyor", "Doğrulama", "Tamamlandı"]

    try:
        stage_index = stages.index(stage)
    except ValueError:
        stage_index = 0

    # Calculate overall progress
    overall = (stage_index + stage_progress) / len(stages)

    return {
        "type": "execution_progress",
        "stage": stage,
        "stage_progress": round(stage_progress, 2),
        "overall_progress": round(overall, 2),
        "progress_bar": generate_progress_bar(overall),
        "stages": stages,
        "current_stage_index": stage_index,
        "message": f"{stage} ({int(overall * 100)}%)",
    }


def generate_quality_progress(
    current_score: float,
    target_score: float = 7.0,
    iteration: int = 1,
    max_iterations: int = 3,
) -> dict[str, Any]:
    """
    Generate quality refinement progress indicator.

    Tracks Critic-driven refinement loop progress.

    Args:
        current_score: Current quality score (0-10)
        target_score: Target quality threshold
        iteration: Current iteration number
        max_iterations: Maximum allowed iterations

    Returns:
        Dict with quality progress data
    """
    # Score progress (how close to target)
    score_progress = min(1.0, current_score / target_score)

    # Iteration progress
    iteration_progress = iteration / max_iterations

    # Meeting target?
    meets_target = current_score >= target_score

    return {
        "type": "quality_progress",
        "current_score": round(current_score, 2),
        "target_score": target_score,
        "score_progress": round(score_progress, 2),
        "score_bar": generate_progress_bar(score_progress, width=20),
        "iteration": iteration,
        "max_iterations": max_iterations,
        "iteration_progress": round(iteration_progress, 2),
        "meets_target": meets_target,
        "message": (
            f"Kalite: {current_score:.1f}/{target_score:.1f} "
            f"(İterasyon {iteration}/{max_iterations})"
        ),
        "status_icon": "✅" if meets_target else "🔄",
    }
