"""Curated help for navigating the Samanvay single-window website.

Keep these answers limited to website navigation and features. Approval names,
fees, and legal applicability belong to the deterministic approvals registry.
"""
import re
from typing import Optional
from app.config import settings

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    types = None
    GEMINI_AVAILABLE = False


WEBSITE_ASSISTANT_SYSTEM_PROMPT = """
You are the Website Assistant for Samanvay (समन्वय) — a Maharashtra industrial
setup & regulatory approval navigation platform (prototype v1.0).

YOUR ONLY JOB: Help visitors understand and navigate the Samanvay WEBSITE itself.
You are NOT the regulatory/approvals engine — never answer questions about specific
approval fees, timelines, legal applicability, or clearance requirements. If asked
about those, say: "That's a regulatory question — please use the Setup & Approval
Assistant on the homepage and enter your project details so the rules engine can
give you a verified answer."

WHAT YOU KNOW ABOUT THIS WEBSITE:

- Samanvay has three portals: Applicant/Industry Portal, Officer/Government Officer
  Portal, and Admin/Apex Administrative Portal.
- Applicant Portal: Register Project, Dashboard, Applications, Incentives,
  Notifications, Profile, Projects, Renewals, Roadmap, Document Vault.
- Officer Portal: Work Queue, Application Review, Inspections, Escalations,
  SLA Monitoring.
- Admin Portal: Departments, Regulatory Rules, Audit Logs, Workload.
- To register: sign in via the Applicant/Industry Portal → open "Register Project."
  The wizard collects business details, project details, location, operations,
  environmental info, and utilities info, then generates an approval roadmap.
- The homepage has 6 quick-action cards: Start a New Industry, Find Required
  Approvals, Check Documents, Understand the Setup Process, Ask a Question,
  Explore Industries — each opens the Setup & Approval Assistant chat below it.
- Application status is checked under Applications or Dashboard after signing in.
- The site covers Maharashtra only and is powered by a deterministic rules engine
  (not free-form AI) for anything regulatory, so approvals/fees are always sourced
  and dated.

TONE & FORMAT:

- Short, direct, friendly answers (2-4 sentences).
- Plain English by default; add the Marathi term in parentheses only if the user
  writes in Marathi or asks for it.
- If ambiguous between "how do I use the site" and "what does regulation require,"
  ask one quick clarifying question.
- Never invent pages, buttons, or features not listed above.
- If you don't know, say so and point to the homepage quick-action cards or the
  Setup & Approval Assistant.
""".strip()


WEBSITE_FAQS = [
    {
        "patterns": [
            r"\bhow (?:do|can) i register(?: here)?[?.!]*$",
            r"\bhow (?:do|can) i register (?:a |my )?project\b",
            r"\bregister (?:a |my )?project\b",
            r"\bstart (?:a |my )?project application\b",
            r"\bproject registration (?:process|steps|wizard)\b",
        ],
        "question": "How do I register a project?",
        "answer": (
            "Sign in through the Applicant / Industry Portal and open Register Project. "
            "The wizard collects business details, project details, location, and operations, "
            "environmental, and utilities information. It then generates an approval roadmap."
        ),
    },
    {
        "patterns": [
            r"\bwhat can i do here\b",
            r"\bwhat can i do (?:on|with) (?:this|the) (?:website|portal|site)\b",
            r"\bwhat can (?:this|the) (?:website|portal|site) do\b",
            r"\bwhat does (?:this|the) (?:website|portal|site) do\b",
            r"\b(?:website|portal) features\b",
        ],
        "question": "What can I do on this website?",
        "answer": (
            "The homepage has six quick-action cards—Start a New Industry, Find Required Approvals, Check Documents, "
            "Understand the Setup Process, Ask a Question, and Explore Industries—and each opens the Setup & Approval Assistant. "
            "Applicant pages cover registration, dashboards, applications, incentives, notifications, profiles, projects, "
            "renewals, roadmaps, and the Document Vault; Officers have work queue, review, inspections, escalations, and SLA pages, "
            "while Admin pages cover departments, regulatory rules, audit logs, and workload."
        ),
    },
    {
        "patterns": [
            r"\bwhat(?:'s| is) the difference between (?:an? )?(?:applicant|officer)(?: login)? and (?:an? )?(?:applicant|officer)(?: login)?\b",
            r"\bapplicant (?:vs\.?|versus) officer\b",
            r"\bofficer login (?:different|difference)\b",
            r"\bapplicant login (?:different|difference)\b",
        ],
        "question": "How is an officer login different from an applicant login?",
        "answer": (
            "The Applicant / Industry Portal is for businesses registering and following their projects. "
            "The Officer / Government Officer Portal provides work queues and pages for reviewing "
            "applications, inspections, escalations, and service-level monitoring."
        ),
    },
    {
        "patterns": [
            r"\bwhere (?:can|do) i (?:check|see|track) (?:my )?(?:application|project) status\b",
            r"\bhow (?:can|do) i track (?:my )?(?:application|project)\b",
            r"\bapplication status\b",
        ],
        "question": "Where can I check my application status?",
        "answer": (
            "Sign in to the Applicant / Industry Portal and check the Applications or Dashboard pages "
            "for your project. The site also provides a Projects page."
        ),
    },
    {
        "patterns": [
            r"\b(?:where|how) (?:do|can) i (?:find|open|use) (?:the )?(?:setup & approval assistant|setup and approval assistant|approval assistant)\b",
            r"\bhomepage quick.?action cards\b",
            r"\bwhat are the quick.?action cards\b",
        ],
        "question": "What are the homepage quick-action cards?",
        "answer": (
            "The homepage has six cards: Start a New Industry, Find Required Approvals, Check Documents, "
            "Understand the Setup Process, Ask a Question, and Explore Industries. Each opens the Setup & Approval Assistant."
        ),
    },
    {
        "patterns": [
            r"\bwhere (?:is|can i find) (?:the )?(?:document vault|vault)\b",
            r"\bhow (?:do|can) i (?:check|find) documents\b",
        ],
        "question": "Where can I find my documents?",
        "answer": "Sign in through the Applicant / Industry Portal and open Document Vault.",
    },
    {
        "patterns": [
            r"\b(?:does|is) (?:this|the) (?:website|site|platform) (?:only )?(?:cover|for) maharashtra\b",
            r"\bwhich state(?:s)? (?:does|do) (?:this|the) (?:website|site|platform) cover\b",
        ],
        "question": "Which state does Samanvay cover?",
        "answer": "Samanvay currently covers Maharashtra only.",
    },
    {
        "patterns": [
            r"\b(?:is|does) (?:the )?(?:setup & approval assistant|setup and approval assistant|rules engine) (?:use|using|an? )?(?:free.?form )?ai\b",
            r"\bhow does the deterministic rules engine work\b",
            r"\b(?:deterministic|sourced and dated) regulatory guidance\b",
        ],
        "question": "How does regulatory guidance work on Samanvay?",
        "answer": (
            "Regulatory guidance is produced by the deterministic rules engine, not free-form AI. "
            "Enter your project details in the Setup & Approval Assistant to receive sourced, dated guidance."
        ),
    },
    {
        "patterns": [
            r"\bwhat can (?:an? )?officer do\b",
            r"\bofficer (?:dashboard|work queue|queue|review|inspection|escalation|sla)\b",
        ],
        "question": "What does the officer portal provide?",
        "answer": (
            "The officer area includes a queue, application review, inspections, escalations, "
            "and SLA monitoring."
        ),
    },
    {
        "patterns": [
            r"\bwhat can (?:an? )?admin do\b",
            r"\badmin (?:dashboard|portal|departments|regulatory rules|audit logs|workload)\b",
        ],
        "question": "What does the admin portal provide?",
        "answer": (
            "The Admin / Apex Administrative Portal includes pages for departments, "
            "regulatory rules, audit logs, and workload."
        ),
    },
]


