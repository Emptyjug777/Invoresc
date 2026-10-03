from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from analysis.ai import ai_reconstruct
from analysis.pdf import extract_text as extract_pdf_text
from analysis.engine import analyze_incident
from analysis.ocr import extract_text
from analysis.report import build_report


app = FastAPI(
    title="Invoresc API",
    description="Investor Incident Response & Resilience Assistant",
    version="0.1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    evidence: str
    ai_reconstruction: dict | None = None


@app.get("/")
def root():
    return {
        "name": "Invoresc",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    result = analyze_incident(req.evidence)

    if result["success"]:
        result["ai_reconstruction"] = ai_reconstruct(
            req.evidence
        )

    return result


@app.post("/analyze-image")
async def analyze_image(
    file: UploadFile = File(...)
):
    file_bytes = await file.read()
    text = extract_text(file_bytes)

    if not text:
        return {
            "success": False,
            "error": "No readable text was detected in the image."
        }

    result = analyze_incident(text)

    if not result["success"]:
        return result

    result["ai_reconstruction"] = ai_reconstruct(
        text
    )

    result["extracted_text"] = text

    return result


@app.post("/analyze-pdf")
async def analyze_pdf(
    file: UploadFile = File(...)
):
    file_bytes = await file.read()
    text = extract_pdf_text(file_bytes)

    if not text:
        return {
            "success": False,
            "error": "No readable text was detected in the PDF."
        }

    result = analyze_incident(text)

    if not result["success"]:
        return result

    result["ai_reconstruction"] = ai_reconstruct(
        text
    )

    result["extracted_text"] = text

    return result


@app.post("/generate-report")
def generate_report(req: AnalyzeRequest):
    analysis = analyze_incident(
        req.evidence
    )

    if not analysis["success"]:
        return analysis

    if req.ai_reconstruction:
        analysis["ai_reconstruction"] = req.ai_reconstruction
    else:
        analysis["ai_reconstruction"] = ai_reconstruct(
            req.evidence
        )

    pdf = build_report(
        analysis,
        req.evidence
    )

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=invoresc-incident-report.pdf"
        }
    )