# Planning

You are creating an implementation plan for a software engineering task. You work from research output, gather deep codebase context via Driver MCP, and produce a plan specific enough that an engineer or agent can implement it mechanically — down to the level of specific files, functions, and code changes.

---

## How This Skill Works

1. **Ingest research** — read the research output to understand findings and decisions
2. **Clarify scope** — ask the user what exactly to build, push back on vagueness
3. **Gather broad codebase context** — use `gather_task_context` for architecture and conventions
4. **Detail with primitive tools** — use `get_code_map`, `get_file_documentation`, `get_source_file` for specific file-level understanding
5. **Write the plan** — approach, TDD-ordered task breakdown, acceptance criteria
6. **Self-review** — validate the plan against the actual codebase using Driver tools
7. **Finalize** — user reviews and approves

---

## Step 1: Ingest Research

This skill assumes research has been done. Ask the user to point you to the research output folder.

**Read all research documents:**
- Start with `00-overview.md` for the summary and document index
- Read each numbered deep-dive document for detailed findings
- Note key decisions, open questions, and constraints

If research doesn't exist, tell the user: "This skill works best with research output as input. Want to run the research skill first?"

---

## Step 2: Clarify Scope

With research context loaded, ask the user what they want to build.

**Ask focused questions:**
- Which findings from research do you want to act on?
- What's the desired end state?
- What constraints exist? (timeline, compatibility, dependencies)
- What's explicitly out of scope?

**Push back on scope creep.** If the user says "and also..." that's a signal to split into separate plans. Each plan should deliver one logical unit of work.

---

## Step 3: Gather Broad Codebase Context

### CRITICAL: Use `gather_task_context` — Not Native Agents

`gather_task_context` is Driver MCP's primary tool. **It is your default tool for codebase context.**

**What it does:** It spawns a specialized context agent on Driver's servers that reads pre-computed, exhaustive codebase documentation — architecture overviews, code maps, file-level documentation, changelogs — and does live runtime analysis. It then synthesizes everything into task-specific dynamic context: relevant architecture, key files, conventions, and suggested approaches.

**How to call it for planning:** Provide a task description focused on what you're about to plan. Include architectural concerns and testing patterns.

```
Example task description:
"Planning implementation of retry logic for the notification delivery
system. Need to understand: current delivery pipeline architecture,
error handling patterns, queue configuration, existing retry mechanisms
elsewhere in the codebase, and testing patterns/frameworks used."
```

**It takes 1-3 minutes. This is expected and normal.** The tool is doing work that would take you just as long or longer to do iteratively with native tools — and it produces higher-quality dynamic context because it works from pre-computed, exhaustive documentation rather than raw source files. Wait for the full response.

### CRITICAL: Do NOT Substitute Native Agents

**Do NOT use native Explore agents, subagents, or manual file-reading/grep as a substitute for `gather_task_context`.** These native tools work from raw source only. `gather_task_context` has access to pre-computed documentation that covers architecture, symbol-level details, development history, and conventions — dynamic context that native tools cannot replicate.

---

## Step 4: Detail with Primitive Driver MCP Tools

After `gather_task_context` gives you the broad picture, drill into specifics using Driver's primitive tools. **This step is essential for reaching code-level plan specificity.**

### `get_code_map`
Navigate codebase structure. Use this to:
- Find the exact directories and files the plan will touch
- Understand how code is organized around the area you're modifying
- Verify that files referenced in research still exist and are in expected locations

### `get_file_documentation`
Get symbol-level documentation for specific files. Use this to:
- Understand function signatures, types, classes, and interfaces in files the plan will modify
- Identify the exact methods to extend or modify
- Understand a file's public API without reading every line of source

### `get_source_file`
Read the actual source code. Use this to:
- See exact current implementation when the plan needs to prescribe specific code changes
- Understand control flow, error handling patterns, and edge cases
- Get the precise code context needed to write accurate task specifications

**The progression is: `gather_task_context` (broad) → `get_code_map` (navigate) → `get_file_documentation` (interfaces) → `get_source_file` (implementation).** You won't always need all four, but the plan should be specific enough that you've used at least the first three.

---

## Step 5: Write the Plan

Write the plan to a file. **Never write plan content only in chat.**

### Output Structure

```
plan-output/
├── 00-overview.md      # Index (only if multiple plans)
├── 01-<name>.md        # The plan
└── ...                 # Additional plans if needed (usually just 1)
```

### Plan Document Template

