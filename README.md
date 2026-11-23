# AgentOrdeal Leaderboard

The public record of AgentOrdeal benchmark results. AgentOrdeal is a
reproducible benchmark for autonomous agent security: specification
1.0, battery 1.2.0, reference runner `agentordeal` (the agent-ordeal
repository).

**Status: local staging. Nothing in this repository is published yet.**
There are no remotes, no deployed site, and the workflows under
`.github/workflows/` are local files only -- they run nowhere until
this repository is published and they are enabled there.

## Source of truth

`scores.json` is the source of truth. `index.html` is generated from
it by `generate.py` and must never be edited by hand.

Top-level fields: `benchmark`, `spec_version`, `battery_version`,
`methodology`, `tool_version`, `generated`, `note`, `entries`.

Each entry carries the runner leaderboard fields -- `name`, `url`,
`slug`, `status` (`scored` / `unscored`), `score`, `grade`, `citation`,
`version`, `note`, and, for scored entries, `target`, `tool_version`,
`run_date`, and `scorecard` -- plus:

- `battery_version` on every entry (the battery the entry was scored
  under, or the current battery for unscored entries), and
- `categories` on scored entries: the per-category breakdown copied
  from that entry's `scorecard.json` in the runner repository, as a
  mapping of category name to `{score, passed, total}`.

No score is invented: unscored entries have `score: null` and are
listed only in the "Not yet scored" section of the site, never
interleaved with ranked scores.

## How scores flow in

1. Preferred: run the battery in the runner repository and export
   directly in this repository's format:

   ```
   cd agent-ordeal
   python leaderboard/run_leaderboard.py --export ../agentordeal-leaderboard/scores.json
   ```

   `--export PATH` writes the same field shape as `scores.json`
   (including per-category scores read from the generated scorecards)
   after building the leaderboard. Without `--export`, the runner's
   behaviour is unchanged.

2. Or: manually copy a verified run -- the `leaderboard.json` fields
   from a run of `leaderboard/run_leaderboard.py`, plus the
   `categories` object from each scored entry's
   `leaderboard/results/<slug>/scorecard.json`, plus a per-entry
   `battery_version`.

Then append one history line per scored target (see below) and
regenerate the site.

Scores are published only after a pinned-version run and the
maintainer rerun window in the runner's `docs/METHODOLOGY.md`
(critical findings are shared privately first, with a 14-day fix
window).

## Regenerate the site

```
python3 generate.py
```

Stdlib only, no build tools. Running it is idempotent: the output
depends only on `scores.json` and `history/*.jsonl`.

## History format

One file per scored target: `history/<slug>.jsonl`, one JSON object
per line, oldest first:

```json
{"date": "2026-11-23", "score": 91.7, "grade": "A", "battery_version": "1.2.0", "citation": "AgentOrdeal-1.0 / battery=1.2.0 / seed=none / score=91.7", "scorecard": "results/llm-reference/scorecard.json"}
```

Fields: `date` (run date), `score`, `grade`, `battery_version`,
`citation` (full specification citation for that run), `scorecard`
(the scorecard path in the runner repository that produced the run).

`scripts/check_regressions.py` compares the newest line per target
against the previous one:

```
python3 scripts/check_regressions.py history
```

If any target dropped by more than 5 points, it writes
`regression-alert.md` (an issue body file) and exits non-zero;
otherwise it exits 0. It is wired into `.github/workflows/weekly.yml`.

## Scheduled rescoring (workflow files, not enabled)

- `nightly.yml` -- nightly: rescore demo and reference targets,
  append history lines, regenerate the site.
- `weekly.yml` -- weekly: full rescoring of all configured targets,
  plus the regression check above.
- `monthly.yml` -- monthly / on release: full rescoring plus a
  history snapshot under `history/snapshots/`.

All three check out the runner and this repository, install the
runner, run `leaderboard/run_leaderboard.py`, and are commit-free:
results are uploaded as build artifacts for a human to review.
Publishing a score stays a human decision.

## Submit your agent

The intended published flow (not live yet) is the GitHub Action:

```yaml
- uses: agentordeal/action@v1
  with:
    target: "demo-hardened"
    fail-under: "70"
```

See the "Submit your agent" section of `index.html`.
