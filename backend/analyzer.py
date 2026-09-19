import json
import re
from typing import Dict, Any

from openai import OpenAI


SYSTEM_PROMPT = """
You are ScamLens, an AI-assisted scam awareness and risk analysis system.

Your job is to analyze suspicious messages, emails, job offers, payment requests,
and links for potential scam or social-engineering indicators.

IMPORTANT:
- Do not claim certainty that something is a scam.
- Do not invent facts about the sender or organization.
- Treat the result as a risk assessment, not a legal or financial determination.
- Explain findings in simple language.
- Do not rely on grammar or spelling alone as evidence.
- A legitimate message can contain some warning signals.
- A scam can also be written professionally.

Analyze signals including:

1. Urgency or pressure
2. Requests for money or fees
3. Requests for sensitive information
4. Suspicious or mismatched links
5. Impersonation of banks, companies, authorities, etc.
6. Unrealistic rewards or prizes
7. Job/internship scams
8. Threats or fear-based language
9. Requests to bypass normal processes
10. Suspicious payment instructions

Return ONLY valid JSON.

The JSON must follow this exact structure:

{
    "risk_level": "LOW | MEDIUM | HIGH",
    "risk_score": 0,
    "summary": "Short explanation of the overall assessment.",
    "red_flags": [
        {
            "type": "Short category name",
            "icon": "Font Awesome icon name without fa- prefix",
            "explanation": "Simple explanation of why this is a warning sign."
        }
    ],
    "recommended_action": {
        "title": "Short action title.",
        "description": "Short explanation of what the user should do.",
        "steps": [
            "Action 1",
            "Action 2",
            "Action 3"
        ]
    },
    "simple_explanation": "Explain the situation like you are explaining it to a 15-year-old."
}

Risk score guidance:

0-29 = LOW
30-59 = MEDIUM
60-100 = HIGH

Do not interpret risk_score as a probability.

Keep the number of red_flags between 1 and 6.

Use these Font Awesome icon names when appropriate:

urgency -> bolt
payment -> credit-card
sensitive information -> user-lock
link -> link
impersonation -> user-secret
reward -> gift
job -> briefcase
threat -> triangle-exclamation
general -> circle-info
"""


def analyze_with_ai(message: str) -> Dict[str, Any]:
    """
    Analyze a message using the LLM.
    """

    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.1,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"""
Analyze the following content for ScamLens.

CONTENT:
{message}
"""
            }
        ]
    )

    content = response.choices[0].message.content

    result = json.loads(content)

    return normalize_result(result)


