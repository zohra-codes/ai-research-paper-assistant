
from io import BytesIO
import re
from xml.sax.saxutils import escape

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.lib.units import cm


def format_inline(text):
    """Convert basic Markdown bold and italic to ReportLab markup."""
    text = escape(text)

    # Bold: **text**
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)

    # Italic: *text*
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)

    # Inline code: `text`
    text = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", text)

    return text


def generate_pdf(text):
    buffer = BytesIO()

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="AI Research Report",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        spaceAfter=18,
    )

    heading_style = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        spaceBefore=12,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        leading=15,
        spaceAfter=6,
    )

    content = [
        Paragraph("AI Research Report", title_style),
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.grey,
            spaceAfter=16,
        ),
    ]

    in_code_block = False
    code_lines = []

    for raw_line in text.splitlines():
        line = raw_line.strip()

        # Skip empty lines, except for spacing
        if not line:
            if in_code_block:
                code_lines.append("")
            else:
                content.append(Spacer(1, 4))
            continue

        # Handle fenced code blocks
        if line.startswith("```"):
            if in_code_block:
                code_text = escape("\n".join(code_lines))
                content.append(
                    Paragraph(
                        code_text.replace("\n", "<br/>"),
                        styles["Code"],
                    )
                )
                content.append(Spacer(1, 8))
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
                code_lines = []
            continue

        if in_code_block:
            code_lines.append(raw_line)
            continue

        # Horizontal rules
        if re.match(r"^([-*_]\s*){3,}$", line):
            content.append(Spacer(1, 5))
            content.append(HRFlowable(width="100%", color=colors.grey))
            content.append(Spacer(1, 8))
            continue

        # Markdown headings
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading_match:
            heading_text = format_inline(heading_match.group(2))
            content.append(Paragraph(heading_text, heading_style))
            continue

        # Bullet points
        if re.match(r"^[-*+]\s+", line):
            bullet_text = re.sub(r"^[-*+]\s+", "", line)
            content.append(
                Paragraph(
                    "&#8226;&nbsp;&nbsp;" + format_inline(bullet_text),
                    body_style,
                )
            )
            continue

        # Numbered lists
        number_match = re.match(r"^(\d+)\.\s+(.+)$", line)
        if number_match:
            content.append(
                Paragraph(
                    escape(number_match.group(1)) + ".&nbsp;&nbsp;"
                    + format_inline(number_match.group(2)),
                    body_style,
                )
            )
            continue

        # Block quotes
        if line.startswith(">"):
            quote_text = format_inline(line.lstrip("> "))
            content.append(
                Paragraph(
                    quote_text,
                    styles["Italic"],
                )
            )
            continue

        # Normal paragraph
        content.append(Paragraph(format_inline(line), body_style))

    # Close a code block if the AI left it unfinished
    if in_code_block and code_lines:
        code_text = escape("\n".join(code_lines))
        content.append(
            Paragraph(code_text.replace("\n", "<br/>"), styles["Code"])
        )

    pdf.build(content)
    buffer.seek(0)
    return buffer.getvalue()


if __name__ == "__main__":
    sample_text = """
# How should a beginner start coding?

Starting coding can feel difficult, but you can learn step by step.

## 1. Learn Python fundamentals

- Understand variables and data types.
- Practice conditions and loops.
- Write simple functions.
- Build small projects.

**Tip:** Practice a little every day.
"""

    with open("research_result.pdf", "wb") as file:
        file.write(generate_pdf(sample_text))

    print("PDF created successfully: research_result.pdf")
