from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .agent import AgentError, OpenAITransport, qualify_lead


def main() -> int:
    parser = argparse.ArgumentParser(description="Qualify one lead and draft a follow-up for human review")
    parser.add_argument("lead", type=Path, help="Path to a JSON lead file")
    args = parser.parse_args()
    try:
        lead = json.loads(args.lead.read_text(encoding="utf-8"))
        result = qualify_lead(lead, OpenAITransport())
    except (OSError, ValueError, AgentError) as exc:
        print(f"LeadFlow error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