def normalize_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Make sure AI output always follows the format expected by the frontend.
    """

    level = str(
        result.get("risk_level", "MEDIUM")
    ).upper()

    if level not in ["LOW", "MEDIUM", "HIGH"]:
        level = "MEDIUM"

    try:
        score = int(result.get("risk_score", 50))
    except (ValueError, TypeError):
        score = 50

    score = max(0, min(score, 100))

    red_flags = result.get("red_flags", [])

    if not isinstance(red_flags, list):
        red_flags = []

    cleaned_flags = []

    for flag in red_flags[:6]:

        if not isinstance(flag, dict):
            continue

        flag_type = str(
            flag.get("type", "Warning sign")
        )

        icon = str(
            flag.get("icon", "circle-info")
        )

        explanation = str(
            flag.get(
                "explanation",
                "This may require additional verification."
            )
        )

        cleaned_flags.append({
            "type": flag_type,
            "icon": icon,
            "explanation": explanation
        })

    if not cleaned_flags:

        cleaned_flags.append({
            "type": "Limited signals detected",
            "icon": "circle-info",
            "explanation":
                "ScamLens did not identify many obvious scam indicators, but this does not guarantee that the message is safe."
        })

    action = result.get("recommended_action", {})

    if not isinstance(action, dict):
        action = {}

    title = str(
        action.get(
            "title",
            "Verify before proceeding."
        )
    )

    description = str(
        action.get(
            "description",
            "Verify the request independently before sharing information or sending money."
        )
    )

    steps = action.get("steps", [])

    if not isinstance(steps, list):
        steps = []

    steps = [
        str(step)
        for step in steps[:5]
    ]

    if not steps:

        steps = [
            "Verify the sender",
            "Do not share sensitive information",
            "Use an official source to confirm the request"
        ]

    summary = str(
        result.get(
            "summary",
            "ScamLens identified some signals that deserve attention."
        )
    )

    simple = str(
        result.get(
            "simple_explanation",
            "There are some things here that deserve a second look. Verify the message before acting."
        )
    )

    return {
        "risk_level": level,
        "risk_score": score,
        "summary": summary,

        "red_flags": cleaned_flags,

        "recommended_action": {
            "title": title,
            "description": description,
            "steps": steps
        },

        "simple_explanation": simple
    }


# ==========================================================
# LOCAL FALLBACK
# ==========================================================

def local_fallback_analysis(message: str) -> Dict[str, Any]:
    """
    Simple rule-based fallback.

    This is NOT a machine-learning model.
    It exists so ScamLens can still demonstrate basic functionality
    if the AI API is unavailable.
    """

    text = message.lower()

    flags = []
    score = 10

    # ----------------------------
    # Urgency
    # ----------------------------

    urgency_words = [
        "urgent",
        "immediately",
        "right now",
        "today",
        "within 2 hours",
        "within 24 hours",
        "limited time",
        "act now",
        "last chance"
    ]

    if any(word in text for word in urgency_words):

        flags.append({
            "type": "Urgency pressure",
            "icon": "bolt",
            "explanation":
                "The message pressures you to act quickly instead of giving you time to verify the request."
        })

        score += 18

    # ----------------------------
    # Payment
    # ----------------------------

    payment_words = [
        "pay",
        "payment",
        "fee",
        "processing fee",
        "registration fee",
        "deposit",
        "transfer money",
        "send money",
        "₹",
        "rs."
    ]

    if any(word in text for word in payment_words):

        flags.append({
            "type": "Payment request",
            "icon": "credit-card",
            "explanation":
                "The message appears to request money, a fee, or a payment."
        })

        score += 25

    # ----------------------------
    # Sensitive data
    # ----------------------------

    sensitive_words = [
        "otp",
        "password",
        "pin",
        "bank details",
        "card number",
        "cvv",
        "aadhaar",
        "pan card",
        "kyc"
    ]

    if any(word in text for word in sensitive_words):

        flags.append({
            "type": "Sensitive information",
            "icon": "user-lock",
            "explanation":
                "The message asks for information that can be sensitive or financially important."
        })

        score += 20

    # ----------------------------
    # Links
    # ----------------------------

    has_url = bool(
        re.search(
            r"(https?://|www\.|bit\.ly|tinyurl\.com)",
            text
        )
    )

    if has_url:

        flags.append({
            "type": "Link requires verification",
            "icon": "link",
            "explanation":
                "The message contains a link. Verify the destination independently before opening it."
        })

        score += 18

    # ----------------------------
    # Rewards
    # ----------------------------

    reward_words = [
        "winner",
        "won",
        "prize",
        "reward",
        "lottery",
        "cashback",
        "free money"
    ]

    if any(word in text for word in reward_words):

        flags.append({
            "type": "Unexpected reward",
            "icon": "gift",
            "explanation":
                "Unexpected prizes or financial rewards can be used to persuade people to act without verification."
        })

        score += 15

    # ----------------------------
    # Job scams
    # ----------------------------

    job_words = [
        "job",
        "internship",
        "work from home",
        "work-from-home",
        "salary",
        "hiring"
    ]

    if any(word in text for word in job_words):

        if any(
            word in text
            for word in [
                "fee",
                "payment",
                "registration",
                "deposit"
            ]
        ):

            flags.append({
                "type": "Job offer warning",
                "icon": "briefcase",
                "explanation":
                    "Job or internship offers that request upfront payment deserve extra verification."
            })

            score += 15

    # ----------------------------
    # Impersonation
    # ----------------------------

    organization_words = [
        "bank",
        "account",
        "government",
        "income tax",
        "police",
        "courier",
        "amazon",
        "flipkart"
    ]

    if any(word in text for word in organization_words):

        flags.append({
            "type": "Possible impersonation",
            "icon": "user-secret",
            "explanation":
                "The message appears to speak on behalf of an organization or authority."
        })

        score += 10

    score = min(score, 97)

    if score >= 70:
        level = "HIGH"

        summary = (
            "This message contains multiple warning signs "
            "commonly associated with scams."
        )

        action = {
            "title": "Pause before you act.",

            "description":
                "Do not click links, transfer money or share sensitive information until you independently verify the request.",

            "steps": [
                "Don't click suspicious links",
                "Don't share OTPs or passwords",
                "Verify through an official website",
                "Contact the organization directly"
            ]
        }

    elif score >= 40:
        level = "MEDIUM"

        summary = (
            "This message contains some warning signs "
            "worth checking before you act."
        )

        action = {
            "title": "Verify before proceeding.",

            "description":
                "Check the sender and verify the request independently.",

            "steps": [
                "Check who sent the message",
                "Avoid rushing into a decision",
                "Verify using an official source"
            ]
        }

    else:
        level = "LOW"

        summary = (
            "ScamLens found relatively few common "
            "scam indicators."
        )

        action = {
            "title": "No major red flags found.",

            "description":
                "This does not guarantee the message is safe. Verify unexpected requests before acting.",

            "steps": [
                "Check the sender",
                "Be cautious with links",
                "Never share sensitive credentials"
            ]
        }

    if not flags:

        flags.append({
            "type": "Limited signals detected",
            "icon": "circle-info",
            "explanation":
                "ScamLens did not identify many obvious scam indicators, but this does not guarantee that the message is safe."
        })

    if level == "HIGH":

        simple = (
            "This message is trying to make you act quickly "
            "or trust something without checking it first. "
            "Slow down and verify it yourself."
        )

    elif level == "MEDIUM":

        simple = (
            "There are a few things here that deserve a "
            "second look. Check where the message came from "
            "before doing anything."
        )

    else:

        simple = (
            "Nothing here strongly looks like a scam, "
            "but that does not automatically mean it is safe. "
            "Verify important requests."
        )

    return {
        "risk_level": level,
        "risk_score": score,
        "summary": summary,
        "red_flags": flags[:6],
        "recommended_action": action,
        "simple_explanation": simple
    }
# ==========================================================
# IMAGE / SCREENSHOT ANALYSIS
# ==========================================================

import base64
import mimetypes


def analyze_screenshot(image_bytes, filename):
    """
    Analyze a screenshot using AI Vision.
    If the Vision API is unavailable because of quota,
    return a safe fallback analysis so the demo still works.
    """

    client = OpenAI()

    mime_type, _ = mimetypes.guess_type(filename)

    if mime_type not in [
        "image/jpeg",
        "image/png",
        "image/webp"
    ]:
        mime_type = "image/jpeg"

    base64_image = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    image_data_url = (
        f"data:{mime_type};base64,{base64_image}"
    )

    prompt = """
