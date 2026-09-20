/* =========================================
   SCAMLENS FRONTEND
========================================= */


/* =========================================
   ELEMENTS
========================================= */

const messageInput = document.getElementById("messageInput");
const charCount = document.getElementById("charCount");
const analyzeButton = document.getElementById("analyzeButton");

const resultsSection = document.getElementById("results");

const riskScore = document.getElementById("riskScore");
const riskLevel = document.getElementById("riskLevel");
const riskSummary = document.getElementById("riskSummary");

const flagsList = document.getElementById("flagsList");
const flagCount = document.getElementById("flagCount");

const actionTitle = document.getElementById("actionTitle");
const actionDescription = document.getElementById("actionDescription");
const actionList = document.getElementById("actionList");

const simpleExplanation = document.getElementById("simpleExplanation");

const ringProgress = document.getElementById("ringProgress");

const screenshotInput =
    document.getElementById("screenshotInput");

const fileName =
    document.getElementById("fileName");


// Screenshot filename
screenshotInput.addEventListener("change", () => {

    if (!screenshotInput.files.length) {
        fileName.textContent = "";
        return;
    }

    fileName.textContent =
        screenshotInput.files[0].name;
});
/* =========================================
   EXAMPLE DATA
========================================= */

const examples = {

    bank: `URGENT: Your bank account will be suspended today due to incomplete KYC verification.

Verify your account immediately to avoid permanent suspension:

http://secure-bank-verify.example.com

Failure to verify within 2 hours will result in account closure.`,

    prize: `Congratulations! 🎉

You have been selected as the lucky winner of ₹50,000 in our special customer reward program.

To claim your prize, please pay a refundable processing fee of ₹499.

Send the payment and your bank details immediately to confirm your reward.`,

    job: `Congratulations! Your profile has been selected for a work-from-home internship with a monthly salary of ₹35,000.

To confirm your position, please pay a one-time registration fee of ₹2,499.

Send your Aadhaar card, PAN card and payment screenshot to proceed.

Limited positions available. Apply within 2 hours.`
};


/* =========================================
   CHARACTER COUNTER
========================================= */

messageInput.addEventListener("input", () => {

    const length = messageInput.value.length;

    charCount.textContent = `${length} / 5000`;

});


/* =========================================
   SCROLL
========================================= */

function scrollToAnalyzer() {

    document
        .getElementById("analyzer")
        .scrollIntoView({
            behavior: "smooth"
        });

}


/* =========================================
   CLEAR MESSAGE
========================================= */

function clearMessage() {

    messageInput.value = "";

    charCount.textContent = "0 / 5000";

    messageInput.focus();

}


/* =========================================
   LOAD EXAMPLE
========================================= */

function loadExample(type) {

    messageInput.value = examples[type];

    charCount.textContent =
        `${messageInput.value.length} / 5000`;

    scrollToAnalyzer();

}


/* =========================================
   MESSAGE TYPE TABS
========================================= */

const tabs = document.querySelectorAll(".type-tab");

tabs.forEach(tab => {

    tab.addEventListener("click", () => {

        tabs.forEach(t => {
            t.classList.remove("active");
        });

        tab.classList.add("active");

    });

});


/* =========================================
   ANALYSIS
========================================= */

