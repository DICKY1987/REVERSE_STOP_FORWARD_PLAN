# Supplemental Patch – LangChain/LangGraph Orchestration + GitHub‑Native Identity (GH‑ID + run_ulid)

## 0) Summary
This patch augments the autonomous, GitHub‑centric pipeline by (1) adopting **LangChain/LangGraph** for deterministic orchestration and resilience, and (2) simplifying task identity by replacing `atom_key` with a **GitHub‑native task identifier** while **retaining a single global `run_ulid`** per execution. The result is higher determinism (idempotent keys, immutable anchors), safer concurrency (fan‑out/fan‑in with backpressure), and audit‑grade observability (traceable, replayable, cross‑system).

**Decision:**
- Use **GH task identity** (canonical path) as the task key: `gh://owner/repo/{issues|pulls}/{number}` and optionally `github_node_id`.
- **Keep** a single **`run_ulid`** per orchestrated execution for cross‑tool correlation.
- Introduce **LangGraph StateGraph** for orchestration with checkpointing, interrupts (HITL gates), and concurrency control.

**Non‑Goals:** Replace GitHub as source of truth, change repo layout, or alter CI gates beyond identity/trigger glue.

---

## 1) Scope of Change (What’s Affected)
- **Identity & Ledger**: Replaces `atom_key` with `gh_task_id`; adds standard GH anchors (commit SHA, PR number, workflow run ID). Keeps `run_ulid`.
- **Orchestration**: Planning → Dispatch → Execute/PR → QA → Post‑merge loops move to **LangGraph** with nodes/edges, checkpoints, and interrupts.
- **Eventing/CI**: GitHub events call **graph endpoints** (start/resume/retry) instead of bespoke pollers.
- **Observability**: Standardizes tracing/metrics on **LangSmith‑style traces** tagged with `run_ulid` + GH IDs.
- **Concurrency & Worktrees**: Parallelism managed by **graph fan‑out** keyed by `gh_task_id`, with limits to avoid conflicts.

---

## 2) Identity Model Patch
**Before:** `atom_uid` + `atom_key` (custom).  
**After:**
- **Task key:** `gh_task_id` = `gh://owner/repo/{issues|pulls}/{number}` (+ optional `github_node_id`).
- **Run key:** `run_ulid` (global, time‑sortable; used across traces, CI, artifacts, and ledger).
- **Anchors:** `commit_sha`, `pr_number`, `workflow_run_id`, `workflow_attempt`, `project_item_id` (if Projects used).

**Determinism impacts:**
- Idempotency uses `(gh_task_id, run_ulid)` composite.  
- Immutable references (commit SHA) guarantee reproducible decisions.  
- Cross‑repo uniqueness via canonicalized `gh://…` path (no collisions).

---

## 3) Orchestration Patch (LangGraph)
**Additions:**
- **Nodes** map 1:1 to atomic phases (e.g., intake, planning, dispatch, workspace allocation, execution, PR creation, QA, post‑merge analysis).
- **Edges** implement success/failure branches; **loops** re‑enter planning after merge to maintain the generative cycle.
- **Checkpointing** at node boundaries for crash‑safe resume.
- **Interrupts** at human‑in‑the‑loop gates (maintainer/security review). Graph pauses that branch, persists state; other branches continue.
- **Concurrency** controls per repo/worktree with backpressure to cap PRs in flight.

**Determinism impacts:** repeatable control flow (no ad‑hoc shell sequencing), ordered retries, and guaranteed resume points.

---

## 4) Step‑by‑Step Workflow Deltas (Before → After)
### 4.1 Plan Intake
- **Before:** Custom keying & dedupe; mixed poll/label logic.  
- **After:** Triggered by GitHub event (label, project move). Graph starts with `gh_task_id`; dedupe on `(gh_task_id, run_ulid)`; backlog hygiene improves.

### 4.2 Dispatch & Queueing
- **Before:** Scripting/forking per tool; uneven backpressure.  
- **After:** Graph fan‑out per `gh_task_id` with concurrency limits; queues visible via run state. Deterministic routing by labels (e.g., `aider`, `jules`).

### 4.3 Workspace Allocation (Worktrees)
- **Before:** Ad‑hoc allocation; race potential on branch names.  
- **After:** One worktree per branch keyed by `run_ulid`; naming policy: include `gh_task_id` + `run_ulid` for uniqueness. Conflict risk drops; cleanup is systematic at node exit.

### 4.4 Execution & PR Creation
- **Before:** Tool invocations coupled to scripts; PR linkage sometimes manual.  
- **After:** Execution node emits artifacts labeled with `{commit_sha}-{run_ulid}`; PR auto‑links to issue; `run_ulid` added to PR body/labels for round‑trip correlation.