You are ScamLens, an AI-assisted scam awareness system.

Analyze the uploaded screenshot for scam and
social-engineering warning signs.

Return ONLY valid JSON.

Use exactly this structure:

{
    "extracted_text": "Important visible text.",
    "risk_level": "LOW | MEDIUM | HIGH",
    "risk_score": 0,
    "summary": "Short explanation.",
    "red_flags": [
        {
            "type": "Short category name",
            "icon": "Font Awesome icon name without fa- prefix",
            "explanation": "Simple explanation."
        }
    ],
    "recommended_action": {
        "title": "Short action title.",
        "description": "What the user should do.",
        "steps": [
            "Action 1",
            "Action 2",
            "Action 3"
        ]
    },
    "simple_explanation": "Explain the situation simply."
}

Risk score:

0-29 = LOW
30-59 = MEDIUM
60-100 = HIGH

Keep red_flags between 1 and 6.

Useful icons:

urgency -> bolt
payment -> credit-card
sensitive information -> user-lock
link -> link
impersonation -> user-secret
reward -> gift
job -> briefcase
threat -> triangle-exclamation
general -> circle-info
"""

    try:

        response = client.responses.create(
            model="gpt-5.6-luna",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt
                        },
                        {
                            "type": "input_image",
                            "image_url": image_data_url,
                            "detail": "high"
                        }
                    ]
                }
            ]
        )

        result_text = response.output_text

        result = json.loads(result_text)

        result = normalize_result(result)

        return result

    except Exception as error:

        print(
            "Vision API unavailable. "
            "Using screenshot fallback:",
            str(error)
        )

        # =========================================
        # SCREENSHOT FALLBACK
        # =========================================

        fallback_result = {
            "extracted_text":
                "Screenshot received successfully. "
                "AI Vision analysis is currently unavailable.",

            "risk_level":
                "MEDIUM",

            "risk_score":
                50,

            "summary":
                "The screenshot was uploaded successfully, "
                "but detailed visual analysis is unavailable "
                "because the AI analysis service is currently "
                "out of credits.",

            "red_flags": [
                {
                    "type":
                        "External communication",

                    "icon":
                        "comment",

                    "explanation":
                        "The screenshot contains a message "
                        "or communication that should be "
                        "verified before taking action."
                },

                {
                    "type":
                        "Potential social engineering",

                    "icon":
                        "user-secret",

                    "explanation":
                        "Messages requesting urgent action, "
                        "personal information, payments, or "
                        "clicks should be independently verified."
                },

                {
                    "type":
                        "Verify before acting",

                    "icon":
                        "shield-halved",

                    "explanation":
                        "Do not share passwords, OTPs, "
                        "banking information, or payment details "
                        "until the sender has been verified."
                }
            ],

            "recommended_action": {
                "title":
                    "Verify before proceeding.",

                "description":
                    "Do not click links, send money, or "
                    "share sensitive information until you "
                    "confirm the message through an official source.",

                "steps": [
                    "Verify who sent the message",
                    "Avoid suspicious links or payments",
                    "Contact the organization through its official website or number"
                ]
            },

            "simple_explanation":
                "We received your screenshot, but the AI "
                "vision service is temporarily unavailable. "
                "Treat suspicious messages carefully and "
                "verify them through an official source."
        }

        return normalize_result(fallback_result)