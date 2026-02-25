# GTD Processing Rules

## Dual-Space Axiom

```
Dev-logs [ ]/[x]  =  AI's workspace     → completed in dialogue
Reminders flags   =  Ryan's action list  → completed in physical world
```

- **Reminders = Ryan's attention queue.** Every flagged item is something Ryan personally does.
- **Dev-logs = AI's work queue.** AI tasks live here. Ryan only sees "启动AI做X" as an atomic action.
- These two spaces never merge.

## Flag Rule

- Flag = atomic action = next physical action
- Atomic = can be done in one step, no further decomposition needed
- Flagging requires a due date (deadline or reminder time)
- Flag is a commitment: "I will do this soon"

## Decomposition Rule

- If not completable in one step → decompose
- Each sub-task gets re-evaluated: who does it? atomic?
- Recurse until every leaf node is atomic
- Decompose through dialogue — AI suggests, Ryan confirms

## Role Judgment

| Role | Criteria | Destination |
|------|----------|-------------|
| **Ryan** | Personal: writing, social, decisions, experiences, learning, physical tasks | Reminders flag + due date |
| **AI** | Technical: development, scripts, data processing, automation | Dev-logs task + Reminders "启动AI做X" |
| **Together** | Collaborative: exploration, planning, validating AI output | Reminders with "和AI一起" note |

## Classification

```
Item (any source)
  ├─ Actionable now?
  │   ├─ Yes
  │   │   ├─ Belongs where? (existing project / area / independent / new project)
  │   │   ├─ Who does it? (Ryan / AI / together)
  │   │   └─ Atomic?
  │   │       ├─ Yes → route to correct space
  │   │       └─ No → decompose → re-evaluate each sub-task
  │   │
  │   └─ No
  │       ├─ Incubate (someday/maybe, project seed, half-formed idea)
  │       │   ├─ Cross-domain seed → `03Resources/Seeds/[name].md`
  │       │   └─ Domain-specific idea → `02Areas/[domain]/` as note
  │       │
  │       └─ Reference (pure information, no intent)
  │           └─ Archive to `03Resources/[topic]/`
```

## Project Alignment

When an item matches an existing project or area, **read its current state before deciding**:

1. Read project dev-logs or area CLAUDE.md
2. Determine relationship:
   - **Redundant** — already covered by active Epic → suggest delete
   - **In backlog** — similar item exists → suggest delete or merge
   - **New** — not yet in project scope → suggest adding to backlog or creating task
3. Show Ryan the project context so he can decide

## Routing Actions

Processing an inbox item has two distinct routing actions. Never confuse them:

| Action | When | Operation |
|--------|------|-----------|
| **Move** | Item stays in Reminders but belongs to a different list | `edit <task> --move-to-list <target>` |
| **Graduate** | Item leaves Reminders entirely (→ Context files: Seeds, dev-logs, Resources) | `done <task>` (mark completed in 收集箱) |

- **Move**: the task is still a commitment, just re-categorized. It keeps its identity.
- **Graduate**: the task has been absorbed into Context. Completing it in Reminders means "processed, no longer needs to live here."

## Mapping

- `~/context/01Projects/[name]/` ↔ Reminders list with same name
- `~/context/02Areas/[name]/` ↔ Reminders list with same name
- Reminders "收集箱" = unprocessed inbox
- No matching list → ask Ryan where it belongs
