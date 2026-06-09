# utils/pdf_export.py

import io
from PIL import Image
from fpdf import FPDF


PAGE_WIDTH = 210
PAGE_HEIGHT = 297
MARGIN = 15
IMAGE_HEIGHT = 160

FONT_SIZE_TITLE = 20
FONT_SIZE_TEXT = 12
FONT_SIZE_PAGE = 9


def _clean_text(text: str) -> str:
    """Replace problematic unicode characters for PDF rendering."""

    replacements = {
        "\u2014": "-",
        "\u2013": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2026": "...",
        "\u00e9": "e",
        "\u00e0": "a",
        "\u00f1": "n",
        "\u00fc": "u",
        "\u2022": "-",
        "\u00a0": " ",
    }

    for char, replacement in replacements.items():
        text = text.replace(char, replacement)

    return text


def export_pdf(pages: list, title: str) -> bytes:
    """Convert story pages into a downloadable PDF."""

    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=False)

        # Title page
        pdf.add_page()
        pdf.set_font("Helvetica", "B", FONT_SIZE_TITLE)
        pdf.set_y(PAGE_HEIGHT / 2 - 20)

        pdf.cell(
            w=0,
            h=20,
            text=_clean_text(title),
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )

        pdf.set_font("Helvetica", "", 12)
        pdf.cell(
            w=0,
            h=10,
            text=f"{len(pages)} pages",
            align="C",
        )

        # Story pages
        for page in pages:
            pdf.add_page()

            # Image
            if page.get("image_url"):
                try:
                    pil_image = Image.open(
                        io.BytesIO(page["image_url"])
                    ).convert("RGB")

                    buffer = io.BytesIO()
                    pil_image.save(buffer, format="JPEG", quality=95)
                    buffer.seek(0)

                    img_w = PAGE_WIDTH - (MARGIN * 2)

                    pdf.image(
                        buffer,
                        x=MARGIN,
                        y=MARGIN,
                        w=img_w,
                        h=IMAGE_HEIGHT,
                    )

                except Exception as e:
                    print(f"Image error page {page.get('page_number')}: {e}")

            # Text
            pdf.set_font("Helvetica", "", FONT_SIZE_TEXT)
            pdf.set_xy(MARGIN, 185)

            pdf.multi_cell(
                w=PAGE_WIDTH - (MARGIN * 2),
                h=7,
                text=_clean_text(page.get("text", "")),
                align="L",
            )

            # Page number
            pdf.set_font("Helvetica", "", FONT_SIZE_PAGE)
            pdf.set_xy(MARGIN, PAGE_HEIGHT - 12)

            pdf.cell(
                w=PAGE_WIDTH - (MARGIN * 2),
                h=8,
                text=f"- {page.get('page_number', '')} -",
                align="C",
            )

        return bytes(pdf.output())

    except Exception as e:
        import streamlit as st
        st.error(f"PDF generation failed: {str(e)}")
        return None