### 4.5 QA Gates (CI/Checks)
- **Before:** Gates run but correlation inconsistent across retries.  
- **After:** Checks reference `commit_sha` + `run_ulid`; retries are idempotent; failure branches route to fix nodes; approvals resume via interrupt release.

### 4.6 Post‑Merge Regeneration
- **Before:** Push triggers variable follow‑ups; occasional duplicate issues.  
- **After:** Merge event re‑enters analysis node; dedupe guards on `gh_task_id`; new issues are atomic and properly linked.

---

## 5) Ledger & Data Contract Patch
**New/standardized fields (append‑only):**
- `run_ulid` (global run identifier)
- `gh_task_id` (canonical task path)
- `github_node_id` (optional join key)
- `commit_sha`, `pr_number`, `workflow_run_id`, `workflow_attempt`
- `orchestrator_node` (graph node name)
- `checkpoint_id` (last persisted boundary)
- `gate_verdict` (pass/fail/waived), `gate_name`
- `artifacts[]` (URIs stamped with `{commit_sha}-{run_ulid}`)
- `labels[]`, `assignees[]`, `project_item_id` (if used)

**Removed/renamed:**
- `atom_key` → replaced by `gh_task_id`.  
- `atom_uid` → superseded by `run_ulid` (for execution correlation).  

**Determinism impacts:** a single schema across tools/CI; unambiguous joins; stable replay.

---

## 6) Eventing & CI Glue Patch
- **Triggers:** `issues` (labeled/opened/edited), `project_item` moved, `pull_request` (opened/synchronize/closed), `workflow_run` completed.
- **Calls:** Events invoke graph endpoints (start/resume/retry) with `gh_task_id` and generate a `run_ulid` if none supplied.
- **Idempotency:** CI re‑runs attach to the same `(gh_task_id, run_ulid)`; attempts tracked via `workflow_attempt`.
- **Branch protection:** Required checks bind to the PR; approvals release interrupts.

---

## 7) Observability & Forensics Patch
- **Tracing:** Per‑node spans tagged with `run_ulid`, `gh_task_id`, `owner`, `repo`, `issue_or_pr`, `commit_sha`.
- **Dashboards:** Slice by gate, repo, tool, and failure reason; drill‑through links to GitHub PR/Issue.
- **Retention:** Align trace retention with ledger/CI artifacts; redact secrets at source.

---

## 8) Security & Governance Patch
- **Least‑privilege tokens:** Orchestrator reads issues, creates branches/PRs, triggers workflows; tool adapters use scoped tokens.
- **Policy as checks:** Security/lint/test as required checks; waivers captured as interrupt metadata with approver identity & timestamp.
- **Provenance:** Artifact names include `{commit_sha}-{run_ulid}`; PR body contains last orchestrated `run_ulid` and ledger link.

---

## 9) Migration & Rollout Plan
**Phase 0 – Readiness:** finalize identity schema; add PR/Issue metadata blocks; enable graph persistence store; dry‑run traces.

**Phase 1 – Pilot Lane:** one low‑risk lane (docs/lint autofix). Success criteria: stable resume, no duplicate runs, clear traces, PR linkage.

**Phase 2 – Concurrency:** enable worktree fan‑out (2–3 in flight). Success: no conflicts, predictable throughput, bounded queue.

**Phase 3 – HITL Gates:** activate interrupts at review/security; validate pause/resume and waiver recording.

**Phase 4 – Deprecate Two‑ID:** stop emitting `atom_key`; keep `run_ulid`; backfill old ledger entries with `gh_task_id` via join.

**Rollback:** retain legacy scripts; disable graph endpoint triggers; revert identity to legacy mapping if needed.

---

## 10) Risks & Mitigations
- **Orchestrator service dependency:** mitigate with HA/persistence; keep GitHub‑only fallback path.
- **Vendor/tool coupling:** keep adapters thin (MCP/CLI boundaries); document escape hatches.
- **Throughput vs. contention:** cap parallel PRs; shard by repo/component.
- **Cost growth (tokens, runners):** rate‑limit fan‑out; prioritize lanes; enforce timeouts.

---

## 11) Success Metrics (SLOs)
- **Determinism:** 0 duplicate executions per `(gh_task_id, run_ulid)`.
- **Resilience:** ≥ 99% successful resume after failure/restart.
- **Throughput:** +30–50% tasks completed per day at steady error rate.
- **MTTR:** −40% time to recover from failed QA gate.
- **Auditability:** 100% runs reconstructable from ledger + traces with GH links.

---

## 12) Open Questions / Next Actions
- Confirm persistence backend for orchestrator (e.g., SQLite/Postgres/Redis) and retention policy.
- Decide label taxonomy for routing (e.g., `agent:aider`, `agent:jules`, `gate:security`).
- Finalize PR metadata format for embedding `run_ulid` and ledger URI.
- Pilot timeline and owner; readiness checklist sign‑off across Dev/Sec/Ops.

