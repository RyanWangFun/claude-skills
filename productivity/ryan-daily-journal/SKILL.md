---
name: ryan-daily-journal
description: Automatically generate Ryan's daily journal by detecting changes in Context system. Use when the user asks to write/generate journal, daily log, or diary for today or any specific date. Analyzes modifications in 01Projects (项目进展) and 02Areas (领域丰富) directories to populate journal template sections.
---

# Ryan Daily Journal

Automate Ryan's daily journaling by detecting and analyzing recent activity in the Context system, then generating structured journal entries based on the journal template.

## Core Workflow

When the user requests a daily journal:

1. **Detect Changes**: Run `detect_changes.py` to find modified markdown files
2. **Analyze Content**: Read and understand the modifications in both Projects and Areas
3. **Generate Entries**: Create journal sections based on the template structure
4. **Present Results**: Format and present the completed journal entry
5. **Save Journal**: Write the journal to the appropriate file path

## Step 1: Detect Recent Changes

The detection script supports three modes for specifying time ranges:

### Mode 1: Hours (Relative Time)

For generating today's journal or recent activity:

```bash
python3 scripts/detect_changes.py --hours 24 --context-path $CONTEXT_PATH
```

### Mode 2: Specific Date

For generating journal for a specific date:

```bash
python3 scripts/detect_changes.py --date 2024-12-03 --context-path $CONTEXT_PATH
```

This will find all files modified on that entire day (00:00 to 23:59).

### Mode 3: Date Range

For generating weekly summaries or multi-day journals:

```bash
python3 scripts/detect_changes.py --start-date 2024-12-01 --end-date 2024-12-03 --context-path $CONTEXT_PATH
```

### Mode 4: Git Enhanced Mode (Recommended for Journal Generation)

**UPDATED**: Enhanced hybrid detection strategy that combines the best of both approaches:

```bash
python3 scripts/detect_changes.py --use-git --date 2025-12-16 --context-path $CONTEXT_PATH
```

**How Git Enhanced Mode Works**:

采用**混合检测策略**：
1. **第一步：时间戳扫描**（保证不漏掉文件）
   - 扫描所有在指定时间段内修改的.md文件
   - 无论文件是否已commit，都能检测到

2. **第二步：Git信息增强**（获取具体改动）
   - 对于在Git仓库中的文件，查找该时间段内的所有相关commits
   - 显示commit messages和变更统计
   - 即使文件已经commit也能看到具体改了什么

**相比纯时间戳模式的优势**:
- ✅ 不仅知道"哪些文件被修改"，还能看到"具体改了什么"
- ✅ 显示commit messages，了解每个改动的意图
- ✅ 即使文件已被commit也能检测到（不会漏掉）
- ✅ 对不在Git仓库中的文件仍然能正常检测

**When to use**:
- ✅ **强烈推荐用于日记生成**（提供最完整的上下文）
- ✅ 特别适合回顾历史日期（昨天、上周等）
- ✅ 适用于混合环境（部分项目有Git，部分没有）

### Common Parameters

- `--context-path PATH`: Path to the Context directory (default: `$CONTEXT_PATH`)
- `--projects-only`: Only scan 01Projects
- `--areas-only`: Only scan 02Areas
- `--use-git`: Enable Git diff mode for precise change detection
- `--output json`: Output in JSON format for programmatic parsing

### Usage Examples

**User says: "帮我写今天的日记"**
→ Use `--use-git --hours 24` (Git Enhanced Mode - 推荐)

**User says: "生成 12月3日的日记"**
→ Use `--use-git --date 2024-12-03` (Git Enhanced Mode - 推荐，能看到具体改动)

**User says: "写昨天的日记"**
→ Calculate yesterday's date and use `--use-git --date YYYY-MM-DD` (Git Enhanced Mode)

**User says: "总结这周的工作"**
→ Use `--use-git --start-date YYYY-MM-DD --end-date YYYY-MM-DD` (Git Enhanced Mode)

**快速对比（不需要详细改动信息）**
→ 去掉 `--use-git` 参数，只用时间戳模式

### Script Behavior

- Scans for `.md` files modified within the specified time window
- Excludes system directories: `node_modules`, `.git`, `.obsidian`, `dist`, `build`
- Excludes the journal output directory: `02Areas/日记/`
- Sorts results by modification time (newest first)

## Step 2: Read and Analyze Modified Files

对每个检测到的文件，按以下步骤处理：

### 2.1 读取文件内容

**始终读取文件内容**，无论是否有 Git 信息：
- 使用检测脚本提供的文件路径
- 理解文件的主题、内容和工作重点
- 了解这个文件是关于什么的

### 2.2 检查 Git 信息

查看检测结果中的 `git_info` 字段：
- 如果 `git_info.commits` 存在且非空 → 有 Git commits
- 如果 `git_info.commits` 为空或不存在 → 没有 Git commits

