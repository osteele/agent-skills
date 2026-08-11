#!/usr/bin/env python3
"""Emit one deterministic synthetic training result."""

from __future__ import annotations

import argparse
import json


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--condition", required=True, choices=("true-batch", "accumulated")
    )
    parser.add_argument("--seed", required=True, type=int)
    args = parser.parse_args()

    noise = ((args.seed * 37) % 11 - 5) * 0.001
    condition_effect = 0.004 if args.condition == "accumulated" else 0.0
    result = {
        "condition": args.condition,
        "seed": args.seed,
        "final_validation_loss": round(0.8 + noise + condition_effect, 3),
        "finite": True,
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