```markdown
# Plan: <name>

## Context
_Summary from research — problem statement, scope, key decisions_

## Architecture Fit
_Existing patterns to follow, with specific file paths from Driver context_
_Directories and files this plan touches_
_Integration points with existing code_

## Acceptance Criteria
- [ ] Criterion 1 (specific, testable)
- [ ] Criterion 2

## Test Strategy

### Testing Patterns
_Testing framework, file organization, and conventions discovered via Driver_

### Unit Tests
- [ ] Test: `<test_name>` — verifies <specific behavior>

### Integration Tests
- [ ] Test: `<test_name>` — verifies <specific behavior>

## Implementation Approach
_High-level approach, key design decisions, rationale_

## Scope
**In scope (explicitly requested):** ...
**In scope (surfaced during planning):** ...
**Out of scope (deferred):** ...

## Constraints
- <specific, actionable constraints — not generic advice>

## Task Breakdown

### Task 1: Write tests for <component>
**Goal**: Define test expectations (TDD red phase)
**Files**: `path/to/test_file.py` (create)
**Tests**: <specific test cases from Test Strategy>
**Constraints**: Tests should fail initially — implementation comes in Task 2

### Task 2: Implement <component>
**Goal**: Make Task 1 tests pass (TDD green phase)
**Files**: `path/to/source_file.py` (modify — add `function_name` method to `ClassName`)
**Tests**: Task 1 tests should now pass
**Constraints**: Follow patterns from `path/to/existing_similar.py`
```

### TDD Task Ordering

**Always order test tasks before implementation tasks.**

```
WRONG:
  Task 1: Implement retry logic
  Task 2: Write tests for retry logic

RIGHT:
  Task 1: Write tests for retry logic (TDD red phase)
  Task 2: Implement retry logic (TDD green phase — make Task 1 tests pass)
```

### Code-Level Specificity

Each task must prescribe concrete changes — not hand-wavy descriptions:

**Too vague:** "Implement the notification handler"

**Specific enough:** "Add `retry_delivery` method to `NotificationService` in `backend/services/notification_service.py`. Method should accept a `notification_id: str` and `attempt: int`, look up the notification from the database using the existing `get_notification` method, and re-enqueue it via `delivery_queue.enqueue()` with exponential backoff. Follow the retry pattern in `backend/services/email_service.py:retry_send`."

This level of detail comes from Step 4 — using Driver's primitive tools to understand the exact files, functions, and patterns involved.

### Explicit Constraints

Be specific. Generic advice is not a constraint.

| Good Constraint | Bad Constraint |
|----------------|---------------|
| "Follow error handling pattern in `src/errors.ts`" | "Write good error handling" |
| "NO TODOs or stubbed functions" | "Write complete code" |
| "Run `pytest backend/tests/` after every change" | "Run tests" |
| "All new functions must have type hints" | "Follow best practices" |

---

## Step 6: Self-Review

After drafting the plan, validate it against the actual codebase. **This step is required, not optional.**

### Big-Picture Check
Call `gather_task_context` with a task description focused on validating the plan:

```
Example:
"Reviewing a plan to add retry logic to the notification delivery system.
Need to verify: Does the planned approach fit the codebase's architecture
and conventions? Are there existing patterns we should follow that the plan
might be missing? Any concerns about the approach?"
```

### Specific Checks
Use primitive tools to verify concrete plan details:

- **`get_code_map`** — do the files and directories referenced in the plan actually exist?
- **`get_file_documentation`** — do the interfaces and function signatures the plan depends on match reality?
- **`get_source_file`** — do the implementation details the plan assumes still hold?

### Report Findings
Tell the user what you found:
- Confirmed: what matches
- Discrepancies: what doesn't match (with specifics)
- Suggestions: adjustments to the plan based on what you discovered

Update the plan to address any discrepancies before the user reviews it.

---

## Step 7: Finalize

Present the plan to the user for review.

- "The plan is at `plan-output/01-<name>.md`. I've validated it against the codebase — [summary of self-review findings]."
- Address any questions or change requests
- The user decides when the plan is ready — do not push to move on

---

## Using `driver-rp`

`driver-rp` is a small CLI that creates and validates planning artifacts with structured frontmatter. **Use it to create every plan and task** rather than hand-writing markdown files. The frontmatter is what makes plans queryable, what powers `driver-rp validate`, and what the dry-run loop (next section) reads to merge mechanical and judgment gaps.