### 2.3 确定描述方式

**有 Git Commits 的情况**：
- **主线**：使用 commit messages 了解"做了什么"
- **补充**：结合文件内容理解"具体是什么"
- **输出**：基于 commit message 的主题 + 文件内容的细节

示例：
```
Commit: "完成skill系统架构设计"
文件内容: 包括加载流程、文件结构、调用机制
→ 日记写: 完成了skill系统的架构设计，包括加载流程和调用机制
```

**没有 Git Commits 的情况**：
- **依据**：完全基于文件内容
- **描述**：说明在这个项目/领域做了什么工作
- **重点**：描述工作内容，而不是推测今天的变动

示例：
```
文件内容: 心理咨询记录，讨论了自我认知和情绪管理
→ 日记写: 进行了心理咨询，深化了对自我认知的理解，整理了情绪管理方法
```

### 2.4 核心原则

✅ **要做的**：
- 读取所有检测到的文件内容
- 基于文件内容描述你的工作
- 有 Git commits 时以它为主线
- 描述"你在做什么"、"完成了什么"

❌ **不要做的**：
- 推测"今天改了什么"、"新增了什么"
- 臆想变动内容（如果没有 Git 信息）
- 对比文件的历史版本来找差异

## Step 3: Generate Journal Sections

### Template Structure

The journal template is located at `$CONTEXT_PATH/04Archives/template/日记模板 v4.md`

**Key sections to populate:**

```markdown
---
# 项目进展


---
# 领域丰富


---
```

### Writing Guidelines

### 内容生成原则：基于事实，不推测变动

**核心理念**：日记要描述"你在做什么工作"，而不是推测"今天改了什么"。

#### 原则 1: 始终读取文件内容

无论文件是否有 Git commits，都要读取文件来了解：
- 这个文件的主题是什么
- 你在进行什么工作
- 有哪些具体内容和成果

#### 原则 2: 根据 Git 信息决定描述方式

**有 Git Commits**：
```markdown
策略：Commit Message（做了什么）+ 文件内容（具体是什么）

示例：
检测到: 01Projects/信息获取/架构设计.md
Git commits:
  - "重构API调用层"
  - "添加缓存机制"
文件内容: 包含新的API架构图、缓存策略说明

日记写：
## 信息获取 [[01Projects/信息获取/架构设计.md]]
- 重构了API调用层，优化了接口设计
- 添加了缓存机制，提升了响应速度
- 完善了架构文档和缓存策略
```

**没有 Git Commits**：
```markdown
策略：完全基于文件内容描述工作

示例：
检测到: 02Areas/个人成长/阅读笔记.md
Git commits: 无
文件内容: 包含《原则》一书的读书笔记，重点是决策框架

日记写：
## 个人成长 [[02Areas/个人成长/阅读笔记.md]]
- 阅读了《原则》，整理了关于决策框架的笔记
- 学习了系统化的决策方法
```

#### 原则 3: 区分"描述工作" vs "推测变动"

**✅ 正确示范 - 描述工作**：
```markdown
基于文件内容发现你在研究AI Agent架构
→ "研究了AI Agent的架构设计，探索了多Agent协作模式"
```

**❌ 错误示范 - 推测变动**：
```markdown
看到文件修改时间是下午3点
→ "下午新增了关于多Agent协作的章节"  ← 这是在推测今天加了什么
```

**区别在于**：
- 描述工作：基于文件内容说明你在做什么
- 推测变动：试图推断今天的修改是什么

#### 原则 4: 为不同类型的文件选择合适的描述

**01Projects - 项目文件**：
- 描述项目进展、实现的功能、解决的问题
- 说明设计决策、技术选型
- 记录关键里程碑

**02Areas - 领域文件**：
- 描述学习的内容、获得的知识
- 记录实践和探索
- 总结领域内的成长

---

**项目进展 (Project Progress)**:
- Group updates by project (use project folder names as headers)
- For each project, summarize:
  - What was worked on
  - Key achievements or milestones
  - Important decisions or insights
  - Next steps or blockers
- Use concise, action-oriented language
- Include specific details (file names, features, etc.) when relevant
- **MUST include file references** for all mentioned changes (see File Reference Guidelines below)

**领域丰富 (Domain Enrichment)**:
- Group updates by domain/area (use area folder names as headers)
- For each area, summarize:
  - New knowledge or skills acquired
  - Insights or connections made
  - Practices or experiments tried
  - Questions or future explorations
- Focus on learning and growth
- Connect new information to existing knowledge when possible
- **MUST include file references** for all mentioned changes (see File Reference Guidelines below)

### File Reference Guidelines

**Core Principle**: Every change written in the journal MUST have corresponding file references. This creates a traceable link between the journal entry and the actual work done.

