---
name: ea-pptx
description: "Presentation creation, editing, and analysis. When Claude needs to work with presentations (.pptx files) for: (1) Creating new presentations, (2) Modifying or editing content, (3) Working with layouts, (4) Adding comments or speaker notes, or any other presentation tasks"
license: Proprietary. LICENSE.txt has complete terms
---

# EA PPTX

EA 课程专属 PPT 生成 skill。完整继承 pptx 的所有技术能力，集成 EA 专属的品牌规范、布局规则，以及多阶段 Agent 调度流程。

## EA 专属资源

| 文件 | 说明 |
|------|------|
| [brand-style.md](brand-style.md) | EA 品牌颜色、字体规范 |
| [layout-rules.md](layout-rules.md) | 递归组合式布局系统：容器类型（HStack/VStack）、内容类型、组合规则、典型场景示例、布局设计原则 |
| [references/quality-checklist.md](references/quality-checklist.md) | 质量检查清单：空间布局、内容适配、视觉层次、品牌一致性、细节打磨、技术规范 |
| [assets/](assets/) | Logo 等品牌资源 |

---

## Workflow

本 skill 使用**交互式、逐页生成工作流**，确保每一页都符合质量标准后再继续下一页。

### 整体流程

```
┌─────────────────────────────────────────────────────────────────┐
│                         EA PPTX Workflow                         │
│                                                                  │
│  Step 1: 内容准备                                                │
│  ┌─────────────┐      ┌──────────────┐      ┌───────────────┐  │
│  │  用户输入    │ ──▶  │  结构化内容   │ ──▶  │  content.md   │  │
│  └─────────────┘      └──────────────┘      └───────────────┘  │
│                                                                  │
│  Step 2: 逐页生成（循环）                                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 结构分析 → 布局选择 → 生成 → 质量检查 → 预览 → 用户确认  │  │
│  │ (布局不合理时) ↖_______________调整布局__________________│  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Step 3: 最终输出                                                │
│  ┌──────────────┐                                               │
│  │  final.pptx  │                                               │
│  └──────────────┘                                               │
└─────────────────────────────────────────────────────────────────┘
```

---

### Step 1: 内容准备

**目标**: 将用户输入转化为结构化的 Markdown 内容

#### 收集输入

| 输入项 | 必须 | 说明 |
|--------|------|------|
| Content Source | ✓ | 主题 / 参考文件 / Markdown / Figma URL |
| Output Path | ✓ | 输出文件路径 |
| Instructor Name | - | 讲师姓名（用于 Cover 和 Closing 页） |
| Course Subject | - | 课程科目（如"个人税 Part 1"） |

#### 生成结构化内容

将任何输入转化为层级 Markdown（`content.md`）：

```markdown
# Presentation Title

## Slide 1: [Title]
- Point 1
- Point 2

## Slide 2: [Title]
[Content...]
```

**输出**: `content.md`

---

### Step 2: 逐页生成

**目标**: 逐页分析内容、选择布局、生成 PPT，每页生成后立即预览和确认

#### 循环流程（针对每一页）

对于每一页（Slide N）：

##### 2.1 结构分析和布局选择

1. **读取页面内容**
   - 读取 `content.md` 中 Slide N 的内容
   - **CRITICAL**: 完整读取 [layout-rules.md](layout-rules.md) 理解 EA 专属版式定义和布局规则

2. **分析内容结构**
   - 页面类型：Cover / Content / Closing
   - 标题层级和数量
   - 要点数量（列表项数量）
   - 是否有图表、图片或表格
   - 内容密度（文字量、信息块数量）

3. **设计布局组合**
   - **CRITICAL**: 完整读取 [layout-rules.md](layout-rules.md)
   - 根据"递归组合式布局系统"设计页面布局
   - Cover/Closing 页使用对应的固定版式
   - Content 页根据内容特征选择容器和内容类型组合
   - 输出：YAML 格式的布局结构描述