If `driver-rp` is not installed, install it once: `uv tool install driver-rp` (or `uvx driver-rp <command>` for one-off invocations). The research skill covers `driver-rp init` and the research/decision artifact commands; this section assumes you are working inside an existing feature directory created by `driver-rp init`.

### Create a plan

```
driver-rp add plan 01-retry-logic
```

Creates `plans/01-retry-logic/plan.md` with valid frontmatter and a stub heading. Note the **directory layout**: each plan is its own directory containing `plan.md`. Tasks live as sibling files under `plans/01-retry-logic/tasks/`. This layout is required for `add task` to find the plan.

Edit `plans/01-retry-logic/plan.md` to flesh out the sections from the plan template above (Context, Architecture Fit, Acceptance Criteria, Test Strategy, Implementation Approach, Scope, Constraints, Task Breakdown).

### Create tasks under a plan

```
driver-rp add task 01-retry-logic "Write tests for retry_delivery"
driver-rp add task 01-retry-logic "Implement retry_delivery method"
```

Each call creates the next numbered task file under `plans/01-retry-logic/tasks/` (e.g., `t01-write-tests-for-retry-delivery.md`, `t02-implement-retry-delivery-method.md`) with valid frontmatter. The first argument is the plan name; the second is the task title.

Pass `--no-extract` to skip code-reference extraction when creating scaffolding tasks: `driver-rp add task 01-retry-logic "Scratchpad" --no-extract`. By default, `add task` extracts code references from the task body and stores them in the task frontmatter so the dry-run loop can verify them against Driver MCP.

### Task IDs are always `<plan-name>/<task-basename>`

Every task-addressed CLI command (`task get`, `complete`, `refs extract`, `refs verify`) requires the **full** task ID:

```
driver-rp task get 01-retry-logic/t01-write-tests-for-retry-delivery
driver-rp complete 01-retry-logic/t01-write-tests-for-retry-delivery
```

**Bare basenames are rejected** with an "ambiguous task id" error. The `<plan-name>/` prefix is mandatory because the same task basename can exist under multiple plans. Use the full form in every example you write into a plan body, every CLI invocation, and every reference in a SKILL.md.

### Find what to work on next

```
driver-rp next            # all unblocked tasks across all plans
driver-rp next --plan 01-retry-logic  # only this plan
```

Returns tasks whose `depends_on` chain is satisfied. Output is human-readable by default; pass `--json` for structured output suitable for piping into a planning agent.

### Validate before declaring planning complete

```
driver-rp validate                    # all artifacts under the feature root
driver-rp validate --plan 01-retry-logic  # only this plan and its tasks
```

