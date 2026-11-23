#!/usr/bin/env python3
"""Compare the newest history line per target against the previous one.

Usage: python scripts/check_regressions.py [HISTORY_DIR]
HISTORY_DIR defaults to the history/ directory next to this repo root.
If any target's score dropped by more than 5 points versus its previous
history line, write regression-alert.md (an issue body file) in the
current directory and exit non-zero. Otherwise exit 0.
"""
import json, os, sys

THRESHOLD = 5.0

def load_lines(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows

def check(history_dir, alert_path="regression-alert.md"):
    regressions = []
    if not os.path.isdir(history_dir):
        print(f"history dir not found: {history_dir}")
        return 0
    for name in sorted(os.listdir(history_dir)):
        if not name.endswith(".jsonl"):
            continue
        rows = load_lines(os.path.join(history_dir, name))
        if len(rows) < 2:
            continue
        prev, newest = rows[-2], rows[-1]
        try:
            drop = float(prev["score"]) - float(newest["score"])
        except (KeyError, TypeError, ValueError):
            continue
        if drop > THRESHOLD:
            regressions.append((name[:-len(".jsonl")], prev, newest, drop))
    if regressions:
        lines = ["# AgentOrdeal score regression alert", ""]
        for slug, prev, newest, drop in regressions:
            lines.append(
                f"- **{slug}**: score dropped {drop:.1f} points, "
                f"from {prev.get('score')} (grade {prev.get('grade')}, {prev.get('date')}, battery {prev.get('battery_version')}) "
                f"to {newest.get('score')} (grade {newest.get('grade')}, {newest.get('date')}, battery {newest.get('battery_version')}). "
                f"Citation: {newest.get('citation')}")
        lines.append("")
        lines.append("Threshold: a drop of more than 5 points versus the previous history line.")
        with open(alert_path, "w") as f:
            f.write("\n".join(lines) + "\n")
        print(f"regression detected: wrote {alert_path}")
        for slug, prev, newest, drop in regressions:
            print(f"  {slug}: {prev.get('score')} -> {newest.get('score')} (drop {drop:.1f})")
        return 1
    print("no regressions: no target dropped by more than 5 points")
    return 0

def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    default_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "history")
    history_dir = argv[0] if argv else default_dir
    return check(history_dir)

if __name__ == "__main__":
    raise SystemExit(main())
