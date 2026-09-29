import logging
import json
import re
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
        baseline_registrations: List[str] = []
        not_applicable = []
        category_breakdowns = {}
        data_gaps = ["Verification date not recorded in source dataset"]
        doc_checklist_map: Dict[str, str] = {}

        for approval in approvals:
            if not approval.rules:
                baseline_registrations.append(f"{approval.name} — No applicability rule in the dataset; verify whether it applies")
                data_gaps.append(f"No applicability rule for {approval.name}")
                if not approval.documents:
                    data_gaps.append(f"No document mapping for {approval.name}")
                continue
            is_matched, applicability, why_text, cond_summary = cls._evaluate_single_approval(approval, profile)
            if applicability == "Not applicable" and why_text != "No matching condition triggers found.":
                not_applicable.append({"approval_id": approval.id, "name": approval.name, "reason": why_text})
                continue
            if cond_summary:
                try:
                    parsed_summary = json.loads(cond_summary)
                    if parsed_summary.get("by_category"):
                        category_breakdowns[approval.id] = parsed_summary["by_category"]
                except (ValueError, AttributeError) as exc:
                    logger.warning("Unable to parse category breakdown for approval %s: %s", approval.id, type(exc).__name__)
            
            if is_matched:
                if not approval.last_verified:
                    data_gaps.append(f"Verification date not recorded for {approval.name}")
                if not approval.documents:
                    data_gaps.append(f"No document mapping for {approval.name}")
                is_outdated = bool(approval.last_verified and (today - approval.last_verified).days > staleness_threshold)

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
                    is_demo=approval.is_demo,
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
            next_steps=next_steps,
            baseline_registrations=baseline_registrations,
            not_applicable=not_applicable,
            by_category=category_breakdowns,
            assumptions=[f"{field} was not provided" for field in ("district", "investment_inr", "employee_count", "sub_sector", "activity", "pollution_category", "project_stage", "hazardous_materials", "construction_required") if getattr(profile, field, None) is None],
            data_gaps=sorted(set(data_gaps)),
        )

    @classmethod
    def _evaluate_single_approval(cls, approval: Approval, profile: BusinessProfile) -> Tuple[bool, str, str, Optional[str]]:
        if not approval.rules:
            return False, "Not applicable", "No applicability rule is configured.", None

        applicability_rank = {"Likely applicable": 0, "Potentially applicable": 1, "Depends on conditions": 2, "Information required": 3}
        matched = []
        ordered_rules = sorted(approval.rules, key=lambda rule: (
            0 if getattr(rule, "district", None) else 1 if (getattr(rule, "sub_sector", None) or getattr(rule, "activity", None)) else 2 if getattr(rule, "industry", None) else 3,
            str(getattr(rule, "id", "")),
        ))
        for rule in ordered_rules:
            scope_needs_confirmation = False
            embedded_sub_sector = None
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
            activity_text = getattr(rule, "activity", None)
            scope_activity = None
            if activity_text and re.search(r"\b(paint shop|foundry|forging|processing/dyeing|light assembly|MRO|generation|dry storage|township|processing unit)\b", activity_text, re.I):
                scope_activity = activity_text
            required_scope = "; ".join(filter(None, [embedded_sub_sector, getattr(rule, "sub_sector", None), scope_activity]))
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
            if getattr(rule, "employee_max", None) is not None and profile.employee_count is not None:
                if profile.employee_count > rule.employee_max:
                    continue

            if getattr(rule, "project_stage", None) and profile.project_stage:
                allowed_stages = {part.strip().casefold() for part in re.split(r"[;,/]", rule.project_stage) if part.strip()}
                supplied_stages = {part.strip().casefold() for part in re.split(r"[;,/]", profile.project_stage) if part.strip()}
                if not allowed_stages.intersection(supplied_stages):
                    continue

            if rule.pollution_category:
                category = profile.pollution_category
                if category and rule.pollution_category.lower() != category.lower():
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
            if applicability.casefold() == "not applicable":
                matched.append((0, (0, str(getattr(rule, "id", ""))), "Not applicable", why_text, cond_summary, rule.pollution_category))
                continue
            specificity = (0 if getattr(rule, "district", None) else 1 if (getattr(rule, "sub_sector", None) or getattr(rule, "activity", None)) else 2 if getattr(rule, "industry", None) else 3, str(getattr(rule, "id", "")))
            matched.append((applicability_rank.get(applicability, 9), specificity, applicability, why_text, cond_summary, rule.pollution_category))

        if matched:
            category_rules = matched
            categories = {}
            for item in category_rules:
                if item[5]:
                    candidate = (item[1], item[2])
                    if item[5] not in categories or candidate[0] < categories[item[5]][0]:
                        categories[item[5]] = candidate
            if profile.pollution_category is None and len(categories) > 1:
                breakdown = {category: value[1] for category, value in categories.items()}
                detail = "; ".join(f"{category}: {value}" for category, value in sorted(breakdown.items()))
                return True, "Depends on conditions", f"Applicability depends on pollution category: {detail}.", json.dumps({"by_category": breakdown})
            _, _, applicability, why_text, cond_summary, _ = min(matched, key=lambda item: item[1])
            if applicability == "Not applicable":
                return False, applicability, why_text, cond_summary
            return True, applicability, why_text, cond_summary
        return False, "Not applicable", "No matching condition triggers found.", None

    @classmethod
    def _generate_setup_steps(cls, profile: BusinessProfile) -> List[SetupStep]:
        return [SetupStep(
            step_number=1,
            title="Review the workbook-matched records",
            description="Check each applicability note, source, and listed data gap against the project details, then confirm uncertain requirements with the authority named in the record.",
            department_involved=None,
        )]
