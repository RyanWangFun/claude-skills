---
name: green-style-guidelines
description: "Applies organic green brand colors and typography to presentations and artifacts. Use when creating eco-friendly, nature-themed, or organic brand style content. Keywords green, organic, eco, nature, forest, sustainable."
---

# Green Organic Style Guidelines

## Overview

Apply the organic green brand identity and style to presentations and visual artifacts. This style evokes nature, sustainability, and eco-friendliness.

**Keywords**: green style, organic brand, eco-friendly, nature theme, forest green, sustainable design, natural colors, organic presentation

## Brand Guidelines

### Colors

**Primary Colors:**

- Forest Green: `#335635` - Primary brand color, headers, accents
- Cream: `#FDF9ED` - Primary background, light sections
- Warm Gray: `#F5F1EB` - Secondary background, subtle sections
- White: `#FFFFFF` - Clean backgrounds, text on dark

**Color Usage:**

- Use Forest Green (#335635) for headers, titles, and key visual elements
- Use Cream (#FDF9ED) as the primary slide background
- Use Warm Gray (#F5F1EB) for content cards and secondary sections
- Use White (#FFFFFF) for text on green backgrounds

### Typography

**Headings:**
- Primary: Poppins SemiBold / Poppins Bold
- Alternative: Urbanist SemiBold
- Fallback: Arial Bold

**Body Text:**
- Primary: Pretendard Regular / Poppins Medium
- Fallback: Arial

**Font Pairing Guidelines:**
- Large titles (32pt+): Poppins Bold or Urbanist SemiBold
- Section headers (24pt): Poppins SemiBold
- Subheadings (18pt): Poppins Medium
- Body text (12-14pt): Pretendard Regular or Poppins Regular

## Design Principles

### Visual Style

- **Organic shapes**: Prefer rounded corners, natural curves
- **Earthy tones**: Stick to the green/cream palette
- **Whitespace**: Generous margins for clean, breathable layouts
- **Nature imagery**: Leaf patterns, botanical elements when appropriate

### Layout Recommendations

- Clean, minimalist compositions
- Left-aligned text for readability
- Strong visual hierarchy with green accents
- Cards and sections with subtle cream/warm gray backgrounds

## Technical Details

### Color Application in Code

**HTML/CSS:**
```css
:root {
  --green-primary: #335635;
  --cream-bg: #FDF9ED;
  --warm-gray: #F5F1EB;
  --white: #FFFFFF;
}
```

**PptxGenJS (no # prefix):**
```javascript
const COLORS = {
  green: '335635',
  cream: 'FDF9ED',
  warmGray: 'F5F1EB',
  white: 'FFFFFF'
};
```

### Font Management

- Poppins and Urbanist should be pre-installed for best results
- Falls back to Arial automatically if custom fonts unavailable
- Chinese text: Use system default (e.g., PingFang SC, Microsoft YaHei)

## Example Usage

### Slide Background
```javascript
// Cream background with green header bar
slide.addShape(pptx.shapes.RECTANGLE, {
  x: 0, y: 0, w: '100%', h: 0.8,
  fill: { color: '335635' }
});
```

### Title Styling
```javascript
slide.addText('Section Title', {
  x: 0.5, y: 0.2, w: 9, h: 0.5,
  fontSize: 28,
  fontFace: 'Poppins',
  bold: true,
  color: 'FFFFFF'  // White on green background
});
```

### Content Card
```javascript
slide.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
  x: 0.5, y: 1.5, w: 4, h: 3,
  fill: { color: 'FFFFFF' },
  line: { color: '335635', width: 1 },
  rectRadius: 0.1
});
```
