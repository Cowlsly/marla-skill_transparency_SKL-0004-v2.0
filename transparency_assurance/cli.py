from __future__ import annotations

import argparse
import json
from pathlib import Path

from .repair import boundary_connected_flat_repair
from .validator import inspect_asset, write_report


def main() -> None:
    parser = argparse.ArgumentParser(prog="transparency")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="Validate an asset against a target profile")
    validate.add_argument("asset")
    validate.add_argument("--profile", default="repo-generic")
    validate.add_argument("--json", dest="json_path")

    repair = sub.add_parser("repair", help="Conservatively repair a flat boundary-connected background")
    repair.add_argument("asset")
    repair.add_argument("--output", required=True)
    repair.add_argument("--tolerance", type=float, default=18.0)

    args = parser.parse_args()

    if args.command == "validate":
        report = inspect_asset(args.asset, args.profile)
        if args.json_path:
            write_report(report, args.json_path)
        print(json.dumps(report, indent=2, sort_keys=True))
        raise SystemExit(0 if report.get("target_compliant") else 2)

    if args.command == "repair":
        result = boundary_connected_flat_repair(args.asset, args.output, args.tolerance)
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
