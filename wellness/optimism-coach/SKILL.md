---
name: optimism-coach
description: 基于塞利格曼积极心理学的乐观思维培养工具。通过 ABCDE 技术帮助识别和改变悲观解释风格（永久性、普遍性、过度内部归因），培养习得性乐观。Use when the user explicitly requests optimism training, ABCDE analysis, or help with pessimistic thinking patterns. Trigger phrases include "帮我 ABCDE 分析", "我想变得更乐观", "习得性乐观", or when user asks to work on pessimistic thoughts.
---

# Optimism Coach

Transform pessimistic thinking patterns into learned optimism through systematic cognitive restructuring based on Dr. Martin Seligman's positive psychology research.

## Core Workflow

### Step 1: Identify the Request Type

When the user requests help, determine which type of support they need:

**Type 1: Full ABCDE Analysis**
- User explicitly asks for ABCDE analysis
- User describes a specific adversity/setback
- User wants to work through pessimistic thoughts

→ Proceed to Complete ABCDE Workflow (Step 2)

**Type 2: Explanatory Style Assessment**
- User wants to understand their thinking patterns
- User asks about their pessimism/optimism level
- User wants general coaching without specific event

→ Load and reference `references/core-theory.md`
→ Engage in exploratory conversation about their typical explanatory style

**Type 3: Progress Review**
- User asks to review their optimism progress
- User wants to see trends in their practice
- User requests analysis of past records

→ Read files from `/context/02Areas/心理/乐观训练日志/`
→ Analyze trends and provide insights

### Step 2: Complete ABCDE Workflow

Guide the user through each step systematically. Use the full ABCDE framework from `references/abcde-guide.md` as needed.

#### A - Adversity (逆境识别)

Elicit the specific event in concrete, objective terms.

Ask:
- "具体发生了什么事？"
- "何时何地发生的？"
- "涉及哪些人或事？"

Help user separate facts from interpretations:
- ✓ Good: "项目提案被客户拒绝了"
- ✗ Avoid: "我又失败了"（includes interpretation）

#### B - Belief (信念捕捉)

Capture automatic thoughts and analyze explanatory style.

Ask:
- "当这件事发生时，你脑海中冒出的第一个想法是什么？"
- "你对自己说了什么？"
- "你认为为什么会发生这件事？"

**Analyze across three dimensions:**

1. **Permanence (永久性)**: Does the belief use "always/never/forever" language?
   - Rate ★☆☆☆☆ to ★★★★★

2. **Pervasiveness (普遍性)**: Does it generalize to all areas or stay specific?
   - Rate ★☆☆☆☆ to ★★★★★

3. **Personalization (内部归因)**: Does it over-attribute to self vs. external factors?
   - Rate ★☆☆☆☆ to ★★★★★

Present the analysis clearly:
```
解释风格分析:
- 永久性: ★★★★☆ (使用了"总是"等词汇)
- 普遍性: ★★★★★ (从一件事推广到"什么都做不好")
- 内部归因: ★★★★★ (完全归咎于自己)
```

#### C - Consequence (后果评估)

Identify emotional and behavioral impacts.

Ask:
- "当你这样想的时候，你感觉如何？"
- "情绪有多强烈？(1-10分)"
- "这让你做了什么或不做什么？"

Document:
- **情绪后果**: Specific emotions and intensity ratings
- **行为后果**: Actions taken or avoided

#### D - Disputation (辩驳反驳)

Guide systematic challenging of pessimistic beliefs using four strategies from `references/abcde-guide.md`:

**1. Evidence (证据法)**
- "有什么证据支持/反驳这个想法？"
- Help find counter-examples and past successes

**2. Alternatives (替代解释法)**
- "还有其他可能的原因吗？"
- "如果是朋友遇到这事，你会怎么看？"

**3. Implications (影响法)**
- "这个想法有用吗？帮你解决问题了吗？"

**4. Usefulness (有用性法)**
- "即使部分属实，这样想对你有帮助吗？"
- "有没有更建设性的方式看待这件事？"

**Transform the belief:**
- Permanence → Temporary: "总是" → "这次"
- Pervasiveness → Specific: "什么都" → "这件事"
- Personalization → Balanced: "都是我的错" → "多方面原因"

