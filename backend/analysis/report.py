from io import BytesIO

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib import colors


pdfmetrics.registerFont(
    TTFont(
        "DejaVuSans",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    )
)


LABELS = {
    "title": "Invoresc — Investor Incident Report",
    "assessment": "Incident Assessment",
    "assessment_label": "Assessment",
    "indicator_score": "Indicator Score",
    "summary": "Summary",
    "risk": "Risk Indicators",
    "claims": "Claims & Evidence",
    "claim": "Claim",
    "source": "Source",
    "verification": "Verification",
    "timeline": "Incident Timeline",
    "ai_reconstruction": "AI-Assisted Incident Reconstruction",
    "ai_note": (
        "This section organizes the supplied evidence using AI. "
        "It does not independently verify claims or establish that "
        "fraud has occurred."
    ),
    "narrative": "Incident Narrative",
    "plain_explanation": "Plain-Language Explanation",
    "ai_claims": "AI-Reconstructed Claims",
    "evidence": "Evidence",
    "ai_timeline": "AI-Reconstructed Timeline",
    "missing": "Missing Evidence",
    "document": "What to Document or Verify",
    "ai_model": "AI model",
    "ai_basis": (
        "AI output is based only on the evidence supplied by the user."
    ),
    "safe": "Safe Response Plan",
    "original": "Original Evidence",
    "limitations": "Limitations",
    "footer": (
        "Invoresc is an investor-resilience tool. "
        "This report does not establish that fraud has occurred "
        "and does not provide investment recommendations."
    ),
}


def build_report(analysis, evidence):
    t = LABELS

    output = BytesIO()

    doc = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    for style in styles.byName.values():
        style.fontName = "DejaVuSans"

    story = []

    story.append(
        Paragraph(
            t["title"],
            styles["Title"],
        )
    )

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            t["assessment"],
            styles["Heading2"],
        )
    )

    assessment = analysis["assessment"]

    table_data = [
        [t["assessment_label"], assessment["level"]],
        [t["indicator_score"], str(assessment["indicator_score"])],
    ]

    table = Table(
        table_data,
        colWidths=[150, 300],
    )

    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    story.append(table)
    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            t["summary"],
            styles["Heading2"],
        )
    )

    story.append(
        Paragraph(
            analysis["summary"],
            styles["BodyText"],
        )
    )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            t["risk"],
            styles["Heading2"],
        )
    )

    for item in analysis["risk_indicators"]:
        story.append(
            Paragraph(
                f"<b>{item['title']}</b> — {item['severity']}",
                styles["BodyText"],
            )
        )

        story.append(
            Paragraph(
                item["explanation"],
                styles["BodyText"],
            )
        )

        story.append(Spacer(1, 7))

    story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            t["claims"],
            styles["Heading2"],
        )
    )

    if analysis["claims"]:
        for item in analysis["claims"]:
            story.append(
                Paragraph(
                    f"<b>{t['claim']}:</b> {item['claim']}",
                    styles["BodyText"],
                )
            )

            story.append(
                Paragraph(
                    f"<b>{t['source']}:</b> {item['source']}<br/>"
                    f"<b>{t['verification']}:</b> {item['verification']}",
                    styles["BodyText"],
                )
            )

            story.append(Spacer(1, 7))
    else:
        story.append(
            Paragraph(
                "No financial claims were identified.",
                styles["BodyText"],
            )
        )

    story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            t["timeline"],
            styles["Heading2"],
        )
    )

    if analysis["timeline"]:
        for item in analysis["timeline"]:
            story.append(
                Paragraph(
                    f"<b>{item['date']}</b> — {item['event']}",
                    styles["BodyText"],
                )
            )

            story.append(Spacer(1, 7))
    else:
        story.append(
            Paragraph(
                "No timeline events were identified.",
                styles["BodyText"],
            )
        )

    ai = analysis.get("ai_reconstruction")

    if ai and ai.get("enabled") and ai.get("data"):
        data = ai["data"]

        story.append(Spacer(1, 12))

        story.append(
            Paragraph(
                t["ai_reconstruction"],
                styles["Heading2"],
            )
        )

        story.append(
            Paragraph(
                t["ai_note"],
                styles["BodyText"],
            )
        )

        story.append(Spacer(1, 10))

        story.append(
            Paragraph(
                t["narrative"],
                styles["Heading3"],
            )
        )

        story.append(
            Paragraph(
                data["incident_narrative"],
                styles["BodyText"],
            )
        )

        story.append(Spacer(1, 10))

        story.append(
            Paragraph(
                t["plain_explanation"],
                styles["Heading3"],
            )
        )

        story.append(
            Paragraph(
                data["plain_language_explanation"],
                styles["BodyText"],
            )
        )

        story.append(Spacer(1, 10))

        story.append(
            Paragraph(
                t["ai_claims"],
                styles["Heading3"],
            )
        )

        for item in data.get("claims", []):
            story.append(
                Paragraph(
                    f"<b>{t['claim']}:</b> {item['claim']}",
                    styles["BodyText"],
                )
            )

            story.append(
                Paragraph(
                    f"<b>{t['evidence']}:</b> {item['evidence']}<br/>"
                    f"<b>{t['verification']}:</b> {item['verification']}",
                    styles["BodyText"],
                )
            )

            story.append(Spacer(1, 7))

        story.append(
            Paragraph(
                t["ai_timeline"],
                styles["Heading3"],
            )
        )

        for item in data.get("timeline", []):
            story.append(
                Paragraph(
                    f"<b>{item['date_or_time']}</b> — {item['event']}",
                    styles["BodyText"],
                )
            )

            story.append(Spacer(1, 7))

        story.append(
            Paragraph(
                t["missing"],
                styles["Heading3"],
            )
        )

        for item in data.get("missing_evidence", []):
            story.append(
                Paragraph(
                    f"• {item}",
                    styles["BodyText"],
                )
            )

        story.append(Spacer(1, 8))

        story.append(
            Paragraph(
                t["document"],
                styles["Heading3"],
            )
        )

        for item in data.get("documentation_questions", []):
            story.append(
                Paragraph(
                    f"• {item}",
                    styles["BodyText"],
                )
            )

        story.append(Spacer(1, 10))

        story.append(
            Paragraph(
                f"{t['ai_model']}: "
                f"{ai.get('model', 'Not specified')}. "
                f"{t['ai_basis']}",
                styles["BodyText"],
            )
        )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            t["safe"],
            styles["Heading2"],
        )
    )

    for index, action in enumerate(
        analysis["safe_actions"],
        1,
    ):
        story.append(
            Paragraph(
                f"{index}. {action}",
                styles["BodyText"],
            )
        )

        story.append(Spacer(1, 5))

    story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            t["original"],
            styles["Heading2"],
        )
    )

    story.append(
        Paragraph(
            evidence.replace("\n", "<br/>"),
            styles["BodyText"],
        )
    )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            t["limitations"],
            styles["Heading2"],
        )
    )

    for item in analysis["limitations"]:
        story.append(
            Paragraph(
                f"• {item}",
                styles["BodyText"],
            )
        )

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            t["footer"],
            styles["BodyText"],
        )
    )

    doc.build(story)

    output.seek(0)

    return output