**Reference Format**:
- Use double square brackets: `[[path/to/file.md]]`
- All paths are relative to `$CONTEXT_PATH/` root directory
- Examples:
  - `[[01Projects/个人助手开发/CLAUDE.md]]`
  - `[[02Areas/AI工具使用/认知地图.md]]`
  - `[[04Archives/00账号/公众号存档.md]]`

**When to Reference**:

1. **Single Focus Change** - Reference the main file or CLAUDE.md:
   ```markdown
   ## 个人助手开发 [[01Projects/个人助手开发/CLAUDE.md]]
   - 完成了skill系统的核心架构设计
   - 实现了自动化文件检测功能
   ```

2. **Multiple Related Changes** - Reference all important files and explain what they cover:
   ```markdown
   ## 信息获取
   今日完成系统重构，涉及 [[01Projects/信息获取/架构设计.md]]、[[01Projects/信息获取/技术选型.md]]、[[01Projects/信息获取/CLAUDE.md]]
   - 重新设计了整体架构
   - 确定了技术栈
   - 更新了项目路线图
   ```

3. **Batch Changes in One Area** - If all files are important, reference them all:
   ```markdown
   ## AI工具使用
   完成Claude Code文档学习，更新了 [[02Areas/AI工具使用/Claude Code核心概念.md]]、[[02Areas/AI工具使用/最佳实践.md]]、[[02Areas/AI工具使用/工具集成.md]]
   - 掌握了MCP服务器配置
   - 理解了skill开发流程
   - 建立了工作流最佳实践
   ```

**Smart Referencing Strategy**:
- Judge what is a "significant change" - not every minor edit needs journaling
- When mentioning a project/area, decide intelligently:
  - Reference CLAUDE.md for overall project progress
  - Reference specific files for focused work on particular documents
  - Use both approaches flexibly based on context
- Clearly indicate what the changes involve, especially for batch updates
- Maintain readability - don't let references overwhelm the narrative

**Path Construction Examples**:
Assuming journal is saved in `02Areas/日记/`, references are still relative to `$CONTEXT_PATH/`:
- Project: `[[01Projects/项目名/文件.md]]` (NOT `../../01Projects/...`)
- Area: `[[02Areas/领域名/文件.md]]` (NOT `../领域名/...`)
- Archive: `[[04Archives/分类/文件.md]]`
- Resource: `[[03Resources/主题/文件.md]]`

### Formatting Standards

