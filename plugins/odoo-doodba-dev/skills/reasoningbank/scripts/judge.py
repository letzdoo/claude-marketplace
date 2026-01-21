#!/usr/bin/env python3
"""
Judge task trajectories as Success or Failure.

Implements LLM-as-judge from ReasoningBank paper using Claude.
"""

import asyncio
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.utils.config import load_config, get_anthropic_api_key

try:
    from anthropic import AsyncAnthropic
except ImportError:
    print("Error: anthropic package not installed. Run: uv sync", file=sys.stderr)
    sys.exit(1)


JUDGE_PROMPT_TEMPLATE = """You are a strict evaluator for task completion.

Your job is to determine if a task was completed successfully based on the query and the trajectory of actions taken.

Task: {task_query}

Trajectory:
{trajectory_json}

Evaluate if the final state meets the acceptance criteria for the task. Consider:
1. Was the stated goal achieved?
2. Were there any critical errors or failures?
3. Is the final state consistent with success?

Respond with pure JSON in this exact format:
{{
  "label": "Success" or "Failure",
  "confidence": <float between 0 and 1>,
  "reasons": [<list of brief reasons for your judgment>]
}}

Be strict but fair. Partial completion should be considered based on the task's nature.
"""


async def judge_trajectory(
    task_query: str,
    trajectory: Dict[str, Any],
    config = None
) -> Tuple[str, float, list]:
    """
    Judge a task trajectory using Claude.

    Args:
        task_query: The original task query
        trajectory: Trajectory data (steps, messages, tool calls, etc.)
        config: Configuration object

    Returns:
        Tuple of (label, confidence, reasons)
        where label is "Success" or "Failure"
    """
    if config is None:
        config = load_config()

    # Get API key
    api_key = get_anthropic_api_key()

    # Create client
    client = AsyncAnthropic(api_key=api_key)

    # Format trajectory for prompt
    trajectory_json = json.dumps(trajectory, indent=2)

    # Build prompt
    prompt = JUDGE_PROMPT_TEMPLATE.format(
        task_query=task_query,
        trajectory_json=trajectory_json
    )

    # Call Claude
    response = await client.messages.create(
        model=config.judge.model,
        max_tokens=config.judge.max_tokens,
        temperature=config.judge.temperature,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Parse response
    try:
        # Extract text from response
        response_text = response.content[0].text

        # Find JSON in response
        # Sometimes the model wraps it in markdown code blocks
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()

        result = json.loads(response_text)

        label = result.get("label", "Failure")
        confidence = float(result.get("confidence", 0.5))
        reasons = result.get("reasons", [])

        # Validate label
        if label not in ["Success", "Failure"]:
            print(f"Warning: Invalid label '{label}', defaulting to Failure",
                  file=sys.stderr)
            label = "Failure"

        # Clamp confidence
        confidence = max(0.0, min(1.0, confidence))

        return label, confidence, reasons

    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"Error parsing judge response: {e}", file=sys.stderr)
        print(f"Response was: {response_text}", file=sys.stderr)
        # Default to failure with low confidence
        return "Failure", 0.3, ["Failed to parse judge response"]


async def main():
    """CLI entry point for judging trajectories."""
    parser = argparse.ArgumentParser(
        description="Judge task trajectory as Success or Failure"
    )
    parser.add_argument("query", help="Task query text")
    parser.add_argument("trajectory_file", help="JSON file with trajectory data")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")

    args = parser.parse_args()

    # Load trajectory
    with open(args.trajectory_file, 'r') as f:
        trajectory = json.load(f)

    # Judge
    label, confidence, reasons = await judge_trajectory(
        args.query,
        trajectory
    )

    # Output
    if args.json:
        result = {
            "label": label,
            "confidence": confidence,
            "reasons": reasons
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"Judgment: {label}")
        print(f"Confidence: {confidence:.2f}")
        print(f"Reasons:")
        for reason in reasons:
            print(f"  - {reason}")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
