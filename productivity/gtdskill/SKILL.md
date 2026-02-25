---
name: gtdskill
description: "GTD processing engine — the living interface between Ryan's Context workspace (thinking) and macOS Reminders (action). Manages commitments by sensing both spaces, processing items, decomposing tasks, and routing to the correct space. Use when user mentions: (1) inbox/收集箱 processing, (2) task decomposition/next actions, (3) project or area status, (4) GTD review, (5) what to do next, (6) any todo/commitment management. Trigger phrases: '处理收集箱', 'GTD', '分解任务', '下一步行动', 'next action', '回顾', '看看项目', '有什么要做的', '待办', 'process inbox'."
---

# GTD Processing Engine

Manage Ryan's commitments by bridging two spaces: Context (thinking) and Reminders (action).

**Load [references/gtd-rules.md](references/gtd-rules.md) before processing any items.**

## The Two Spaces

```
Dev-logs [ ]/[x]  =  AI's workspace     → tasks completed in dialogue, AI executes
Reminders flags   =  Ryan's action list  → tasks completed in physical world, only Ryan can do
```

These spaces are independent. Never mix them.

Reminders is the confluence of two directions:

```
AI extracts human actions from Context ──→  Reminders  ←── Ryan captures ideas to 收集箱
            (top-down)                                        (bottom-up)
```

## Mapping: Context ↔ Reminders

- `~/context/01Projects/[name]/` ↔ Reminders list with same name
- `~/context/02Areas/[name]/` ↔ Reminders list with same name
- Reminders "收集箱" = GTD Inbox (unprocessed captures)
- 59 Reminders lists already mirror Context structure

## Sensing Both Spaces

```bash
# Reminders side
~/.claude/skills/reminders/scripts/reminders.sh list "收集箱"
~/.claude/skills/reminders/scripts/reminders.sh list "<list-name>"
~/.claude/skills/reminders/scripts/reminders.sh list-lists

# Context side — use Read/Glob/Grep
# ~/context/01Projects/CLAUDE.md — project index
# ~/context/02Areas/CLAUDE.md — area index
# Project details: ~/context/01Projects/[name]/dev-logs/DEVELOPMENT_LOG.md
# Area details: ~/context/02Areas/[name]/CLAUDE.md
```

Load what's relevant to the conversation, not everything.

## Processing an Item

For any item (from inbox or identified from Context):

1. **What is it?** — Actionable / reference material / idea seed / trash
2. **Where does it belong?** — Match to existing project/area, or new
3. **Who does it?** — Ryan (physical world) / AI (dialogue) / together
4. **Atomic?** — Can it be done in one step? If not → decompose

When matching to a project/area, read its current state first (dev-logs or CLAUDE.md) to check if redundant, already in backlog, or genuinely new.

## Routing

| Result | Destination | Command |
|--------|------------|---------|
| Ryan + atomic | Reminders list, flagged + due date | `reminders.sh edit "<title>" --move-to-list "<list>" --flagged --due <date>` |
| Ryan + needs decomposition | Decompose first, then route each sub-task | — |
| AI does it | Dev-logs task + Reminders "启动AI做X" | Write to dev-logs + `reminders.sh edit` |
| Together | Reminders with note + dev-logs if project-related | `reminders.sh edit "<title>" --move-to-list "<list>" --notes "和AI一起做" --flagged --due <date>` |
| Reference material | Context (03Resources or Area) | Create/update file + `reminders.sh delete "<title>"` |
| Redundant | Delete | `reminders.sh delete "<title>"` |

## Reminders Commands

```bash
reminders.sh list "<list-name>"          # list items
reminders.sh add "<title>" --list "<l>"  # add item
reminders.sh edit "<title>" --move-to-list "<list>" --flagged --due <date> --time <HH:MM> --notes "<n>"
reminders.sh delete "<title>"            # delete item
reminders.sh search "<query>"            # search across lists
reminders.sh list-lists                  # list all lists
```

Flag = atomic action = next physical action. Always set a due date when flagging.