Walks every artifact and checks that:
- Frontmatter parses cleanly under the schema
- Required fields are present
- Round-trip is byte-stable (no silent drift)
- Cross-references resolve (`depends_on`, `consumes`/`provides`)
- Code references in task bodies are syntactically extractable (mechanical pass only — semantic verification against Driver MCP is the dry-run loop's job)

A clean `validate` exit is part of "the plan is ready for dry-run." Run it after every `add task` batch.

### Inspect feature state

```
driver-rp status
```

Reports the current feature phase, plan progress, and any pending deviations. Useful as a sanity check at the start of a planning session and after every batch of changes.

### Troubleshooting unexpected `stale_reference` gaps

When the dry-run loop reports `stale_reference` gaps you don't expect, use the `refs` debug subgroup to localize the problem:

```
driver-rp refs extract 01-retry-logic/t02-implement-retry-delivery-method
```
Prints the JSON list of code references the extractor found in the task body. Use this to confirm the extractor sees what you think it sees — if a reference you expected is missing, the issue is the extractor (or the way you wrote the reference); if a reference you didn't expect is present, the task body needs cleaning up.

```
driver-rp refs verify 01-retry-logic/t02-implement-retry-delivery-method
driver-rp refs verify --no-cache 01-retry-logic/t02-implement-retry-delivery-method
```
Runs the full verification path against Driver MCP for one task and prints results + gaps as JSON. Add `--no-cache` to bypass the SQLite verification cache and force a fresh MCP call. Use this to confirm whether the issue is MCP connectivity (verification fails) or stale cache state (verification passes with `--no-cache` but fails without).

```
driver-rp refs cache clear
```
Deletes every row from the verification cache. Use this when you've fixed the underlying code and want the next `validate` run to re-verify everything from scratch.

The diagnostic ladder is: **`refs extract`** (is extraction correct?) → **`refs verify --no-cache`** (does the live MCP path agree?) → **`refs cache clear`** (was a stale cache hit hiding the truth?). Walk it in order.

### A typical planning session

```
# 1. (assumed) feature dir already created via 'driver-rp init'
cd retry-logic-feature

# 2. scaffold the plan and its tasks
driver-rp add plan 01-retry-logic
# ... edit plans/01-retry-logic/plan.md to flesh out the template
driver-rp add task 01-retry-logic "Write tests for retry_delivery"
driver-rp add task 01-retry-logic "Implement retry_delivery method"

# 3. validate as you go
driver-rp validate --plan 01-retry-logic

# 4. inspect what's ready
driver-rp next --plan 01-retry-logic

# 5. final pre-handoff check
driver-rp validate
driver-rp status
```

### Anti-patterns specific to `driver-rp`

- **Do NOT** hand-write plans or tasks without `driver-rp add plan` / `add task` — the directory layout matters and frontmatter typos cause silent validation failures later
- **Do NOT** use bare task basenames (e.g., `t01-write-tests`) in CLI invocations or example snippets — always use the full `<plan-name>/<task-basename>` form
- **Do NOT** skip `driver-rp validate` between batches of `add task` calls — drift caught later costs more
- **Do NOT** edit the `type`, `created`, or auto-generated filenames — these are part of the schema contract
- **Do NOT** create a `Decisions` section inside a plan when the decision belongs as a standalone `research/decisions/dNN-*.md` artifact — plans should reference decisions, not embed them

---

## Dry-Run Loop

Before a plan is implemented, dry-run it: walk through the plan as if you were about to implement it, surface every gap (missing context, ambiguous task, broken cross-reference, untestable acceptance criterion), fix the gaps, and re-walk. Repeat until no new gaps appear. **This is the most leverage-positive activity in the planning phase** — gaps caught here cost minutes; gaps caught during implementation cost hours.

The dry-run is a loop with two passes per iteration:

1. **Mechanical pass** — `driver-rp plan validate <name> --json` runs schema, dependency-graph, and code-reference checks against the plan and its tasks. Returns a `GapEnvelope` JSON body with all gaps the CLI can find without reading the prose.
2. **Judgment pass** — you (the agent) read the plan + every task, read the relevant codebase context via `gather_task_context`, and apply the critic prompt (next section) to surface gaps a schema check can't find: vague tasks, missing test strategy, hand-wavy acceptance criteria, contract mismatches between this plan and downstream plans.

The agent merges the two passes and records the iteration:

```
driver-rp plan critique record <name> --iteration N --gaps <merged-gaps.json>
```

This stamps `gap_id`s, deduplicates against the prior iteration's gaps using `(kind, location.section)` as the merge key, and writes `dry-runs/<name>/iteration-NN.md` with the merged gap list and a `converged` flag.

### The loop is agent-driven, not CLI-driven

There is **no `--auto-loop` flag**. The CLI gives you `plan validate` and `plan critique record` as primitives; the loop is this prose. You drive it explicitly:

```
ITERATION = 1
loop:
  # mechanical pass
  mechanical_gaps = run("driver-rp plan validate <name> --json")

  # judgment pass — apply critic prompt to plan + task bodies
  judgment_gaps = critic_prompt(
      plan_body = read("plans/<name>/plan.md"),
      task_bodies = read("plans/<name>/tasks/*.md"),
      codebase_context = gather_task_context("Validating plan <name> ..."),
  )

  # merge + record
  merged = mechanical_gaps + judgment_gaps
  exit_code = run(f"driver-rp plan critique record <name> --iteration {ITERATION} --gaps merged.json")

  if exit_code == 0:   # converged: no new gaps this iteration
      break
  if exit_code == 3:   # HIGH-severity gap encountered, stopping per policy
      stop_and_present_to_user()
  if exit_code == 4:   # iteration cap reached
      stop_and_present_to_user()
  if exit_code == 1:   # continue: fix the gaps in the plan, increment, loop
      apply_fixes_to_plan_and_tasks(merged)
      ITERATION += 1
```

The loop is intentionally a few lines of prose because:

- Different harnesses (Claude Code, Cursor, Continue, Aider) drive agents differently — there is no portable "auto-loop" primitive that works in all of them
- Operators often want to inspect or override between iterations — a CLI mode would hide that
- The agent needs to apply judgment (which gaps to fix vs. defer, when a "fix" really lands) — that judgment is the critic, not a flag

### Exit codes from `plan critique record`

| Exit | Meaning | What the agent does |
|------|---------|---------------------|
| `0` | Converged — no new gaps merged in this iteration | Stop. Plan is dry-run-clean. |
| `1` | New gaps were merged — keep iterating | Fix the gaps in the plan/task files, increment iteration, loop |
| `3` | A HIGH-severity gap was recorded and the policy says to stop on HIGH | Stop and present to the user; do not auto-fix HIGH gaps |
| `4` | Iteration cap reached (default 5) without convergence | Stop and present to the user; the plan likely needs restructuring, not more iteration |

Treat any exit code other than `0` as a stop point unless your loop pseudocode explicitly handles it. **`1` is the only "continue" code.** Everything else means a human (or the user) needs to look.

### Iteration numbering

Iterations are **1-indexed**. The first run is `--iteration 1`. The CLI rejects `--iteration 0` and rejects gaps in iteration N+1 if iteration N hasn't been recorded. Reports land at `dry-runs/<name>/iteration-01.md`, `iteration-02.md`, etc.

### Stopping criteria — short version

A full breakdown is in the next two sections. The summary:

- **Convergence:** zero new gaps merged in an iteration → stop. `gap_id` is stable across iterations, so a gap that was already present in iteration N - 1 is not "new" in N.
- **Cap:** 5 iterations max, configurable per plan via `dry_run_policy`. After the cap the plan needs human attention.
- **Severity policy:** by default, HIGH-severity gaps halt the loop. The policy is configurable per plan via the `dry_run_policy` field on the plan frontmatter.

### Pre-Plan-05 transition note

The `driver-rp plan validate` and `driver-rp plan critique record` commands are added in Plan 05 of the `research-planning-as-a-product` feature. **Until that ships in `driver-rp ≥ 0.2.0`**, agents drive the loop manually:

- Use the flat `driver-rp validate` (or `driver-rp validate --plan <name>`) for the mechanical pass — it returns the same `GapEnvelope` shape
- Run the critic prompt by hand against the plan body and write the merged gap list into `dry-runs/<name>/iteration-NN.md` directly
- The merge logic, `gap_id` stamping, and convergence check have to be done by the agent in prose

This is friction worth tolerating in the v0.1.0 window because the loop is small. Once `plan validate` / `plan critique record` ship, switch to the CLI-stamped flow — the manual flow is identical in semantics but error-prone in `gap_id` deduplication.

---

## Critic Prompt

<!-- critic_prompt_version: v1 -->

This is the prompt the agent runs during the **judgment pass** of the dry-run loop. It is intentionally specified down to the JSON shape because the loop reads the agent's output programmatically. **Run the prompt verbatim**, do not paraphrase, and do not skip the schema fence — `plan critique record` will reject mis-shaped output.

The HTML comment above this paragraph is a load-bearing version marker. Plan 05's iteration-report writer reads it and stamps the matching version string into the iteration report frontmatter. If you change the prompt body, bump the version (e.g. from v1 to v2) **in that one HTML comment only** — the lint script asserts exactly one occurrence — and add a row to the changelog at the bottom of this section. Iteration reports across versions are not directly comparable.

### The prompt

```
You are critiquing a software-engineering plan you (or another planner) drafted for the dry-run loop. Your job is to find gaps that would block implementation. Be harsh but specific — every gap must cite evidence from the plan itself or from verified codebase context.

INPUT
- plan_body: the full text of plans/<name>/plan.md (frontmatter + body)
- task_bodies: every plans/<name>/tasks/t*.md file (frontmatter + body)
- mechanical_gaps: the GapEnvelope JSON returned by `driver-rp plan validate <name> --json` — the CLI's already-found gaps. Do NOT re-emit these.
- iteration: integer, 1-indexed. Iteration 1 is the first pass.

WHAT TO CHECK (judgment-only — mechanical checks already ran)

1. Missing context. For each task, can a fresh agent execute it without going back to research docs? If a task references "the existing migration pattern" without pointing to a concrete file/function, that is a gap.

2. Unclear instructions. Read each task step. Do you know exactly which file, which function, which line range to edit? "Update the handler" without a specific handler name is a gap.

3. Missing edge cases. For each behavioral change, what fails? Empty input, max size, concurrent access, partial failure? If the plan does not address them, gap.

4. Hidden dependencies. Does any task assume another task's output without declaring `depends_on`? Does any task touch a file another task also touches without coordination? Flag.

5. Test specificity. Each test in the plan: concrete assertion or vague goal? "Test that pagination works" is vague; "Test that fetch_page(0, 10) returns 10 items and fetch_page(1, 10) returns items 11-20" is specific. Flag the vague ones.

6. Architecture concerns. Does the plan introduce a pattern that diverges from existing conventions? Does it add coupling that will be hard to undo? These are HIGH severity — they require user input and stop the loop.

7. Scope understatement. Does any task touch more files than it claims? A 1-line API change might force 5 call-site updates. If task says "update X" but implementation will touch 5 files, flag.

WHAT NOT TO CHECK (the mechanical pass already handled these — do NOT emit duplicate gaps)
- Whether imports / symbols / files actually exist (`stale_reference` from mechanical pass)
- Whether frontmatter is valid (`prerequisite_missing` from mechanical pass)
- Whether `provides` / `consumes` between plans match (`contract_mismatch` from mechanical pass)
- Whether the task dep graph has cycles (`hidden_dependency` from mechanical pass)

If you suspect the mechanical pass missed one of these, emit a `judgment` gap with a clear `evidence` string explaining why the mechanical check did not catch it. Otherwise stay in the judgment lane.

OUTPUT FORMAT

Return a single JSON body. No prose before or after. No markdown code fences. The body MUST match this schema exactly:

{
  "critic_prompt_version": "v1",
  "iteration": <integer>,
  "converged": <boolean>,
  "gaps": [
    {
      "source": "judgment",
      "severity": "low" | "medium" | "high",
      "kind": "missing_context" | "unclear_instructions" | "missing_edge_case" | "hidden_dependency" | "test_not_specific" | "architecture_concern" | "scope_understatement",
      "location": {
        "plan": "<plan-name>",
        "task": "<task-basename>" | null,
        "section": "<see location.section convention table>"
      },
      "summary": "one-line problem statement",
      "detail": "prose explanation",
      "evidence": "quote from the plan or a verified codebase fact",
      "suggested_fix": "what the planner should do (prose, not code)"
    }
  ]
}

Set `converged: true` and `gaps: []` if you find nothing new this pass. Do NOT include `gap_id` (the CLI stamps it deterministically). Do NOT include `status` (defaults to "open"). Do NOT add fields outside this schema — the CLI rejects extras.

LOCATION.SECTION CONVENTION

The `location.section` string must match the conventions below so judgment gaps deduplicate against mechanical gaps with the same target. Mechanical gaps from `driver-rp plan validate` already follow these conventions; you must match them.

| Target | location.section value |
|--------|-----------------------|
| Plan frontmatter field | `frontmatter.<field-name>` (e.g., `frontmatter.depends_on`, `frontmatter.risk_level`) |
| Plan `consumes` entry | `frontmatter.consumes[<index>]` (e.g., `frontmatter.consumes[0]`) |
| Plan `provides` entry | `frontmatter.provides[<index>]` |
| Plan body H2 section | the literal H2 heading (e.g., `"## Test Strategy"`, `"## Acceptance Criteria"`) |
| Task frontmatter field | `frontmatter.<field-name>` (set `location.task` to the task basename) |
| Task body H2 section | the literal H2 heading |
| Cross-task interaction | `cross-task` (set `location.task` to null) |

If a gap is plan-wide and not anchored to a single section, use `"plan-wide"` as the section value.

EXAMPLE RESPONSE (2 gaps — illustrative; do NOT copy verbatim)

{
  "critic_prompt_version": "v1",
  "iteration": 1,
  "converged": false,
  "gaps": [
    {
      "source": "judgment",
      "severity": "low",
      "kind": "test_not_specific",
      "location": {
        "plan": "01-retry-logic",
        "task": "t01-write-tests-for-retry-delivery",
        "section": "## Acceptance Criteria"
      },
      "summary": "Retry-count assertion is not bounded",
      "detail": "Acceptance criterion 'verify retries happen' does not specify how many retries, the backoff schedule, or the failure threshold. A test that calls retry once and asserts the call happened would pass.",
      "evidence": "From t01 body: 'Acceptance: verify that retry_delivery is called when delivery fails.'",
      "suggested_fix": "Replace with: 'verify that retry_delivery is called exactly 3 times with exponential backoff (1s, 2s, 4s) when delivery fails, and that the 4th failure raises DeliveryAbandoned'."
    },
    {
      "source": "judgment",
      "severity": "medium",
      "kind": "hidden_dependency",
      "location": {
        "plan": "01-retry-logic",
        "task": null,
        "section": "cross-task"
      },
      "summary": "Task 3 depends on Task 2's queue refactor but does not declare it",
      "detail": "Task 3 (Wire retry into the delivery worker) reads from delivery_queue.peek_failed(), which Task 2 (Refactor delivery queue interface) introduces. Task 3's depends_on currently lists only Task 1.",
      "evidence": "Task 3 body line 14: 'await delivery_queue.peek_failed(...)'. Task 2 acceptance criterion 4: 'add peek_failed method to DeliveryQueue'.",
      "suggested_fix": "Add 't02-refactor-delivery-queue-interface' to Task 3's depends_on frontmatter list."
    }
  ]
}

INVALID-JSON RETRY PROTOCOL

If your output is not parseable JSON matching the schema above, you will receive ONE retry message: "Your last response was not valid JSON. Re-emit the same content as strict JSON matching the critic prompt schema." Re-emit. If your second response also fails to parse, the loop halts and surfaces the failure to the operator. Two failures in a row means the prompt is under-specified for your model — that is a Plan 04 bug, not your problem to fix at runtime.

SEVERITY POLICY

Each gap's `severity` value drives what the loop does next. The default policy is:

- low: auto-applied by the planner without confirmation
- medium: planner applies the fix, surfaces it to the user for confirmation before writing
- high: loop stops, surfaces the gap to the user for design input

The default is overridable per plan via `dry_run_policy` in plan frontmatter:

  ---
  type: plan
  name: 01-retry-logic
  dry_run_policy:
    low: confirm
    medium: confirm
    high: stop
  ---

Worked example: setting `dry_run_policy: { high: confirm }` (instead of `stop`) means a HIGH gap surfaces to the user but does NOT halt the loop — the user decides whether the fix is in-scope, and if it is, the loop continues. Use this when running a dry-run pass for a plan where some "HIGH" gaps are known design-debate items you want to log without halting.

When `dry_run_policy` is unset in frontmatter, apply the default (low: auto, medium: confirm, high: stop). Honor the policy as-written; do not second-guess it within a single iteration.

STOPPING CRITERIA (short)

- iteration >= 5: stop, regardless of whether converged
- gaps == []: set converged: true; loop exits
- any HIGH gap and policy says stop: loop exits
- otherwise: continue, fix gaps, increment iteration

ANTI-PATTERNS FOR THE CRITIC

- Don't invent new requirements. If the plan doesn't mention a feature, don't critique its absence (unless it is a safety/security concern with evidence).
- Don't over-correct across iterations. If you flagged a gap in iteration 1 and the planner addressed it in iteration 2, don't re-flag the fix as a new gap.
- Don't be vague. "This section needs more detail" is not actionable. "Task 3 references TokenService.rotate() but does not specify the rotation interval — add it" is actionable.
- Don't hunt for perfection. The bar is "implementation-ready," not "elegant."
- Don't echo mechanical gaps. The CLI already found them.
```

### Cross-model expectations

This prompt is designed to produce parseable strict-JSON output on every model in the harness-agnostic target list — Claude Opus 4.6, Claude Sonnet 4.6, Claude Haiku 4.5, GPT-4-class, Gemini Pro, and locally hosted Llama-3-class models. **Claude Haiku 4.5 is the smallest target.** If Haiku consistently fails to produce parseable JSON for a non-trivial plan, the prompt is under-specified — bump to `v2` with tighter examples or move format-critical content from prose to the schema fence.

The cross-model regression test (Plan 04 Task 5 acceptance bar) runs the prompt against at least Haiku and Opus on a frozen golden plan after every prompt change.

### Critic prompt changelog

| Version | Date | Change |
|---------|------|--------|
| v1 | 2026-04-08 | Initial port from `research/03-dry-run-critic.md`. Adds `location.section` convention table, strict-JSON output contract, invalid-JSON retry protocol, `dry_run_policy` wiring, 2-gap example response. |

---

## Stopping Criteria

The dry-run loop has three orthogonal stop conditions. The loop driver (the agent running `## Dry-Run Loop`) checks them in this order, every iteration:

### 1. Convergence (the success path)

After `driver-rp plan critique record` writes iteration N, exit code `0` means **no new gaps were merged in iteration N relative to iteration N-1**. Same gap_id appearing again is not new. Same `(kind, location.section)` mapping to a re-keyed gap_id is also not new — `gap_id` is deterministic from those fields.

When `0` is returned: stop, mark the plan `dry_run_clean` in frontmatter (`status: dry_run_clean`), and proceed to implementation.

**Important:** convergence is "no NEW gaps," not "zero gaps." A plan can converge with a non-empty open-gap list — those remaining gaps are ones the planner has chosen to defer (`status: deferred`) or won't fix (`status: wont_fix`). The loop respects those decisions and does not flag them as un-converged.

### 2. Iteration cap (the "needs human" path)

The cap is **5 iterations** by default. Override per plan in frontmatter:

  ```yaml
  ---
  type: plan
  name: 01-retry-logic
  dry_run_policy:
    iteration_cap: 7
  ---
  ```

Why a cap exists: a non-converging loop usually means the plan needs restructuring, not more iteration. Five passes is enough for a critic to find every gap a critic of its capability can find — if the gap count is still moving after that, the planner is fixing the wrong things or the plan's scope is wrong.

When the cap is hit (exit code `4`): stop. Surface the open-gap list to the user with the message "Dry-run loop hit the iteration cap without converging. Plan likely needs restructuring." Do not silently mark the plan ready.

### 3. Severity policy (the "human design call" path)

Each gap's `severity` triggers loop behavior per the policy. The default policy:

| Severity | Default behavior | Meaning |
|----------|------------------|---------|
| `low` | `auto` | Planner applies the suggested_fix without asking |
| `medium` | `confirm` | Planner applies the fix and surfaces it for user confirmation before writing |
| `high` | `stop` | Loop halts; gap surfaces to the user as a design question |

Override per plan in frontmatter:

  ```yaml
  ---
  type: plan
  name: 01-retry-logic
  dry_run_policy:
    low: auto
    medium: confirm
    high: stop
    iteration_cap: 5
  ---
  ```

Worked example: `dry_run_policy: { high: confirm }` instead of `stop` lets the loop continue past a HIGH gap once the user has decided whether the fix is in-scope. Use this when running a dry-run on a plan with known design-debate items you want logged but not blocking.

When a HIGH gap triggers a stop (exit code `3`): stop, surface the gap, and wait for user input. Do not auto-fix HIGH gaps under any policy — `auto` is rejected by the CLI for `high`.

### Interactions between the three conditions

- The iteration cap **always wins** over convergence — if you hit the cap and gaps remain, the loop is not converged regardless of how few new gaps came in.
- A HIGH stop **always wins** over convergence within the iteration where the HIGH appeared — even if that iteration would have been zero-new-gap otherwise, the HIGH halts the loop and the user must decide before convergence is recognized.
- LOW gaps under `auto` policy never affect the stopping decision — they are silently fixed and the loop continues.
- A plan with status `dry_run_clean` should not be re-run through the loop except after a non-trivial edit. Re-running on an unchanged plan is wasted token spend.

### When to override the defaults

The defaults are conservative on purpose:

- **Tighten** (`{ low: confirm, medium: confirm, high: stop }`) when the plan touches production data, payments, auth, or anything where a wrong auto-fix would be expensive to revert. This is the recommended setting for any plan with `risk_level: high` in its frontmatter.
- **Loosen** (`{ high: confirm }`) only when the user is actively driving the dry-run interactively and wants to triage HIGH gaps inline rather than across sessions.
- **Cap** (`iteration_cap: 3`) when the plan is small and you want a fast fail signal rather than five passes of nothing.

Whatever the policy, the loop must honor it as-written for the entire run. Do not change the policy mid-loop based on what gaps appeared — that hides the convergence signal.

---

## Anti-Patterns

**Do NOT:**
- Use native Explore agents or subagents as a substitute for `gather_task_context`
- Abandon `gather_task_context` if it takes 1-3 minutes — this is expected behavior
- Fall back to `get_architecture_overview` or other tools because `gather_task_context` "seems slow"
- Write plan content only in chat — always write to files
- Skip reading research output before planning
- Write vague task descriptions ("implement the feature")
- Order implementation tasks before test tasks
- Skip the self-review step
- Suggest moving to implementation — the user controls phase transitions

**DO:**
- Call `gather_task_context` with detailed, planning-focused task descriptions
- Wait for the full response — it is doing compressed expert-level codebase analysis
- Use primitive tools (`get_code_map`, `get_file_documentation`, `get_source_file`) to reach code-level specificity
- Write tasks specific enough that an engineer can implement without ambiguity
- Order tests before implementation (TDD)
- Validate the plan against the codebase before presenting to the user
- Include explicit, actionable constraints — not generic advice
