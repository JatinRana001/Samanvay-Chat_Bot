import os
from typing import Optional
from app.config import settings
from app.schemas.approval import ApprovalRecommendationResult

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    types = None
    GEMINI_AVAILABLE = False

class GeminiExplanationService:
    """
    Synthesizes plain-language explanations from deterministic rules engine output.
    Strictly constrained by prompt engineering not to invent approvals, fees, or timelines.
    """

    @classmethod
    def generate_explanation(cls, recommendation: ApprovalRecommendationResult, sources=None) -> str:
        api_key = settings.GEMINI_API_KEY
        
        # Fallback deterministic structured formatter if Gemini API key is not provided
        if not api_key or not GEMINI_AVAILABLE:
            return cls._format_deterministic_explanation(recommendation)

        try:
            system_instruction = (
                    "You are the explanation synthesizer for Samanvay (समन्वय) — Maharashtra Industry Setup Assistant. "
                    "You will receive verified structured output from our deterministic rules engine. "
                    "CRITICAL RULES:\n"
                    "1. You must ONLY explain the structured database records provided in the context.\n"
                    "2. You must NEVER invent, infer, or hallucinate approvals, fees, timelines, or legal requirements not explicitly present in the data.\n"
                    "3. Every regulatory claim must display its official source and last_verified date.\n"
                    "4. When applicability is uncertain, use hedged language ('may apply depending on...', 'further verification required...').\n"
                    "5. Structure the output clearly: Business Profile, Basic Setup Steps, Applicable Approvals, Document Checklist, Next Steps, and Disclaimer. "
                    "Do not introduce regulatory claims absent from the structured records or retrieved documents. Include source and last_verified for every regulatory claim."
            )
            client = genai.Client(api_key=api_key)

            sources = sources or []
            source_context = "\n".join(
                f"- {item.title}; source: {item.source_url}; last verified: {item.last_verified}; clause: {item.chunk_text}"
                for item in sources
            ) or "No additional retrieved regulatory clause matched. Use only the approval records below."
            prompt = (
                f"Explain the following verified regulatory recommendation for a business in Maharashtra:\n\n"
                f"Business Profile:\n{recommendation.business_profile.model_dump_json()}\n\n"
                f"Approvals:\n{[a.dict() for a in recommendation.approvals]}\n\n"
                f"Setup Steps:\n{[s.dict() for s in recommendation.basic_setup_steps]}\n\n"
                f"Document Checklist:\n{recommendation.document_checklist}\n\n"
                f"Retrieved regulatory documents:\n{source_context}\n"
            )

            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    system_instruction=system_instruction,
                ),
            )
            return response.text or cls._format_deterministic_explanation(recommendation)
        except Exception as e:
            # Graceful fallback to deterministic explanation upon API error
            return cls._format_deterministic_explanation(recommendation)

    @classmethod
    def _format_deterministic_explanation(cls, r: ApprovalRecommendationResult) -> str:
        p = r.business_profile
        lines = []
        lines.append(f"### 📋 Business Profile Assessment: {p.industry or 'Industrial Unit'} ({p.district or 'Maharashtra'})")
        lines.append(f"- **Sector / Activity:** {p.industry or 'Manufacturing'}")
        lines.append(f"- **Location:** {p.district or 'Maharashtra'}, India")
        lines.append(f"- **Planned Capital Investment:** {p.investment_display or (f'₹{p.investment_inr:,.0f}' if p.investment_inr else 'Unspecified')}")
        if p.employee_count:
            lines.append(f"- **Estimated Workforce:** {p.employee_count} employees")
        if p.pollution_category:
            lines.append(f"- **Pollution Category:** {p.pollution_category}")
        lines.append("")

        lines.append("### 🏛️ Potentially Applicable Approvals & Clearances")
        for a in r.approvals:
            outdated_tag = " ⚠️ [Notice: Last verified >180 days ago]" if a.is_potentially_outdated else ""
            lines.append(f"#### 1. {a.name} ({a.applicability}){outdated_tag}")
            lines.append(f"- **Department:** {a.department_name}")
            lines.append(f"- **Why Applicable:** {a.why_applicable}")
            if a.fee_info:
                lines.append(f"- **Official Fee:** {a.fee_info}")
            if a.processing_time:
                lines.append(f"- **Processing Time:** {a.processing_time}")
            if a.validity:
                lines.append(f"- **Validity:** {a.validity} (Renewal: {'Required' if a.renewal_required else 'Not Required'})")
            if a.official_portal:
                lines.append(f"- **Official Portal:** [{a.official_portal}]({a.official_portal})")
            lines.append(f"- **Official Source:** {a.official_source} (Verified: {a.last_verified})")
            if a.required_documents:
                doc_list = ", ".join([d.name for d in a.required_documents])
                lines.append(f"- **Required Documents:** {doc_list}")
            lines.append("")

        lines.append("### 📁 Document Checklist")
        lines.append("**Missing Required Documents to Prepare:**")
        for doc in r.document_checklist.get("missing_required", []):
            lines.append(f"- ⚠ {doc}")
        lines.append("")

        lines.append("### 🚀 Recommended Next Steps")
        for step in r.next_steps:
            lines.append(f"- {step}")
        lines.append("")

        lines.append(f"> **Disclaimer:** {r.disclaimer}")
        return "\n".join(lines)