4. **记录布局决策**
   - 在生成过程中记录：页面类型、布局结构（YAML）、设计理由
   - 用于后续质量检查中的布局合理性验证

##### 2.2 生成单页

1. **读取相关规范**
   - **CRITICAL**: 完整读取 [html2pptx.md](html2pptx.md)
   - 读取 [brand-style.md](brand-style.md) 获取 EA 颜色字体
   - 读取 `content.md` 中 Slide N 的内容
   - 参考 [layout-rules.md](layout-rules.md) 中选定版式的具体规范

2. **生成 HTML 文件**

   按照 html2pptx.md 规范创建 `slideN.html`：

   **CRITICAL 规则**（必须遵守，否则转换失败）：
   - 所有文本必须在 `<p>`/`<h1>`-`<h6>`/`<ul>`/`<ol>` 标签内
   - 只使用 web-safe 字体（Arial, Helvetica, Times New Roman, Georgia, Courier New）
   - 不使用 CSS 渐变（渐变需先用 Sharp 预渲染为 PNG）
   - 背景/边框/阴影只能用在 `<div>` 上
   - 使用 `<ul>`/`<ol>` 列表，禁止手动子弹符号（•, -, *）
   - body 尺寸: **720pt × 405pt** (16:9)
   - 使用 `display: flex` 防止 margin collapse

3. **转换为 PPT**

   创建 `slideN.js` 调用 html2pptx：
   ```javascript
   const html2pptx = require('./scripts/html2pptx.js');
   html2pptx('slideN.html', 'slideN.pptx');
   ```

   执行：
   ```bash
   node slideN.js
   ```

##### 2.3 质量检查

使用 [references/quality-checklist.md](references/quality-checklist.md) 进行检查：

**检查维度**:
1. **布局合理性** 🔴
   - 参考 [layout-rules.md](layout-rules.md) 中的"Layout Tips - 布局设计原则"
   - 容器组合与内容关系匹配（并列内容用 HStack，分层内容用 VStack）
   - 内容密度适配：不过度拥挤也不过度空旷
   - 嵌套层级合理：不超过 3 层
   - 比例分配合理：反映内容的重要性
   - **如果布局不合理**: 回到步骤 2.1，重新设计布局并生成
   - **判断标准**:
     - ✅ 通过: 布局与内容完美匹配，视觉舒适
     - ❌ 不通过: 布局与内容不匹配，需要调整

2. **空间布局质量** 🟡
   - 呼吸感：内容占比 75-85%，页边距合理
   - 元素间距：标题与正文 ≥24pt，段落间 ≥16pt
   - 视觉平衡：重心稳定，左右均衡

3. **内容适配性** 🔴
   - 文本溢出：无裁切或省略号
   - 图片比例：等比例缩放，无变形
   - 字号适配：正文 ≥16pt，标题 ≥28pt
   - 密度控制：正文 ≤10-12 行，列表 ≤6-8 项

4. **视觉层次与对齐** 🔴
   - 标题层次：明显尺寸和字重差异
   - 对齐规范：左对齐元素严格对齐，居中元素真正居中
   - 网格一致性：同类页面使用相同布局网格

5. **品牌一致性** 🔴
   - 颜色正确：严格使用 EA 品牌色板
   - 字体应用：Source Han Sans Bold（标题）/ Regular（正文）
   - Logo 位置：Cover/Content 右上角，Closing 底部

6. **细节打磨** 🟡
   - 标点规范：中文全角，英文半角
   - 行距设置：正文 1.5 倍，列表 1.3 倍
   - 对比度：文字与背景 ≥4.5:1

7. **技术规范遵守** 🔴
   - HTML 转换规范：严格遵守 html2pptx.md
   - 页面尺寸：720pt × 405pt

**优先级**:
- 🔴 高优先级：必须通过才能继续（布局不合理需要重新选择布局并生成）
- 🟡 中优先级：可接受轻微偏差

##### 2.4 生成预览