- Use markdown headers (##, ###) for organization
- Use bullet points (-) for lists
- Keep entries concise but informative
- Maintain consistent tense (past tense for completed actions)
- Use Chinese for content (matching Ryan's workflow language)

## Step 4: Present the Journal Entry

1. **Read the template** at `$CONTEXT_PATH/04Archives/template/日记模板 v4.md`
2. **Fill in the two sections**: 项目进展 and 领域丰富
3. **Present the complete journal** with:
   - The original template header (including value review links)
   - Populated 项目进展 section
   - Populated 领域丰富 section
   - Empty sections for other parts (持续输出, 每日复盘, 其他想记录的内容)

**Note**: The user will manually fill in other sections. Only automate what can be derived from file changes.

## Step 5: Save the Journal File

After generating the journal content, save it to the journal directory with the appropriate filename.

### File Naming Convention

**Format**: `YYYY-MM-DD.md`

**Examples**:
- Today's journal: `2024-12-04.md`
- Specific date: `2024-12-03.md`
- Weekly summary: `2024-12-01至12-07.md` or use the end date `2024-12-07.md`

### File Location

**Base directory**: `$CONTEXT_PATH/02Areas/日记/`

**Full path examples**:
- `$CONTEXT_PATH/02Areas/日记/2024-12-04.md`
- `$CONTEXT_PATH/02Areas/日记/2024-12-03.md`

### Saving Workflow

1. **Determine the date** for the journal:
   - For `--hours` mode: Use today's date
   - For `--date` mode: Use the specified date
   - For date range mode: Use the end date or create a descriptive name

2. **Format the filename**:
   ```python
   # Examples:
   # For today (2024-12-04):
   filename = "2024-12-04.md"

   # For specific date:
   filename = f"{date}.md"  # e.g., "2024-12-03.md"
   ```

3. **Construct the full path**:
   ```python
   full_path = f"$CONTEXT_PATH/02Areas/日记/{filename}"
   ```

4. **Write the journal content** using the Write tool:
   - Check if file already exists (optional: ask user if should overwrite)
   - Write the complete journal content including template header and generated sections
   - Confirm successful save to the user

### Important Notes

- **Always use the date being journaled**, not the current date (unless they're the same)
- **Ask for confirmation** if a file with the same name already exists
- **Preserve existing content** in other sections if updating an existing journal
- The journal directory may contain other files; only focus on the target date's file

## Example: Complete Workflow

**User request**: "帮我写今天的日记"

**Step-by-step execution**:

1. Run detection script: `python3 scripts/detect_changes.py --hours 24 --context-path $CONTEXT_PATH`
2. Read and analyze detected files
3. Read template from `$CONTEXT_PATH/04Archives/template/日记模板 v4.md`
4. Generate journal content
5. Save to `$CONTEXT_PATH/02Areas/日记/2024-12-04.md`

**Generated journal content**:

```markdown
# 复习价值观、蓝图、核心工作任务
[[王玥冉的精力管理计划#我的构想表格]]
[[王玥冉的精力管理计划#我的工作构想（反映出我的价值观）：]]
[[我的核心工作任务是什么？]]
[[王玥冉的精力管理计划#Fake it till you make it]]

---
# 项目进展

## 日记skill创建 [[01Projects/日记skill创建/CLAUDE.md]]
**有 Git commits** - 基于 commit message + 文件内容
Git commits:
  - "完成ryan-daily-journal skill初始化"
  - "实现文件变动检测脚本"
  - "编写完整工作流程文档"
文件内容: skill.md 详细说明了工作流程，detect_changes.py 实现了扫描功能

生成的日记:
- 完成了 ryan-daily-journal skill 的初始化和核心框架
- 实现了自动文件变动检测脚本，支持时间范围和Git模式
- 编写了完整的工作流程文档，包括使用说明和最佳实践

## 显化项目 [[01Projects/显化项目/小红书内容生成/CLAUDE.md]]
**没有 Git commits** - 完全基于文件内容
文件内容: 包含小红书爆款公式、内容生成规则、通用原则

生成的日记:
- 完善了小红书内容生成系统
- 整理了爆款文案的创作公式和通用原则
- 优化了内容生成的质量标准

---
# 领域丰富

## 个人助手开发 [[02Areas/个人助手开发/CLAUDE.md]]
**有 Git commits**:
Git commits:
  - "学习Claude Code skill系统设计"
  - "掌握渐进式披露原则"
文件内容: 包含 skill 开发的设计原则、最佳实践

生成的日记:
- 学习了 Claude Code skill 系统的设计原则
- 理解了渐进式披露（Progressive Disclosure）的概念
- 掌握了 skill 开发的最佳实践

## 心理 [[02Areas/心理/CLAUDE.md]]
**没有 Git commits** - 基于文件内容
文件内容: 包含最新的心理咨询记录，讨论了自我认知和行为模式

生成的日记:
- 进行了心理咨询，深化了对自我认知的理解
- 识别了新的行为模式，探索了应对策略

---
# 持续输出


---
# 每日复盘


---
# 其他想记录的内容

```

**Confirmation message**: "✅ 日记已保存到 `$CONTEXT_PATH/02Areas/日记/2024-12-04.md`"

## Best Practices

1. **Be selective**: Not every file change needs to be mentioned. Focus on meaningful work.
2. **Provide context**: Don't just list files changed, explain what was accomplished.
3. **Stay concise**: Keep each project/area update to 3-5 bullet points maximum.
4. **Choose the right time mode**:
   - For today's journal: Use `--hours 24` or default
   - For specific past dates: Use `--date YYYY-MM-DD`
   - For weekly summaries: Use `--start-date` and `--end-date`
   - For catching up after a break: Use `--hours` with larger value (e.g., 72, 168)
5. **Handle date references intelligently**:
   - "今天" → Use current date or `--hours 24`
   - "昨天" → Calculate yesterday's date and use `--date`
   - "12月3日" → Use `--date` with appropriate year (usually current year)
   - "这周" → Calculate Monday to today and use date range
6. **Handle edge cases**:
   - If no changes detected: Inform user and suggest checking a longer time range or different date
   - If too many changes: Summarize at a higher level or group by theme
   - For date-specific requests with no results: Verify the year is correct (system may be in 2025+)

## Troubleshooting

**No files detected:**
- Verify the Context path is correct
- Try extending the time range with `--hours 48` or more
- Check if files were actually modified (not just opened)
- For specific dates, verify the year is correct (2024 vs 2025)

**Too many files:**
- Use `--projects-only` or `--areas-only` to narrow scope
- Focus on files with substantial changes (ignore minor edits)

**Missing template:**
- Verify template exists at `$CONTEXT_PATH/04Archives/template/日记模板 v4.md`
- If missing, ask user for template location

**File already exists:**
- Ask user if they want to overwrite or update the existing journal
- If updating, read the existing file first and preserve manually-written sections (持续输出, 每日复盘, 其他想记录的内容)

**Wrong date in filename:**
- Double-check the date being journaled
- For `--hours` mode, use today's date
- For `--date` mode, use the exact date specified
- Don't confuse the detection date with the save date
