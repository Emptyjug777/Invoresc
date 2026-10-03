import json
import os
import time

from google import genai
from google.genai import types


MODEL = "gemini-3.6-flash"


SYSTEM_INSTRUCTION = """
You are the AI reconstruction component of Invoresc, an Investor Incident
Response & Resilience Assistant.

Your job is to organize and explain user-provided financial incident evidence.

STRICT RULES:
1. Never provide buy, sell, hold, trading, or investment recommendations.
2. Never predict prices, returns, or market movements.
3. Never declare that something is definitely a scam or fraud.
4. Treat all supplied material as user-provided evidence.
5. Do not invent dates, people, organizations, transactions, or events.
6. Regulatory or financial claims in the evidence must be marked as
   "Not independently verified".
7. Do not request or expose OTPs, passwords, PINs, or other authentication
   secrets.
8. Clearly distinguish what is stated in the evidence from what is unknown.
9. If information is missing, say that it is missing.
10. Use simple English suitable for a first-time investor.

Return ONLY valid JSON.
"""


def ai_reconstruct(evidence):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return {
            "enabled": False,
            "error": "Gemini API key is not configured."
        }

    prompt = f"""
Analyze the following user-provided incident evidence.

Create a structured reconstruction in simple English.

Return exactly this JSON structure:

{{
  "incident_narrative": "Short factual reconstruction",
  "claims": [
    {{
      "claim": "Claim found in evidence",
      "evidence": "Relevant evidence",
      "verification": "Not independently verified"
    }}
  ],
  "timeline": [
    {{
      "date_or_time": "Date/time if explicitly present",
      "event": "What happened",
      "source": "User-provided evidence"
    }}
  ],
  "missing_evidence": [
    "Important information that is not present"
  ],
  "plain_language_explanation": "Simple explanation of what the evidence appears to show",
  "documentation_questions": [
    "Useful questions the user should document or verify"
  ]
}}

Important:
- Do not invent information.
- Preserve dates, times, amounts, names, and other factual details exactly as provided.
- Do not alter factual values from the evidence.
- All generated explanatory text must be in simple English.
- "verification" must communicate that the claim has not been independently verified.
- Clearly distinguish evidence from interpretation.
- If information is unavailable, explicitly state that it is missing.

USER-PROVIDED EVIDENCE:
{evidence}
"""

    for attempt in range(3):
        try:
            client = genai.Client(api_key=api_key)

            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.2,
                    max_output_tokens=1800,
                    response_mime_type="application/json"
                )
            )

            raw = response.text.strip()

            if raw.startswith("```"):
                raw = raw.replace("```json", "", 1)
                raw = raw.replace("```", "", 1).strip()

            data = json.loads(raw)

            return {
                "enabled": True,
                "model": MODEL,
                "data": data
            }

        except Exception as exc:
            error = str(exc)

            if ("503" in error or "429" in error) and attempt < 2:
                time.sleep(1.5 * (attempt + 1))
                continue

            return {
                "enabled": False,
                "error": error
            }