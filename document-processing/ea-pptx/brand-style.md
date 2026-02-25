# EA Brand Style

Becker Education EA 课程的品牌视觉规范。

## Colors

### Main Colors

| 名称 | Hex | 用途 |
|------|-----|------|
| Dark Blue | `#1a3a5c` | 主要文字、深色背景 |
| Light | `#ffffff` | 浅色背景、深色背景上的文字 |
| Light Gray | `#f5f5f5` | 柔和背景 |
| Dark Gray | `#333333` | 正文文字 |

### Accent Colors

| 名称 | Hex | 用途 |
|------|-----|------|
| Gold | `#d4a84b` | 主要强调色 |
| Red | `#c44536` | 警告强调色 |
| Green | `#4a7c59` | 成功强调色 |
| Light Blue | `#6a9bcc` | 次要强调色 |

## Typography

| 用途 | 字体 | Fallback |
|------|------|----------|
| 标题 | Source Han Sans Bold | Microsoft YaHei Bold |
| 正文 | Source Han Sans Regular | Microsoft YaHei |

### Font Application Rules

- **标题 (24pt+)**: Source Han Sans Bold
- **正文**: Source Han Sans Regular
- 根据背景色智能选择文字颜色
- 保持文字层级和格式

## Shape & Accent Application

- 非文字形状使用强调色
- 循环使用 Gold → Red → Green → Light Blue
- 保持视觉丰富度同时符合品牌规范

## Technical Notes

### Color Application
- 使用 RGB 值确保品牌色精确匹配
- 在 HTML 中使用 hex 格式 (如 `#1a3a5c`)
- 在 PptxGenJS 中使用不带 # 的 hex (如 `1a3a5c`)
- 跨系统保持颜色一致性

### Font Management
- 优先使用系统已安装的 Source Han Sans 字体
- 自动回退到 Microsoft YaHei
- 无需额外安装字体即可工作
