#!/usr/bin/env python3
"""
PDF to Markdown Converter CLI
Converts PDF files to Markdown format and saves output to the source directory.
"""

import os
import sys
import time
import argparse
from pathlib import Path

# Marker imports
from marker.converters.pdf import PdfConverter
from marker.config.parser import ConfigParser
from marker.models import create_model_dict
from marker.output import text_from_rendered


def save_local_output(text, images, source_path):
    """Save markdown and images to the same directory as source PDF."""
    base_dir = os.path.dirname(os.path.abspath(source_path))
    base_name = os.path.splitext(os.path.basename(source_path))[0]

    # Handle filename conflicts
    md_filename = f"{base_name}.md"
    md_path = os.path.join(base_dir, md_filename)

    final_base_name = base_name
    if os.path.exists(md_path):
        timestamp = int(time.time())
        final_base_name = f"{base_name}_{timestamp}"
        md_path = os.path.join(base_dir, f"{final_base_name}.md")
        print(f"⚠️  Markdown file exists, using timestamped name: {final_base_name}.md")

    # Create images directory
    images_dir_name = f"{final_base_name}_images"
    images_dir = os.path.join(base_dir, images_dir_name)
    os.makedirs(images_dir, exist_ok=True)

    # Save images and update markdown links
    for img_filename, img in images.items():
        img_path = os.path.join(images_dir, img_filename)
        img.save(img_path)

    # Update markdown to point to local image files
    for img_key in images:
        rel_path = os.path.join(images_dir_name, img_key)
        text = text.replace(f"({img_key})", f"({rel_path})")

    # Save Markdown
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(text)

    return md_path, images_dir


def convert_pdf(pdf_path, use_llm=False, force_ocr=False):
    """Convert PDF to Markdown using marker."""
    # Validate input
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if not pdf_path.lower().endswith('.pdf'):
        raise ValueError(f"File is not a PDF: {pdf_path}")

    print(f"📄 Converting: {os.path.basename(pdf_path)}")
    print("⏳ Loading models (this may take a moment on first run)...")

    # Load models
    model_dict = create_model_dict()

    # Configure conversion
    cli_options = {
        "output_format": "markdown",
        "use_llm": use_llm,
        "force_ocr": force_ocr,
        "output_dir": None
    }
    config_parser = ConfigParser(cli_options)
    config_dict = config_parser.generate_config_dict()
    config_dict["pdftext_workers"] = 1

    print("🔄 Processing PDF...")

    # Convert PDF
    converter = PdfConverter(
        config=config_dict,
        artifact_dict=model_dict,
        processor_list=config_parser.get_processors(),
        renderer=config_parser.get_renderer(),
        llm_service=config_parser.get_llm_service(),
    )

    rendered = converter(pdf_path)

    print("💾 Extracting text and images...")
    text, _, images = text_from_rendered(rendered)

    print("💾 Saving output...")
    md_path, images_dir = save_local_output(text, images, pdf_path)

    return md_path, images_dir, len(images)


def main():
    parser = argparse.ArgumentParser(
        description="Convert PDF to Markdown with marker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python convert.py document.pdf
  python convert.py /path/to/document.pdf --use-llm
  python convert.py paper.pdf --force-ocr
        """
    )

    parser.add_argument(
        "pdf_path",
        type=str,
        help="Path to PDF file (absolute or relative)"
    )

    parser.add_argument(
        "--use-llm",
        action="store_true",
        help="Use LLM enhancement for higher quality (slower)"
    )

    parser.add_argument(
        "--force-ocr",
        action="store_true",
        help="Force OCR on all pages"
    )

    args = parser.parse_args()

    try:
        # Convert path to absolute
        pdf_path = os.path.abspath(args.pdf_path)

        # Perform conversion
        md_path, images_dir, num_images = convert_pdf(
            pdf_path,
            use_llm=args.use_llm,
            force_ocr=args.force_ocr
        )

        print("\n✅ Conversion complete!")
        print(f"📝 Markdown: {md_path}")
        print(f"🖼️  Images: {images_dir} ({num_images} files)")

        return 0

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