def find_website_faq(message: str) -> Optional[dict]:
    """Return the first matching website FAQ, if the message asks about site use."""
    normalized = message.lower().strip()
    for faq in WEBSITE_FAQS:
        if any(re.search(pattern, normalized) for pattern in faq["patterns"]):
            return faq
    return None


REGULATORY_REDIRECT = (
    "That's a regulatory question — please use the Setup & Approval Assistant on the homepage "
    "and enter your project details so the rules engine can give you a verified answer."
)

AMBIGUOUS_QUESTION = (
    "Are you asking how to find the Setup & Approval Assistant on the website, or what regulatory "
    "requirements apply to your project?"
)

WEBSITE_FALLBACK = (
    "I can help with using the Samanvay website. Try one of the homepage quick-action cards or ask "
    "the Setup & Approval Assistant for project-specific regulatory guidance."
)

REGULATORY_PATTERNS = [
    r"\b(fee|fees|charges|processing time|timeline|how long|legal|law|applicab(?:le|ility)|clearance|permit|licen[cs]e|approval requirements|approvals do i need|required approvals|regulatory requirement)\b",
]


def answer_website_question(message: str) -> dict:
    """Answer within the Website Assistant scope; never evaluate regulatory rules."""
    faq = find_website_faq(message)
    if faq:
        return {"response_type": "website_faq", "message": faq["answer"]}

    normalized = message.lower().strip()
    if re.search(r"\b(approval|approvals|clearance|permit|license|licence|requirement|documents?)\b", normalized) and re.search(
        r"\b(where|how|what|which|can|do i|should i)\b", normalized
    ) and not re.search(r"\b(fee|fees|timeline|processing time|legally|required|applicable|applicability|need for my|do i need)\b", normalized):
        return {"response_type": "clarification", "message": AMBIGUOUS_QUESTION}

    if any(re.search(pattern, normalized) for pattern in REGULATORY_PATTERNS):
        return {"response_type": "regulatory_redirect", "message": REGULATORY_REDIRECT}

    return {"response_type": "fallback", "message": _generate_website_answer(message)}


def _generate_website_answer(message: str) -> str:
    """Use Gemini only for unmatched website-help questions, with a safe static fallback."""
    api_key = settings.GEMINI_API_KEY
    if not api_key or not GEMINI_AVAILABLE:
        return WEBSITE_FALLBACK

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=message,
            config=types.GenerateContentConfig(
                temperature=0.2,
                system_instruction=WEBSITE_ASSISTANT_SYSTEM_PROMPT,
            ),
        )
        return response.text.strip() if response.text and response.text.strip() else WEBSITE_FALLBACK
    except Exception:
        return WEBSITE_FALLBACK
