---
name: pdf2markdown
description: Convert PDF files to Markdown format with high-quality text extraction, preserving images, tables, and formulas. Use when the user requests to convert, transform, or process a PDF file into Markdown format, or when they need to make PDF content editable/searchable in their knowledge system. Supports both absolute and relative file paths.
---

# PDF to Markdown Converter

Convert PDF files to clean, well-formatted Markdown with automatic image extraction.

## Quick Start

When the user provides a PDF path and requests conversion, execute the script in background mode:

**CRITICAL**: Use `run_in_background=true` parameter in Bash tool. Do NOT wait for completion or monitor output.

```bash
scripts/convert.py <pdf-path>
```

The script will complete independently and save results to the source PDF directory.

**Example user requests:**
- "Convert this PDF to markdown: /path/to/document.pdf"
- "/pdf2markdown ~/Documents/paper.pdf"
- "Transform this PDF into a markdown file"

## Usage

### Basic Conversion

```bash
scripts/convert.py /path/to/document.pdf
```

**Execution**: Always run in background without monitoring.

**Output** (automatically saved to source directory):
- `document.md` - Markdown file in the same directory as the source PDF
- `document_images/` - Directory containing extracted images
- Markdown links automatically updated to reference local images

### Advanced Options

**LLM Enhancement** (higher quality, slower):
```bash
scripts/convert.py document.pdf --use-llm
```

**Force OCR** (for scanned PDFs):
```bash
scripts/convert.py document.pdf --force-ocr
```

All commands should be executed in background mode.

### File Conflict Handling

If `document.md` already exists, the script automatically appends a timestamp:
- `document_1704564789.md`
- `document_1704564789_images/`

## Technical Details

**Engine:** marker-pdf (high-quality PDF conversion library)

**Dependencies:** Uses the virtual environment from `/path/to/context/04Archives/pdf2markdown/venv/`

**Output location:** Same directory as source PDF

**First run:** Models are automatically downloaded to local cache (takes a few minutes, one-time only)

**Supported:** All PDF types (text-based, scanned, mixed)

## Script Location

`scripts/convert.py` - Executable script that leverages the project's environment

## Notes

- This skill shares dependencies with the pdf2markdown project to avoid duplication
- If the project is moved to Archives, update the shebang path in `scripts/convert.py`