async function analyzeMessage() {

    const message = messageInput.value.trim();
    const screenshot = screenshotInput.files[0];

    console.log("Message:", message);
    console.log("Screenshot:", screenshot);

    // Nothing selected
    if (!message && !screenshot) {

        messageInput.focus();

        messageInput.style.border =
            "1px solid rgba(255,93,108,0.5)";

        setTimeout(() => {
            messageInput.style.border = "";
        }, 1500);

        return;
    }

    analyzeButton.disabled = true;
    analyzeButton.classList.add("loading");

    try {

        let response;

        // =====================================
        // SCREENSHOT ANALYSIS
        // =====================================

        if (screenshot) {

            console.log("Sending screenshot to backend...");

            const formData = new FormData();

            formData.append(
                "image",
                screenshot
            );

            response = await fetch(
                "https://scamlens-backend-l1m6.onrender.com/analyze-image",
                {
                    method: "POST",
                    body: formData
                }
            );
        }

        // =====================================
        // TEXT ANALYSIS
        // =====================================

        else {

            console.log("Sending text to backend...");

            response = await fetch(
                "https://scamlens-backend-l1m6.onrender.com/analyze",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        text: message
                    })
                }
            );
        }

        const result = await response.json();

        console.log("Backend result:", result);

        if (!response.ok) {
            throw new Error(
                result.error ||
                "Analysis failed."
            );
        }

        showResults(result);

    } catch (error) {

        console.error(
            "ScamLens error:",
            error
        );

        alert(
            error.message ||
            "Unable to analyze."
        );

    } finally {

        analyzeButton.disabled = false;
        analyzeButton.classList.remove("loading");
    }
}

/* =========================================
   DEMO ANALYSIS
========================================= */

function generateDemoAnalysis(message) {

    const lower = message.toLowerCase();

    let flags = [];

    let score = 18;


    /* Urgency */

    if (
        lower.includes("urgent") ||
        lower.includes("immediately") ||
        lower.includes("today") ||
        lower.includes("within") ||
        lower.includes("limited")
    ) {

        flags.push({

            icon: "fa-bolt",

            title: "Urgency pressure",

            description:
                "The message pushes you to act quickly instead of giving you time to verify the request."

        });

        score += 18;

    }


    /* Payment */

    if (
        lower.includes("pay") ||
        lower.includes("payment") ||
        lower.includes("fee") ||
        lower.includes("₹") ||
        lower.includes("money")
    ) {

        flags.push({

            icon: "fa-credit-card",

            title: "Payment request",

            description:
                "The sender asks for money before you receive the promised reward, service or opportunity."

        });

        score += 24;

    }


    /* Sensitive information */

    if (
        lower.includes("otp") ||
        lower.includes("password") ||
        lower.includes("bank details") ||
        lower.includes("aadhaar") ||
        lower.includes("pan card") ||
        lower.includes("kyc")
    ) {

        flags.push({

            icon: "fa-user-lock",

            title: "Sensitive information",

            description:
                "The message requests personal or financial information that should not be shared casually."

        });

        score += 20;

    }


    /* Links */

    if (
        lower.includes("http") ||
        lower.includes("www.") ||
        lower.includes("bit.ly") ||
        lower.includes("link")
    ) {

        flags.push({

            icon: "fa-link",

            title: "Suspicious link",

            description:
                "The message contains a link that could redirect you to an unverified website."

        });

        score += 20;

    }


    /* Prize / reward */

    if (
        lower.includes("winner") ||
        lower.includes("won") ||
        lower.includes("prize") ||
        lower.includes("reward") ||
        lower.includes("₹50,000")
    ) {

        flags.push({

            icon: "fa-gift",

            title: "Unexpected reward",

            description:
                "Unexpected prizes or rewards are commonly used to make people act without verifying the sender."

        });

        score += 15;

    }


    /* Impersonation */

    if (
        lower.includes("bank") ||
        lower.includes("account") ||
        lower.includes("kyc") ||
        lower.includes("government")
    ) {

        flags.push({

            icon: "fa-user-secret",

            title: "Possible impersonation",

            description:
                "The message appears to speak on behalf of an organization or authority."

        });

        score += 10;

    }


    /* Job scam */

    if (
        lower.includes("job") ||
        lower.includes("internship") ||
        lower.includes("salary") ||
        lower.includes("work-from-home")
    ) {

        flags.push({

            icon: "fa-briefcase",

            title: "Job offer warning",

            description:
                "Unexpected job offers that request upfront fees or sensitive documents deserve extra verification."

        });

        score += 18;

    }


    /* Default */

    if (flags.length === 0) {

        flags.push({

            icon: "fa-circle-info",

            title: "Limited signals detected",

            description:
                "The message does not contain many obvious scam indicators, but that does not guarantee it is safe."

        });

        score = 25;

    }


    score = Math.min(score, 97);


    let level = "LOW";
    let summary =
        "We found relatively few common scam indicators.";

    if (score >= 70) {

        level = "HIGH";

        summary =
            "This message contains multiple warning signs commonly associated with scams.";

    }

    else if (score >= 40) {

        level = "MEDIUM";

        summary =
            "This message contains some warning signs worth checking before you act.";

    }


    return {

        score,

        level,

        summary,

        flags,

        action: getAction(level, flags),

        simple:
            generateSimpleExplanation(level, flags)

    };

}