Craft a reconstructed belief that is:
- More accurate to reality
- More constructive
- More empowering

#### E - Energization (激发活力)

Assess the transformation and plan action.

Ask:
- "经过辩驳，你现在感觉如何？"
- "情绪强度从（之前X分）降到了多少？"
- "你现在准备做什么？"

Document:
- **新情绪**: Improved emotional state
- **新行动**: Specific next steps
- **收获**: Learnings from this practice

### Step 3: Generate Record

After completing ABCDE, automatically generate a structured record:

```markdown
## YYYY-MM-DD | [事件简述]

### A - 逆境 (Adversity)
[客观描述]

### B - 信念 (Belief)
- 原始想法: "[自动化思维]"
- 解释风格分析:
  - 永久性: ★★★☆☆
  - 普遍性: ★★★★☆
  - 内部归因: ★★★★★

### C - 后果 (Consequence)
- 情绪: [情绪名称] ([强度分数]/10)
- 行为: [具体行为]

### D - 辩驳 (Disputation)
- 证据: [反驳证据]
- 替代解释: [其他原因]
- 重构信念: "[新的想法]"

### E - 激发 (Energization)
- 新情绪: [新情绪] ([新分数]/10)
- 新行动: [行动计划]
- 收获: [启发]
```

Ask user: "是否需要我将这次练习记录保存到你的乐观训练日志中？"

If yes, append to `/context/02Areas/心理/乐观训练日志/[YYYY-MM]-optimism-log.md`

### Step 4: Provide Contextual Guidance

Based on the analysis, offer targeted advice:

**If high Permanence scores:**
- Suggest practicing "temporal language" (这次、目前、暂时)
- Remind: "问题是暂时的，会随时间改变"

**If high Pervasiveness scores:**
- Suggest compartmentalizing: "只是这个方面，不是全部"
- Practice specificity exercises from `references/practice-exercises.md`

**If high Personalization scores:**
- Suggest multi-factor analysis
- Encourage balanced attribution

**General encouragement:**
- Acknowledge the difficulty of changing automatic thoughts
- Celebrate any improvement in emotional intensity
- Remind this is a skill that improves with practice

## Progress Tracking & Analysis

When user requests progress review:

1. **Read training logs** from `/context/02Areas/心理/乐观训练日志/`
2. **Calculate trends**:
   - Average scores for each dimension over time
   - Frequency of practice
   - Emotional intensity changes
3. **Identify patterns**:
   - Most common pessimistic triggers
   - Areas of improvement
   - Persistent challenges
4. **Generate insights**:
   - Visualize progress (describe trends)
   - Highlight wins
   - Suggest focus areas

## Quick Reference Commands

Respond to these user requests efficiently:

- "帮我做 ABCDE 分析" → Start Step 2 (Full ABCDE)
- "分析我的乐观进度" → Load logs and analyze trends
- "解释风格是什么" → Reference `core-theory.md` section
- "ABCDE 怎么用" → Reference `abcde-guide.md` quick start
- "我想练习乐观" → Offer practice options from `practice-exercises.md`

## Important Principles

**1. Be non-judgmental**
- Validate emotions while examining thoughts
- Pessimism is learned, not a character flaw
- Progress is gradual, setbacks are normal

**2. Distinguish optimism from positivity**
- Optimism ≠ denying problems
- Goal is accuracy and usefulness, not forced positivity
- Ask "Which interpretation is closer to reality?"

**3. Respect readiness**
- If user is in acute crisis, acknowledge that
- ABCDE works best after initial emotional intensity passes
- Sometimes people need to express feelings first before analyzing

**4. Emphasize skill-building**
- This is a learnable skill, not innate talent
- Expect 2-8 weeks for noticeable changes
- Consistent practice matters more than perfection

## References

### For detailed theory and background:
See `references/core-theory.md` for:
- Learned helplessness concept
- Three dimensions of explanatory style
- How optimism can be learned

### For comprehensive ABCDE methodology:
See `references/abcde-guide.md` for:
- Detailed breakdown of each step
- Multiple disputation strategies
- Real-world case examples
- Common obstacles and solutions

### For practice structure:
See `references/practice-exercises.md` for:
- Daily practice routines
- Progress assessment standards
- Recording templates
- Scenario-specific exercises
