import logging
from typing import List, Dict, Tuple, Optional
from datetime import date
from sqlalchemy.orm import Session, joinedload, selectinload
from app.models.approval import Approval
from app.models.document import ApprovalDocument
from app.models.rule import ApprovalRule
from app.schemas.profile import BusinessProfile
from app.schemas.approval import RecommendedApproval, DocumentChecklistItem, SetupStep, ApprovalRecommendationResult
from app.config import settings
from app.engine.conditions import ConditionEvaluator
from app.industry_taxonomy import normalize_industry

logger = logging.getLogger(__name__)

class DeterministicRulesEngine:
    @classmethod
    def evaluate_approvals(cls, db: Session, profile: BusinessProfile) -> ApprovalRecommendationResult:
        staleness_threshold = settings.REGULATORY_STALENESS_DAYS
        today = date.today()

        approvals = (
            db.query(Approval)
            .options(
                joinedload(Approval.department),
                selectinload(Approval.rules),
                selectinload(Approval.documents).joinedload(ApprovalDocument.document),
            )
            .filter(Approval.status == "ACTIVE")
            .all()
        )

        recommended_approvals: List[RecommendedApproval] = []
        doc_checklist_map: Dict[str, str] = {}

        for approval in approvals:
            is_matched, applicability, why_text, cond_summary = cls._evaluate_single_approval(approval, profile)
            
            if is_matched:
                days_old = (today - approval.last_verified).days
                is_outdated = days_old > staleness_threshold

                req_docs: List[DocumentChecklistItem] = []
                for app_doc in approval.documents:
                    doc = app_doc.document
                    doc_item = DocumentChecklistItem(
                        document_id=doc.id,
                        name=doc.name,
                        description=doc.description,
                        issuing_authority=doc.issuing_authority,
                        mandatory=app_doc.mandatory,
                        condition=app_doc.condition,
                        status="missing"
                    )
                    req_docs.append(doc_item)
                    doc_checklist_map[doc.name] = "missing"

                rec_app = RecommendedApproval(
                    approval_id=approval.id,
                    name=approval.name,
                    description=approval.description,
                    purpose=approval.purpose,
                    department_name=approval.department.name if approval.department else "Maharashtra State Authority",
                    applicability=applicability,
                    why_applicable=why_text,
                    conditions_summary=cond_summary,
                    official_portal=approval.official_portal,
                    official_source=approval.official_source,
                    fee_info=approval.fee,
                    processing_time=approval.processing_time,
                    validity=approval.validity,
                    renewal_required=approval.renewal_required,
                    last_verified=approval.last_verified,
                    is_potentially_outdated=is_outdated,
                    required_documents=req_docs
                )
                recommended_approvals.append(rec_app)

        information_required = [
            f"Confirm applicability of {item.name} with {item.department_name}"
            for item in recommended_approvals
            if item.applicability == "Information required"
        ]
        document_checklist = {
            "verified_have": [],
            "missing_required": list(doc_checklist_map.keys()),
            "info_needed": information_required
        }

        basic_steps = cls._generate_setup_steps(profile)

        next_steps = [
            f"Review {item.name} with {item.department_name}; applicability: {item.applicability}."
            + (f" Apply through {item.official_portal}." if item.official_portal else "")
            for item in recommended_approvals
        ]
        if not next_steps:
            next_steps = ["No approval matched the supplied profile. Confirm the activity and project details, then consult the relevant Maharashtra authority."]

        return ApprovalRecommendationResult(
            business_profile=profile,
            basic_setup_steps=basic_steps,
            approvals=recommended_approvals,
            document_checklist=document_checklist,
            next_steps=next_steps
        )

    @classmethod
    def _evaluate_single_approval(cls, approval: Approval, profile: BusinessProfile) -> Tuple[bool, str, str, Optional[str]]:
        if not approval.rules:
            # Without explicit rules we cannot safely claim applicability.
            return True, "Information required", "This registry record has no applicability rules; verify with the issuing authority.", "Applicability rules are not configured."

        for rule in approval.rules:
            scope_needs_confirmation = False
            # 1. State check
            if rule.state and profile.state and rule.state.lower() != profile.state.lower():
                continue

            # 2. Industry match
            if rule.industry:
                if not profile.industry:
                    continue
                profile_industry, _ = normalize_industry(profile.industry)
                rule_industry, embedded_sub_sector = normalize_industry(rule.industry)
                if not profile_industry:
                    logger.warning("Unrecognized profile industry label %r; skipping industry-scoped rule", profile.industry)
                    continue
                if not rule_industry:
                    logger.warning("Unrecognized approval rule industry label %r; skipping rule", rule.industry)
                    continue
                if profile.industry.casefold() != profile_industry.casefold():
                    logger.warning("Legacy profile industry label %r resolved to canonical %r", profile.industry, profile_industry)
                if rule.industry.casefold() != rule_industry.casefold():
                    logger.warning("Legacy rule industry label %r resolved to canonical %r", rule.industry, rule_industry)
                if rule_industry.casefold() != profile_industry.casefold():
                    continue

                # A legacy label may have carried a sub-sector qualifier in
                # the industry column. Preserve its scope instead of treating
                # it as a match for every business in the parent industry.
                required_scope = "; ".join(filter(None, [embedded_sub_sector, rule.sub_sector, rule.activity]))
                supplied_scope = "; ".join(filter(None, [profile.sub_sector, profile.activity]))
                if required_scope:
                    if not supplied_scope:
                        scope_needs_confirmation = True
                    else:
                        required_terms = [part.strip().casefold() for part in required_scope.split(";") if part.strip()]
                        supplied_folded = supplied_scope.casefold()
                        if not all(term in supplied_folded or supplied_folded in term for term in required_terms):
                            continue

            # 3. District match
            if rule.district:
                if not profile.district or rule.district.lower() != profile.district.lower():
                    continue

            # 4. Investment Range check
            if rule.investment_min is not None and profile.investment_inr is not None:
                if profile.investment_inr < float(rule.investment_min):
                    continue
            if rule.investment_max is not None and profile.investment_inr is not None:
                if profile.investment_inr > float(rule.investment_max):
                    continue

            # 5. Worker count check
            if rule.employee_min is not None and profile.employee_count is not None:
                if profile.employee_count < rule.employee_min:
                    continue

            # 6. Construction requirement check
            if rule.construction_required is not None and profile.construction_required is not None:
                if rule.construction_required != profile.construction_required:
                    continue

            # 7. Hazardous materials check
            if rule.hazardous_materials is not None and profile.hazardous_materials is not None:
                if rule.hazardous_materials != profile.hazardous_materials:
                    continue

            # 8. Pollution category check
            if rule.pollution_category and profile.pollution_category:
                if rule.pollution_category.lower() != profile.pollution_category.lower():
                    continue

            conditions_match, condition_note = ConditionEvaluator.evaluate_rule_conditions(rule.conditions or {}, profile)
            if not conditions_match:
                continue

            why_text = f"Matched statutory rule for {profile.industry or 'manufacturing'} in {profile.district or 'Maharashtra'}."
            if condition_note:
                why_text += f" {condition_note}"
            applicability = rule.applicability
            if scope_needs_confirmation:
                applicability = "Information required"
                why_text += " Confirm the project's sub-sector or activity before treating this approval as applicable."

            cond_summary = str(rule.conditions) if rule.conditions else None
            return True, applicability, why_text, cond_summary

        return False, "Not applicable", "No matching condition triggers found.", None

    @classmethod
    def _generate_setup_steps(cls, profile: BusinessProfile) -> List[SetupStep]:
        industry_name = profile.industry or "Manufacturing Unit"
        district_name = profile.district or "Maharashtra"

        steps = [
            SetupStep(
                step_number=1,
                title="Business Entity & Udyam MSME Registration",
                description="Incorporate company/LLP and register Udyam certificate on the National MSME portal (instant & free).",
                department_involved="Ministry of MSME / Directorate of Industries"
            ),
            SetupStep(
                step_number=2,
                title="Industrial Land / Shed Acquisition",
                description=f"Secure land allotment via MIDC Single Window portal (services.midcindia.org) or private industrial land in {district_name}.",
                department_involved="MIDC / Revenue Department"
            ),
            SetupStep(
                step_number=3,
                title="Check MPCB Consent to Establish applicability",
                description="Confirm whether the selected activity and pollution category require MPCB Consent to Establish before starting construction.",
                department_involved="Maharashtra Pollution Control Board (MPCB)"
            ),
            SetupStep(
                step_number=4,
                title="Factory Building Plan Appraisal & Fire Provisional NOC",
                description="Submit architectural structural drawings and fire safety plans to DISH / Local Authority before plant construction.",
                department_involved="Directorate of Industrial Safety & Health (DISH) / Fire Services"
            ),
            SetupStep(
                step_number=5,
                title="Power & Water Infrastructure Sanctions",
                description="Apply for High-Tension (HT) or Low-Tension (LT) power supply via MSEDCL portal and water connection via MIDC.",
                department_involved="MSEDCL & MIDC Water Supply"
            ),
            SetupStep(
                step_number=6,
                title="Check operating and sector-specific licenses",
                description=f"Before operations, confirm which operating consents and licenses apply to the selected activity ({industry_name}), including any factory or sector-specific license.",
                department_involved="MPCB, DISH & Regulatory Authorities"
            )
        ]
        return steps