/* =========================================
   ACTION GENERATOR
========================================= */

function getAction(level, flags) {

    if (level === "HIGH") {

        return {

            title: "Pause before you act.",

            description:
                "Do not click links, transfer money or share sensitive information until you independently verify the request.",

            steps: [

                "Don't click suspicious links",

                "Don't share OTPs or passwords",

                "Verify through the official website",

                "Contact the organization directly"

            ]

        };

    }


    if (level === "MEDIUM") {

        return {

            title: "Verify before proceeding.",

            description:
                "Some parts of this message deserve caution. Check the sender and verify the request independently.",

            steps: [

                "Check who sent the message",

                "Avoid rushing into a decision",

                "Verify using an official source"

            ]

        };

    }


    return {

        title: "No major red flags found.",

        description:
            "ScamLens didn't find many common warning signs, but always verify unexpected requests before sharing information or money.",

        steps: [

            "Check the sender",

            "Be cautious with links",

            "Never share sensitive credentials"

        ]

    };

}


/* =========================================
   SIMPLE EXPLANATION
========================================= */

function generateSimpleExplanation(level, flags) {

    if (level === "HIGH") {

        return "This message is trying to make you act quickly or trust something without checking it first. Slow down, don't send money or personal information, and verify the request yourself.";

    }

    if (level === "MEDIUM") {

        return "There are a few things here that deserve a second look. It might be legitimate, but don't act until you've checked where the message came from.";

    }

    return "Nothing here strongly screams scam, but that doesn't mean it's automatically safe. When money or personal information is involved, verify first.";

}


/* =========================================
   SHOW RESULTS
========================================= */

