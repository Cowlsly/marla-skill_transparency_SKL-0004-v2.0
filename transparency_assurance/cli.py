from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image

from .composite import DEFAULT_BACKGROUNDS, make_contact_sheet
from .profiles import PROFILES
from .repair import boundary_connected_flat_repair
from .validator import inspect_asset, write_report


def main() -> None:
    parser = argparse.ArgumentParser(prog="transparency")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="Validate an asset against a target profile")
    validate.add_argument("asset")
    validate.add_argument("--profile", default="repo-generic", choices=sorted(PROFILES))
    validate.add_argument("--json", dest="json_path")

    attest = sub.add_parser("attest", help="Write a machine-readable QA attestation")
    attest.add_argument("asset")
    attest.add_argument("--profile", default="repo-generic", choices=sorted(PROFILES))
    attest.add_argument("--json", dest="json_path", required=True)

    sheet = sub.add_parser("contact-sheet", help="Create linear-light QA composites on contrasting backgrounds")
    sheet.add_argument("asset")
    sheet.add_argument("--output", required=True)

    repair = sub.add_parser("repair", help="Conservatively repair a flat boundary-connected background")
    repair.add_argument("asset")
    repair.add_argument("--output", required=True)
    repair.add_argument("--tolerance", type=float, default=18.0)

    profiles = sub.add_parser("profiles", help="List built-in target profiles")

    args = parser.parse_args()

    if args.command == "validate":
        report = inspect_asset(args.asset, args.profile)
        if args.json_path:
            write_report(report, args.json_path)
        print(json.dumps(report, indent=2, sort_keys=True))
        raise SystemExit(0 if report.get("target_compliant") else 2)

    if args.command == "attest":
        report = inspect_asset(args.asset, args.profile)
        write_report(report, args.json_path)
        print(json.dumps({"attestation": args.json_path, "target_compliant": report.get("target_compliant")}, indent=2))
        raise SystemExit(0 if report.get("target_compliant") else 2)

    if args.command == "contact-sheet":
        with Image.open(args.asset) as im:
            output = make_contact_sheet(im, DEFAULT_BACKGROUNDS, args.output)
        print(json.dumps({"contact_sheet": str(output), "backgrounds": [name for name, _ in DEFAULT_BACKGROUNDS]}, indent=2))
        return

    if args.command == "repair":
        result = boundary_connected_flat_repair(args.asset, args.output, args.tolerance)
        print(json.dumps(result, indent=2, sort_keys=True))
        return

    if args.command == "profiles":
        print(json.dumps({name: {"transparency": p.transparency.value, "width": p.width, "height": p.height, "max_bytes": p.max_bytes, "notes": p.notes} for name, p in sorted(PROFILES.items())}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