```bash
python scripts/thumbnail.py slideN.pptx slideN-preview.jpg --cols 1
```

##### 2.5 展示给用户

```
【Slide N 生成完成】

页面信息:
- 标题: [页面标题]
- 页面类型: [Cover / Content / Closing]
- 布局结构 (YAML):
  [容器和内容类型的组合结构]
- 设计理由: [为什么选择这种组合]
- 主要元素: [列表/图片/图表等]
- 颜色: [使用的主要颜色]
- 字体: [标题/正文字体和字号]

质量检查结果:
✅ 布局合理性
✅ 空间布局质量
✅ 内容适配性
✅ 视觉层次与对齐
✅ 品牌一致性
✅ 细节打磨
✅ 技术规范遵守

[显示 slideN-preview.jpg 预览图]

是否继续下一页？如需调整请说明。
```

##### 2.6 用户确认

- **✅ 确认通过**: 继续生成下一页（重复 Step 2）
- **❌ 需要调整**: 根据用户反馈修改当前页，重新生成并预览
- **⏸ 暂停**: 保存当前进度，稍后继续

##### 2.7 合并页面

当前页通过后，将其合并到累积的 PPT 文件：

```bash
# 第一页
cp slide1.pptx working.pptx

# 后续页面（使用 ooxml 操作）
python ooxml/scripts/unpack.py slideN.pptx temp/
python ooxml/scripts/unpack.py working.pptx working-temp/
# 提取 slideN 的 XML 并添加到 working-temp
python ooxml/scripts/pack.py working-temp/ working.pptx
```

**循环直到所有页面完成**

---

### Step 3: 最终输出

1. **重命名最终文件**
   ```bash
   cp working.pptx [用户指定的输出路径]
   ```

2. **生成完整预览**
   ```bash
   python scripts/thumbnail.py final.pptx final-thumbnails.jpg --cols 5
   ```

3. **交付给用户**
   ```
   【PPT 生成完成】

   输出文件: [输出路径]
   总页数: N 页

   [显示 final-thumbnails.jpg 完整预览]

   所有页面均已通过质量检查。
   ```

---

## Design Principles

**CRITICAL**: Before creating any presentation, analyze the content and choose appropriate design elements:
1. **Consider the subject matter**: What is this presentation about? What tone, industry, or mood does it suggest?
2. **Check for branding**: For EA courses, use brand-style.md specifications
3. **Match palette to content**: Select colors that reflect the subject
4. **State your approach**: Explain your design choices before writing code

**Requirements**:
- ✅ State your content-informed design approach BEFORE writing code
- ✅ For EA courses: Use Source Han Sans fonts (see brand-style.md)
- ✅ Create clear visual hierarchy through size, weight, and color
- ✅ Ensure readability: strong contrast, appropriately sized text, clean alignment
- ✅ Be consistent: repeat patterns, spacing, and visual language across slides

### Visual Details Options

**Geometric Patterns**:
- Diagonal section dividers instead of horizontal
- Asymmetric column widths (30/70, 40/60, 25/75)
- Rotated text headers at 90° or 270°
- Circular/hexagonal frames for images
- Triangular accent shapes in corners
- Overlapping shapes for depth

**Border & Frame Treatments**:
- Thick single-color borders (10-20pt) on one side only
- Double-line borders with contrasting colors
- Corner brackets instead of full frames
- L-shaped borders (top+left or bottom+right)
- Underline accents beneath headers (3-5pt thick)

**Typography Treatments**:
- Extreme size contrast (72pt headlines vs 11pt body)
- All-caps headers with wide letter spacing
- Numbered sections in oversized display type
- Monospace (Courier New) for data/stats/technical content
- Condensed fonts (Arial Narrow) for dense information
- Outlined text for emphasis

**Chart & Data Styling**:
- Monochrome charts with single accent color for key data
- Horizontal bar charts instead of vertical
- Dot plots instead of bar charts
- Minimal gridlines or none at all
- Data labels directly on elements (no legends)
- Oversized numbers for key metrics