function showResults(data) {

    /* =========================
       NORMALIZE BACKEND DATA
    ========================= */

    const score =
        data.score ??
        data.risk_score ??
        0;

    const level =
        data.level ??
        data.risk_level ??
        data.risk ??
        "LOW";

    const summary =
        data.summary ??
        data.risk_summary ??
        "ScamLens completed the analysis.";

    const flags =
        Array.isArray(data.flags)
            ? data.flags
            : Array.isArray(data.warning_signs)
                ? data.warning_signs
                : Array.isArray(data.red_flags)
                    ? data.red_flags
                    : [];

    const action =
        data.action ?? {
            title: "Verify before proceeding.",
            description:
                "Be cautious and independently verify the request before sharing information, clicking links, or sending money.",
            steps: [
                "Check who sent the message",
                "Avoid clicking suspicious links",
                "Verify through an official source"
            ]
        };

    const simple =
        data.simple ??
        data.simple_explanation ??
        data.explanation ??
        "Take a moment to verify this message before taking any action.";


    /* =========================
       RISK
    ========================= */

    riskScore.textContent = score;

    riskLevel.textContent =
        `${level} RISK`;

    riskLevel.className =
        `risk-level ${String(level).toLowerCase()}`;

    riskSummary.textContent = summary;


    /* =========================
       RISK RING
    ========================= */

    const circumference =
        2 * Math.PI * 68;

    const offset =
        circumference -
        (Number(score) / 100) * circumference;

    ringProgress.style.strokeDashoffset =
        offset;


    /* Ring color */

    if (String(level).toUpperCase() === "HIGH") {

        ringProgress.style.stroke =
            "var(--danger)";

    } else if (
        String(level).toUpperCase() === "MEDIUM"
    ) {

        ringProgress.style.stroke =
            "var(--warning)";

    } else {

        ringProgress.style.stroke =
            "var(--accent)";
    }


    /* =========================
       WARNING FLAGS
    ========================= */

    flagsList.innerHTML = "";

    flags.forEach(flag => {

    const element = document.createElement("div");

    element.className = "flag";

    // Handle both object and string flags
    const title =
        typeof flag === "string"
            ? flag
            : flag.title ||
              flag.name ||
              flag.type ||
              "Warning sign";

    const description =
        typeof flag === "string"
            ? ""
            : flag.description ||
              flag.reason ||
              flag.explanation ||
              "";

    let icon = "fa-triangle-exclamation";

if (typeof flag === "object") {

    const title =
        (flag.title ||
         flag.name ||
         flag.type ||
         "").toLowerCase();

    if (
        title.includes("urgency") ||
        title.includes("pressure")
    ) {
        icon = "fa-bolt";
    }

    else if (
        title.includes("payment") ||
        title.includes("money") ||
        title.includes("financial")
    ) {
        icon = "fa-credit-card";
    }

    else if (
        title.includes("sensitive") ||
        title.includes("information") ||
        title.includes("personal")
    ) {
        icon = "fa-user-shield";
    }

    else if (
        title.includes("link") ||
        title.includes("url")
    ) {
        icon = "fa-link";
    }

    else if (
        title.includes("impersonation") ||
        title.includes("identity") ||
        title.includes("authority")
    ) {
        icon = "fa-user-secret";
    }
}

    element.innerHTML = `
        <div class="flag-icon">
            <i class="fa-solid ${icon}"></i>
        </div>

        <div>
            <strong>${title}</strong>

            ${
                description
                    ? `<p>${description}</p>`
                    : ""
            }
        </div>
    `;

    flagsList.appendChild(element);
});


    flagCount.textContent =
        `${flags.length} ${
            flags.length === 1
                ? "flag"
                : "flags"
        }`;


    /* =========================
       ACTION
    ========================= */

    actionTitle.textContent =
        action.title || "Verify before proceeding.";

    actionDescription.textContent =
        action.description || "";

    actionList.innerHTML = "";

    const steps =
        Array.isArray(action.steps)
            ? action.steps
            : [];

    steps.forEach(step => {

        const element =
            document.createElement("span");

        element.innerHTML = `
            <i class="fa-solid fa-check"></i>
            ${step}
        `;

        actionList.appendChild(element);
    });


    /* =========================
       SIMPLE EXPLANATION
    ========================= */

    simpleExplanation.textContent =
        simple;


    /* =========================
       SHOW RESULTS
    ========================= */

    resultsSection.classList.remove("hidden");

    setTimeout(() => {

        resultsSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    }, 100);
}

/* =========================================
   SCAN AGAIN
========================================= */

function scanAgain() {

    resultsSection.classList.add("hidden");

    scrollToAnalyzer();

    setTimeout(() => {

        messageInput.focus();

    }, 600);

}


/* =========================================
   WAIT HELPER
========================================= */

function wait(ms) {

    return new Promise(resolve =>
        setTimeout(resolve, ms)
    );

}


/* =========================================
   DEMO KEYBOARD SHORTCUT
========================================= */

messageInput.addEventListener(
    "keydown",
    event => {

        if (
            (event.ctrlKey || event.metaKey) &&
            event.key === "Enter"
        ) {

            analyzeMessage();

        }

    }
);
analyzeButton.addEventListener("click", analyzeMessage);
