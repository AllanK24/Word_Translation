from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
import json
import os

def save_json_to_pdf(data, output_path="translations.pdf"):
    from reportlab.lib import colors

    # Load and register a Unicode-compatible font
    font_path = "DejaVuSans.ttf"  # Make sure this file exists in your script directory
    if not os.path.exists(font_path):
        raise FileNotFoundError("Font file 'DejaVuSans.ttf' not found. Please place it in your working directory.")

    pdfmetrics.registerFont(TTFont("DejaVu", font_path))

    # Parse JSON and flatten nested entries
    cleaned = []
    for entry in data:
        if isinstance(entry, dict) and "response" in entry:
            try:
                nested = json.loads(entry["response"].strip("`json\n"))
                cleaned.extend(nested)
            except Exception:
                continue
        else:
            cleaned.append(entry)

    # Setup document
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            rightMargin=20, leftMargin=20,
                            topMargin=20, bottomMargin=20)

    styles = {
        'word': ParagraphStyle(
            name='WordStyle',
            fontName='DejaVu',
            fontSize=14,
            textColor=colors.darkblue,
            leading=18,
            spaceAfter=4,
            alignment=TA_LEFT
        ),
        'definition': ParagraphStyle(
            name='DefStyle',
            fontName='DejaVu',
            fontSize=11,
            leading=14,
            spaceAfter=10,
            alignment=TA_LEFT
        )
    }

    story = []

    for entry in cleaned:
        en_word = entry.get("en", "").strip().capitalize()
        ru_word = entry.get("ru", "").strip()
        en_def = entry.get("en_def", "").strip()
        ru_def = entry.get("ru_def", "").strip()

        story.append(Paragraph(f"<b>{en_word}</b> — {ru_word}", styles['word']))
        story.append(Paragraph(en_def, styles['definition']))
        story.append(Paragraph(ru_def, styles['definition']))
        story.append(Spacer(1, 6))

    doc.build(story)
    print(f"[INFO] PDF saved to: {output_path}")

if __name__=="__main__":
    import json

    # Load your JSON data from file or directly
    with open('translates.json', 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    save_json_to_pdf(json_data, output_path="words_translation_output.pdf")