**Layout Innovations**:
- Full-bleed images with text overlays
- Sidebar column (20-30% width) for navigation/context
- Modular grid systems (3×3, 4×4 blocks)
- Z-pattern or F-pattern content flow
- Floating text boxes over colored shapes
- Magazine-style multi-column layouts

**Background Treatments**:
- Solid color blocks occupying 40-60% of slide
- Gradient fills (vertical or diagonal only)
- Split backgrounds (two colors, diagonal or vertical)
- Edge-to-edge color bands
- Negative space as a design element

---

## 技术能力参考

| 文档 | 内容 |
|------|------|
| [html2pptx.md](html2pptx.md) | HTML 转 PPT 的完整语法、规则、示例 |
| [ooxml.md](ooxml.md) | OOXML 格式编辑、解包/打包、XML 操作 |

### 常用脚本

| 脚本 | 用途 |
|------|------|
| `scripts/html2pptx.js` | HTML 转 PPT 核心库 |
| `scripts/thumbnail.py` | 生成缩略图网格 |
| `scripts/rearrange.py` | 重排/复制/删除 slides |
| `scripts/inventory.py` | 提取文字形状信息 |
| `scripts/replace.py` | 批量替换文字 |
| `ooxml/scripts/unpack.py` | 解包 pptx 为 XML |
| `ooxml/scripts/pack.py` | 打包 XML 为 pptx |
| `ooxml/scripts/validate.py` | 验证 XML 合法性 |

---

## Reading and Analyzing Content

### Text extraction
```bash
python -m markitdown path-to-file.pptx
```

### Raw XML access
```bash
python ooxml/scripts/unpack.py <office_file> <output_dir>
```

#### Key file structures
* `ppt/presentation.xml` - Main presentation metadata and slide references
* `ppt/slides/slide{N}.xml` - Individual slide contents
* `ppt/notesSlides/notesSlide{N}.xml` - Speaker notes
* `ppt/slideLayouts/` - Layout templates
* `ppt/slideMasters/` - Master slide templates
* `ppt/theme/` - Theme and styling information
* `ppt/media/` - Images and other media files

---

## Creating Thumbnail Grids

```bash
python scripts/thumbnail.py template.pptx [output_prefix] --cols 4
```

- Creates: `thumbnails.jpg` (or multiple for large decks)
- Default: 5 columns, max 30 slides per grid
- Slides are zero-indexed

---

## Editing an Existing Presentation

1. **MANDATORY**: Read [ooxml.md](ooxml.md) completely
2. Unpack: `python ooxml/scripts/unpack.py <office_file> <output_dir>`
3. Edit XML files
4. Validate: `python ooxml/scripts/validate.py <dir> --original <file>`
5. Pack: `python ooxml/scripts/pack.py <input_directory> <office_file>`

---

## 配置参数

本 skill 使用**交互式单页生成**流程，无需批量并行配置。

**关键参数**:

| 参数 | 说明 |
|------|------|
| 页面尺寸 | 720pt × 405pt (16:9) |
| 最小字号 | 正文 16pt，标题 28pt |
| 页边距 | 上/下 ≥36pt，左/右 ≥43pt |

---

## 依赖

Required dependencies (should already be installed):

- **markitdown**: `pip install "markitdown[pptx]"` (for text extraction)
- **pptxgenjs**: `npm install -g pptxgenjs` (for creating presentations)
- **playwright**: `npm install -g playwright` (for HTML rendering)
- **react-icons**: `npm install -g react-icons react react-dom` (for icons)
- **sharp**: `npm install -g sharp` (for image processing)
- **LibreOffice**: `sudo apt-get install libreoffice` (for PDF conversion)
- **Poppler**: `sudo apt-get install poppler-utils` (for pdftoppm)
- **defusedxml**: `pip install defusedxml` (for secure XML parsing)
