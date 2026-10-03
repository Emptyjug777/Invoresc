import re


PATTERNS = [
    {
        "id": "guaranteed_return",
        "title": "Guaranteed or unusually certain returns",
        "keywords": [
            "guaranteed return",
            "guaranteed returns",
            "guaranteed profit",
            "guaranteed 30%",
            "guaranteed 20%",
            "guaranteed 40%",
            "guaranteed 50%",
            "guaranteed",
            "fixed return",
            "fixed profit",
            "risk free",
            "risk-free",
            "zero risk",
            "no risk",
        ],
        "severity": "high",
        "explanation": "The content uses language suggesting unusually certain or risk-free financial outcomes.",
    },
    {
        "id": "urgency",
        "title": "Urgency or pressure",
        "keywords": [
            "limited slots",
            "act now",
            "today only",
            "last chance",
            "urgent",
            "immediately",
            "offer expires",
        ],
        "severity": "medium",
        "explanation": "Pressure to act quickly can reduce the opportunity to independently verify a financial claim.",
    },
    {
        "id": "regulatory_claim",
        "title": "Regulatory or authority claim",
        "keywords": [
            "sebi approved",
            "sebi registered",
            "government approved",
            "rbi approved",
            "officially approved",
        ],
        "severity": "high",
        "explanation": "The sender invokes a regulatory or government authority. Such claims should be independently verified.",
    },
    {
        "id": "additional_payment",
        "title": "Additional payment requested",
        "keywords": [
            "processing fee",
            "withdrawal fee",
            "release fee",
            "pay to withdraw",
            "pay ₹",
            "pay rs",
            "pay inr",
        ],
        "severity": "high",
        "explanation": "A request for additional money before releasing supposed investment proceeds is a significant warning indicator.",
    },
    {
        "id": "remote_access",
        "title": "Remote-access or screen-sharing request",
        "keywords": [
            "install this application",
            "install the app",
            "remote access",
            "screen share",
            "share your screen",
            "anydesk",
            "teamviewer",
        ],
        "severity": "high",
        "explanation": "Requests for remote access or screen sharing can expose sensitive information and should be treated cautiously.",
    },
    {
        "id": "credential_request",
        "title": "Sensitive credential request",
        "keywords": [
            "share otp",
            "send otp",
            "tell me your otp",
            "share password",
            "send password",
            "share pin",
            "send pin",
        ],
        "severity": "high",
        "explanation": "Requests for authentication credentials or OTPs create a significant security risk.",
    },
    {
        "id": "informal_channel",
        "title": "Informal communication channel",
        "keywords": [
            "telegram",
            "whatsapp",
            "contact manager",
            "message me privately",
        ],
        "severity": "medium",
        "explanation": "Moving financial communication to informal channels can make independent verification more difficult.",
    },
]


def normalize(text):
    return re.sub(r"\s+", " ", text.lower()).strip()


def find_patterns(text):
    text = normalize(text)
    found = []

    for pattern in PATTERNS:
        matches = []

        for keyword in pattern["keywords"]:
            if keyword in text:
                matches.append(keyword)

        if matches:
            found.append(
                {
                    "id": pattern["id"],
                    "title": pattern["title"],
                    "severity": pattern["severity"],
                    "explanation": pattern["explanation"],
                    "matched_terms": matches,
                }
            )

    return found


def extract_claims(text):
    claims = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        low = line.lower()

        words = [
            "guaranteed",
            "approved",
            "registered",
            "profit",
            "return",
            "withdraw",
            "investment",
            "payment",
            "fee",
        ]

        if any(word in low for word in words):
            claims.append(
                {
                    "claim": line,
                    "source": "User-provided evidence",
                    "verification": "Not independently verified",
                }
            )

    return claims[:15]


def build_timeline(text):
    timeline = []

    pattern = re.compile(
        r"(\d{1,2}\s+"
        r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        r"\.?"
        r"(?:,\s*\d{1,2}:\d{2})?"
        r"(?:\s*(?:AM|PM))?)",
        re.IGNORECASE,
    )

    matches = list(pattern.finditer(text))

    if not matches:
        return [
            {
                "date": "Unspecified",
                "event": text.strip(),
            }
        ] if text.strip() else []

    for i, match in enumerate(matches):
        date = match.group(1).strip()

        start = match.end()
        end = (
            matches[i + 1].start()
            if i + 1 < len(matches)
            else len(text)
        )

        event = text[start:end].strip()
        event = re.sub(r"\s+", " ", event)

        if event:
            timeline.append(
                {
                    "date": date,
                    "event": event,
                }
            )

    return timeline[:20]


def calculate_score(patterns):
    score = 0

    for pattern in patterns:
        if pattern["severity"] == "high":
            score += 25
        elif pattern["severity"] == "medium":
            score += 15
        else:
            score += 5

    return min(score, 100)


def get_level(score):
    if score >= 60:
        return "HIGH"

    if score >= 30:
        return "ELEVATED"

    if score > 0:
        return "MODERATE"

    return "NO SPECIFIC INDICATORS"


def build_actions(patterns):
    ids = {pattern["id"] for pattern in patterns}

    actions = [
        "Preserve the original messages, screenshots, receipts and relevant documents.",
        "Do not send additional money until the situation has been independently verified.",
        "Do not share OTPs, passwords, PINs or other authentication credentials.",
    ]

    if "remote_access" in ids:
        actions.append(
            "Do not install unknown remote-access software or share your device screen."
        )

    if "regulatory_claim" in ids:
        actions.append(
            "Independently verify regulatory or institutional claims through appropriate official channels."
        )

    if "additional_payment" in ids:
        actions.append(
            "Document any request for additional payment, including the amount and stated reason."
        )

    actions.append(
        "If money has already been transferred, follow the appropriate official fraud or investor-protection process."
    )

    return actions


def analyze_incident(text):
    text = text.strip()

    if not text:
        return {
            "success": False,
            "error": "No incident evidence was provided.",
        }

    patterns = find_patterns(text)
    claims = extract_claims(text)
    timeline = build_timeline(text)

    score = calculate_score(patterns)
    level = get_level(score)

    if patterns:
        summary = (
            f"The supplied evidence contains {len(patterns)} potentially "
            f"concerning pattern(s). The assessment is {level.lower()} "
            "based on the indicators detected."
        )
    else:
        summary = (
            "No predefined risk indicators were detected in the supplied "
            "text. This does not establish that the content is safe."
        )

    confidence_note = (
        "This is an indicator-based assessment of the supplied "
        "evidence. It does not establish that fraud has occurred."
    )

    limitations = [
        "The analysis is based only on information supplied by the user.",
        "Regulatory or institutional claims have not been independently verified.",
        "The system does not provide investment recommendations.",
    ]

    return {
        "success": True,
        "assessment": {
            "level": level,
            "indicator_score": score,
            "confidence_note": confidence_note,
        },
        "summary": summary,
        "risk_indicators": patterns,
        "claims": claims,
        "timeline": timeline,
        "safe_actions": build_actions(patterns),
        "limitations": limitations,
    }