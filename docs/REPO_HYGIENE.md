# CivForge Repo Hygiene (Borrowed & Adapted from dawsOS Patterns)

**Core Principle**: CivForge and gravity-mosaic (and any governed projects) remain **completely separate**. CivForge provides governance tooling; targets are independent.

## Daily/Pre-Commit Hygiene (dawsOS-style)
- `git status --short` + review untracked/ignored.
- Run `git clean -fdx` (dry first) only on safe paths; never on governed project sources.
- Update .gitignore for any new local state (dbs, logs, build, OS).
- No committing runtime artifacts (use the enhanced .gitignore).
- All changes to governed projects (e.g. gravity-mosaic) go **only** through the strict deploy bridge with literal verification.

## Legacy / Debt Management
- Archive removed features (e.g. _archive/godot-mvp-deprecated) with clear SEPARATION.md and README notes.
- Trim archives of bloat (caches, binaries) before commit.
- Document why legacy was removed (pivot from Godot MVP to FastAPI governance).
- Use receipts/ for audit trail of cleanups.

## Documentation Hygiene
- Keep SEPARATION.md up-to-date as the boundary contract.
- Borrowable patterns in docs/patterns/ for reuse on other projects (interoperable without merging).
- Update README, IMPLEMENTATION_STATUS, planning/ on every major cleanup/push.
- No outdated Godot/MVP references in active docs (only in archive history).

## Separation + Interoperability
- CivForge workspace: governance (core/, backend/, tools/, patterns).
- Governed projects (gravity-mosaic, potentially dawsOS components): stay in their own repos.
- Interop via: CLI, FastAPI endpoints, documented patterns, strict bridges.
- Never mix source trees.

## Verification Before Push
- Run hygiene checks above.
- Confirm no cross-project pollution (find/grep audits).
- `git status` clean.
- Push only after separation and cleanliness verified.

This is adapted from dawsOS repo hygiene (receipt-first, clean boundaries, literal enforcement, generalized patterns) while preserving full separation.
