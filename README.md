# 🔍 ScamLens

### Think before you click.

ScamLens is an AI-assisted scam awareness tool that helps users identify potential scam and social-engineering attempts in suspicious messages and screenshots.

Instead of simply labeling a message as "safe" or "scam", ScamLens provides a risk assessment, explains the warning signs it detects, and tells the user what they should do next.

---

## 🚨 Problem

Online scams are becoming increasingly convincing.

Users receive suspicious:

- SMS messages
- WhatsApp messages
- Emails
- Job offers
- Banking alerts
- Prize notifications
- Payment requests
- Delivery messages
- Suspicious links
- Impersonation attempts

The problem is not only detecting scams.

The bigger problem is that many users don't know **why** a message is suspicious or what they should do next.

---

## 💡 Solution

ScamLens acts as a simple first layer of scam awareness.

Users can:

1. Paste a suspicious message
2. Upload a screenshot
3. Analyze the content
4. Receive a risk score
5. See the warning signs detected
6. Understand why those signs are suspicious
7. Get practical safety recommendations

### Example

Instead of simply saying:

> ❌ SCAM

ScamLens can explain:

> ⚠️ Medium Risk — 58/100

**Warning signs detected:**

- Urgency pressure
- Sensitive information request
- Possible impersonation

**Recommended action:**

> Verify the sender through an official channel before sharing information or making a payment.

---

# ✨ Features

## 📝 Message Analysis

Paste suspicious text and receive an AI-assisted risk assessment.

## 📸 Screenshot Analysis

Upload screenshots of suspicious messages, emails, payment requests or alerts.

## 📊 Risk Score

ScamLens provides a score from 0–100.

| Score | Risk |
|---|---|
| 0–29 | LOW |
| 30–59 | MEDIUM |
| 60–100 | HIGH |

## 🚩 Warning Sign Detection

ScamLens identifies patterns such as:

- Urgency and pressure
- Payment requests
- Sensitive information requests
- Suspicious links
- Possible impersonation
- Fake rewards
- Suspicious job offers
- Threats

## 🧠 Explainable Results

Instead of only producing a classification, ScamLens explains why a message may be risky.

## 🛡️ Safety Recommendations

Users receive practical steps such as:

- Verify the sender
- Avoid suspicious links
- Don't share OTPs or passwords
- Verify payment requests
- Contact organizations through official channels

## 🔄 Local Fallback

If the AI service is temporarily unavailable, ScamLens can provide a fallback safety assessment instead of crashing.

---

# 🏗️ Architecture

                    ┌──────────────────┐
                    │      User        │
                    └────────┬─────────┘
                             │
                 ┌───────────┴───────────┐
                 │                       │
          Text Message              Screenshot
                 │                       │
                 └───────────┬───────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Flask Backend  │
                    └────────┬─────────┘
                             │
                     ┌───────┴───────┐
                     │               │
                     ▼               ▼
              Text Analysis    Image Analysis
                     │               │
                     └───────┬───────┘
                             ▼
                    ┌──────────────────┐
                    │   Scam Analysis  │
                    │                  │
                    │ Risk Score       │
                    │ Warning Signs    │
                    │ Explanation      │
                    │ Recommendations  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Results Dashboard│
                    └──────────────────┘

# 🛠️ Tech Stack

## Frontend

- HTML5
- CSS3
- JavaScript
- Font Awesome

## Backend

- Python
- Flask
- Flask-CORS

## AI

- OpenAI API
- AI-assisted text analysis
- Vision-based screenshot analysis

## Supporting Libraries

- python-dotenv
- Pillow
- pytesseract


# 🚀 Future Improvements

ScamLens can be extended into a more comprehensive scam-awareness platform.

### 📷 Advanced Screenshot Analysis
- OCR-based text extraction from screenshots
- Automatic detection of suspicious links, phone numbers, and email addresses
- Better analysis of screenshots containing multiple messages or complex layouts

### 🔗 Link Intelligence
- Suspicious domain detection
- URL reputation checking
- Shortened-link detection
- Domain impersonation detection

### 🌍 Multilingual Scam Detection
- Support for multiple Indian and international languages
- Detection of region-specific scam patterns
- Localized safety recommendations

### 📱 Browser Extension
Allow users to analyze suspicious web pages and links directly from their browser.

### 📧 Email Analysis
Allow users to analyze suspicious emails and identify common phishing and social-engineering patterns.

### 🧠 Scam Pattern Intelligence
Build a continuously improving database of common scam patterns, tactics, and social-engineering techniques.

### 👥 Community Reporting
Allow users to anonymously report suspicious messages and contribute new scam patterns to a shared intelligence system.

### 📊 Threat Intelligence Integration
Integrate trusted threat-intelligence sources to improve detection of malicious domains, URLs, and known scam campaigns.

# ⚠️ Disclaimer

ScamLens provides an AI-assisted risk assessment for educational and awareness purposes.

It does not guarantee that a message is fraudulent or legitimate.

Users should independently verify important financial, legal, employment, banking, or account-related communications through official channels.
