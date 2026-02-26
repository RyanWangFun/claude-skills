# Claude Skills Collection

> A collection of 15 custom Skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code), covering content creation, translation, productivity, Apple ecosystem integration, document processing, and psychological wellness.

[中文版](#中文说明)

---

## What Are Claude Code Skills?

Skills are reusable capability modules for Claude Code. Each Skill contains a `SKILL.md` definition file, optional reference documents, scripts, and templates. When activated, they give Claude specialized knowledge and workflows for specific tasks — like converting a YouTube video to an article, managing macOS Reminders via natural language, or guiding ACT-based psychological exercises.

## Skills Catalog

### Content Creation (3 Skills)

| Skill | Description |
|-------|-------------|
| **[writing-copilot](content-creation/writing-copilot/)** | Comprehensive writing assistant supporting titles, descriptions, social media posts (Xiaohongshu/Twitter), long-form articles, tag generation, and style migration. Core focus: eliminating AI-sounding prose while maintaining personal voice. |
| **[youtube-to-article](content-creation/youtube-to-article/)** | Converts YouTube videos to formal articles. Extracts transcripts, structures content, and produces polished Markdown articles with proper formatting. |
| **[article-translator](content-creation/article-translator/)** | Translates English articles to Simplified Chinese Markdown. Full pipeline: fetch → translate → format → save, with automatic structure preservation. |

### Translation (1 Skill)

| Skill | Description |
|-------|-------------|
| **[cn-to-en-translator](translation/cn-to-en-translator/)** | Translates Chinese Markdown articles to English while preserving original writing style, formatting, and structure. |

### Productivity (4 Skills)

| Skill | Description |
|-------|-------------|
| **[ryan-daily-journal](productivity/ryan-daily-journal/)** | Auto-generates daily journals by detecting file changes in the Context system (projects and areas). Uses Python script to scan modifications and populate a journal template. |
| **[gtdskill](productivity/gtdskill/)** | GTD processing engine bridging a knowledge workspace (thinking) and macOS Reminders (action). Processes inbox items, decomposes tasks into next actions, and routes to the correct system. |
| **[sync-context](productivity/sync-context/)** | Context system health monitor. Observes file structure for emergent signals — clustering patterns, boundary shifts, index drift — and reports observations. |
| **[fridge](productivity/fridge/)** | Home refrigerator inventory manager. Tracks items across shelves (A/B/C layers) and records daily meals, all through natural language via Apple Notes integration. |

### Apple Integration (2 Skills)

| Skill | Description |
|-------|-------------|
| **[reminders](apple-integration/reminders/)** | Full CRUD management of macOS Reminders via natural language. Supports tasks (add/edit/delete/complete/search), lists (create/rename/delete), and rich metadata (priority, due date, notes, URL, flags). Built with AppleScript/JXA backend. |
| **[apple-notes](apple-integration/apple-notes/)** | Controls macOS Notes.app through natural language. Full CRUD on folders and notes, with HTML table support for structured data. Notes sync via iCloud for cross-device access. |

### Document Processing (2 Skills)

| Skill | Description |
|-------|-------------|
| **[pdf2markdown](document-processing/pdf2markdown/)** | Converts PDF files to Markdown with high-quality text extraction, preserving images, tables, and formulas. |
| **[ea-pptx](document-processing/ea-pptx/)** | PowerPoint (.pptx) creation, editing, and analysis. Supports creating presentations from scratch, modifying content, working with layouts, and adding speaker notes. |

### Wellness (3 Skills)

| Skill | Description |
|-------|-------------|
| **[optimism-coach](wellness/optimism-coach/)** | Learned optimism training based on Seligman's positive psychology. Uses ABCDE technique to identify and restructure pessimistic explanatory styles (permanence, pervasiveness, personalization). |
| **[act-coach](wellness/act-coach/)** | Acceptance and Commitment Therapy (ACT) guide. Covers emotional management, thought defusion, values clarification, and committed action. Helps build psychological flexibility. |
| **[green-style-guidelines](wellness/green-style-guidelines/)** | Organic green brand color palette and typography for presentations and visual artifacts. |

## Skill Structure

Each Skill follows a consistent structure:

```
skill-name/
├── SKILL.md              # Core definition: name, description, triggers, execution logic
├── references/           # Supporting documents: methodology, examples, guidelines
│   ├── methodology.md
│   └── examples.md
├── scripts/              # Automation scripts (Python, AppleScript, Shell)
│   └── script.py
└── templates/            # Output templates
    └── template.md
```

The `SKILL.md` file is the entry point. It defines:
- **Trigger conditions**: When the Skill should activate
- **Execution workflow**: Step-by-step processing logic
- **Hard constraints**: Non-negotiable quality requirements
- **Soft guidelines**: Flexible directional principles
- **References**: Links to supporting documents for specialized knowledge

## How to Use

1. Clone this repo or copy individual Skill directories
2. Place them in your Claude Code skills folder (`~/.claude/skills/`)
3. Skills activate automatically when their trigger conditions are met, or can be invoked explicitly via `/skill-name`

## Project Structure

```
claude-skills/
├── README.md
├── LICENSE
├── content-creation/
│   ├── writing-copilot/
│   ├── youtube-to-article/
│   └── article-translator/
├── translation/
│   └── cn-to-en-translator/
├── productivity/
│   ├── ryan-daily-journal/
│   ├── gtdskill/
│   ├── sync-context/
│   └── fridge/
├── apple-integration/
│   ├── reminders/
│   └── apple-notes/
├── document-processing/
│   ├── pdf2markdown/
│   └── ea-pptx/
└── wellness/
    ├── optimism-coach/
    ├── act-coach/
    └── green-style-guidelines/
```

## Tech Stack

- **Platform**: Claude Code (Anthropic)
- **Languages**: Markdown (Skill definitions), Python (automation scripts), AppleScript/JXA (Apple integration)
- **Integrations**: macOS Reminders, Apple Notes, YouTube API, OpenRouter API

## License

MIT

---

<a name="中文说明"></a>

## 中文说明

> 15 个 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 自定义 Skill 合集，涵盖内容创作、翻译、效率工具、Apple 生态集成、文档处理和心理健康六大类别。

## 什么是 Claude Code Skills？

Skill 是 Claude Code 的可复用能力模块。每个 Skill 包含一个 `SKILL.md` 定义文件，以及可选的参考文档、脚本和模板。激活后，它们为 Claude 提供特定任务的专业知识和工作流 — 例如将 YouTube 视频转为文章、通过自然语言管理 macOS 提醒事项、或引导基于 ACT 的心理练习。

## Skills 目录

### 内容创作（3 个 Skill）

| Skill | 描述 |
|-------|------|
| **[writing-copilot](content-creation/writing-copilot/)** | 全面的写作助手，支持标题创作、简介描述、社交平台短文（小红书/即刻/Twitter）、长文创作、Tag 生成、文章重构与风格迁移。核心目标：去除 AI 味，保持个人风格。 |
| **[youtube-to-article](content-creation/youtube-to-article/)** | 将 YouTube 视频转换为正式文章。提取字幕、结构化内容，输出格式规范的 Markdown 文章。 |
| **[article-translator](content-creation/article-translator/)** | 将英文文章翻译为简体中文 Markdown。完整流水线：获取 → 翻译 → 格式化 → 保存，自动保留原文结构。 |

### 翻译（1 个 Skill）

| Skill | 描述 |
|-------|------|
| **[cn-to-en-translator](translation/cn-to-en-translator/)** | 将中文 Markdown 文章翻译为英文，保留原作写作风格、格式和结构。 |

### 效率工具（4 个 Skill）

| Skill | 描述 |
|-------|------|
| **[ryan-daily-journal](productivity/ryan-daily-journal/)** | 通过检测 Context 系统中的文件变更自动生成每日日记。使用 Python 脚本扫描项目和领域的修改记录，填充日记模板。 |
| **[gtdskill](productivity/gtdskill/)** | GTD 处理引擎，连接知识工作区（思考端）和 macOS 提醒事项（行动端）。处理收集箱、分解任务为下一步行动，并路由到正确的系统。 |
| **[sync-context](productivity/sync-context/)** | Context 系统健康监测器。观察文件结构的涌现信号 — 聚类形成、边界变化、索引偏差 — 并向用户报告观察结果。 |
| **[fridge](productivity/fridge/)** | 家庭冰箱库存管理器。通过自然语言追踪各层（A/B/C 层）物品并记录每日餐食，底层通过 Apple Notes 集成实现。 |

### Apple 生态集成（2 个 Skill）

| Skill | 描述 |
|-------|------|
| **[reminders](apple-integration/reminders/)** | 通过自然语言完整管理 macOS 提醒事项。支持任务的增删改查完成搜索、列表管理，以及优先级、截止时间、备注、URL、标记等丰富元数据。基于 AppleScript/JXA 后端。 |
| **[apple-notes](apple-integration/apple-notes/)** | 通过自然语言控制 macOS 备忘录。支持文件夹和笔记的完整 CRUD 操作，含 HTML 表格支持。笔记通过 iCloud 跨设备同步。 |

### 文档处理（2 个 Skill）

| Skill | 描述 |
|-------|------|
| **[pdf2markdown](document-processing/pdf2markdown/)** | 将 PDF 文件转换为 Markdown，高质量文本提取，保留图片、表格和公式。 |
| **[ea-pptx](document-processing/ea-pptx/)** | PowerPoint (.pptx) 演示文稿创建、编辑和分析。支持从零创建、修改内容、使用布局和添加演讲者备注。 |

### 心理健康（3 个 Skill）

| Skill | 描述 |
|-------|------|
| **[optimism-coach](wellness/optimism-coach/)** | 基于塞利格曼积极心理学的习得性乐观训练工具。通过 ABCDE 技术识别和改变悲观解释风格（永久性、普遍性、过度内部归因）。 |
| **[act-coach](wellness/act-coach/)** | 接纳承诺疗法（ACT）引导工具。涵盖情绪管理、念头脱钩、价值澄清和承诺行动，帮助培养心理灵活性。 |
| **[green-style-guidelines](wellness/green-style-guidelines/)** | 有机绿色品牌色彩和排版指南，用于演示文稿和视觉产出。 |

## Skill 结构

每个 Skill 遵循一致的结构：

```
skill-name/
├── SKILL.md              # 核心定义：名称、描述、触发条件、执行逻辑
├── references/           # 支持文档：方法论、示例、指南
│   ├── methodology.md
│   └── examples.md
├── scripts/              # 自动化脚本（Python、AppleScript、Shell）
│   └── script.py
└── templates/            # 输出模板
    └── template.md
```

`SKILL.md` 是入口文件，定义了：
- **触发条件**：何时激活此 Skill
- **执行工作流**：分步处理逻辑
- **硬约束**：不可违反的质量底线
- **软指导**：灵活的方向性原则
- **参考文档**：指向专业知识的支持文档

## 使用方式

1. 克隆本仓库或复制单个 Skill 目录
2. 放入 Claude Code 的 skills 文件夹（`~/.claude/skills/`）
3. Skill 在触发条件满足时自动激活，也可通过 `/skill-name` 显式调用

## 项目结构

```
claude-skills/
├── README.md
├── LICENSE
├── content-creation/
│   ├── writing-copilot/
│   ├── youtube-to-article/
│   └── article-translator/
├── translation/
│   └── cn-to-en-translator/
├── productivity/
│   ├── ryan-daily-journal/
│   ├── gtdskill/
│   ├── sync-context/
│   └── fridge/
├── apple-integration/
│   ├── reminders/
│   └── apple-notes/
├── document-processing/
│   ├── pdf2markdown/
│   └── ea-pptx/
└── wellness/
    ├── optimism-coach/
    ├── act-coach/
    └── green-style-guidelines/
```

## 技术栈

- **平台**: Claude Code (Anthropic)
- **语言**: Markdown（Skill 定义）、Python（自动化脚本）、AppleScript/JXA（Apple 集成）
- **集成**: macOS 提醒事项、Apple 备忘录、YouTube API、OpenRouter API
