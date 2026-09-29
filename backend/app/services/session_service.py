import re
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List
from app.schemas.profile import BusinessProfile
from app.schemas.chat import ChatResponse
from app.industry_taxonomy import (
    AEROSPACE_DEFENCE, AGRO_FOOD, AUTOMOBILE, BIOTECH_MEDICAL, CEMENT_STEEL,
    DAIRY_SUGAR, DATA_CENTRES, ELECTRIC_VEHICLES, ESDM_SEMICONDUCTORS,
    ENGINEERING, GEMS_JEWELLERY, GLOBAL_CAPABILITY_CENTRES, GREEN_ENERGY,
    INDUSTRY_4_0, INFORMATION_TECHNOLOGY, LOGISTICS, MINERAL_FOREST,
    PHARMACEUTICALS, REAL_ESTATE_CONSTRUCTION, TEXTILES,
)
from app.services.website_faq import find_website_faq
from app.services.knowledge import Knowledge
from app.models import Approval, ChatSession

_SESSION_STORE: Dict[str, BusinessProfile] = {}
_SESSION_META: Dict[str, dict] = {}
_EXPIRED_SESSIONS = set()
SESSION_TTL = timedelta(hours=24)

NON_MAHARASHTRA_STATES = [
    "gujarat", "karnataka", "tamil nadu", "delhi", "rajasthan", "telangana",
    "madhya pradesh", "uttar pradesh", "punjab", "haryana", "kerala", "andhra pradesh",
    "west bengal", "bihar", "odisha", "goa", "assam", "jharkhand", "chhattisgarh",
    "himachal pradesh", "uttarakhand", "arunachal pradesh", "manipur", "meghalaya",
    "mizoram", "nagaland", "sikkim", "tripura", "chandigarh", "jammu and kashmir",
    "ladakh", "puducherry", "andaman and nicobar", "lakshadweep", "dadra and nagar haveli",
    "daman and diu"
]

MAHARASHTRA_DISTRICTS = {
    "ahilyanagar": "Ahmednagar", "ahmednagar": "Ahmednagar",
    "mumbai city": "Mumbai City",
    "sindhudurg": "Sindhudurg", "chandrapur": "Chandrapur", "wardha": "Wardha",
    "akola": "Akola", "beed": "Beed", "bhandara": "Bhandara", "buldhana": "Buldhana",
    "gadchiroli": "Gadchiroli", "gondia": "Gondia", "hingoli": "Hingoli",
    "nandurbar": "Nandurbar", "parbhani": "Parbhani", "washim": "Washim",
    "dharashiv": "Dharashiv (Osmanabad)", "osmanabad": "Dharashiv (Osmanabad)",
    "pune": "Pune",
    "nashik": "Nashik",
    "aurangabad": "Chhatrapati Sambhajinagar (Aurangabad)",
    "chhatrapati sambhajinagar": "Chhatrapati Sambhajinagar (Aurangabad)",
    "sambhajinagar": "Chhatrapati Sambhajinagar (Aurangabad)",
    "mumbai": "Mumbai Suburban",
    "mumbai suburban": "Mumbai Suburban",
    "thane": "Thane",
    "navi mumbai": "Thane",
    "raigad": "Raigad",
    "roha": "Raigad",
    "mahad": "Raigad",
    "nagpur": "Nagpur",
    "kolhapur": "Kolhapur",
    "solapur": "Solapur",
    "amravati": "Amravati",
    "satara": "Satara",
    "sangli": "Sangli",
    "ratnagiri": "Ratnagiri",
    "jalgaon": "Jalgaon",
    "dhule": "Dhule",
    "jalna": "Jalna",
    "ahmednagar": "Ahmednagar",
    "nanded": "Nanded",
    "latur": "Latur",
    "palghar": "Palghar",
    "yavatmal": "Yavatmal"
}

INDUSTRY_PATTERNS = [
    (r"\b(electric vehicle|ev|battery electric|ev assembly|electric car|electric two.?wheeler)\b", ELECTRIC_VEHICLES, None),
    (r"\b(aerospace|defen[cs]e|aircraft|aviation|spacecraft|drone|mro)\b", AEROSPACE_DEFENCE, None),
    (r"\b(it/ites|ites|it.?enabled|information technology|it (?:company|unit|services|firm|sector)|software|saas|bpo|kpo|call cent(?:er|re)|tech company)\b", INFORMATION_TECHNOLOGY, "White"),
    (r"\b(esdm|semiconductor|chip.?manufactur|electronics? manufacturing|electronic assembly|pcb|printed circuit|electronic system design)\b", ESDM_SEMICONDUCTORS, None),
    (r"\b(biotech|biotechnology|medical device|diagnostic device|diagnostic kit|medical equipment|ivd|laboratory reagent)\b", BIOTECH_MEDICAL, None),
    (r"\b(agro|food processing|food manufactur|bakery|fruit|beverage|edible oil|spice|milling|flour|juice|packag(?:ed|ing) food)\b", AGRO_FOOD, "Orange"),
    (r"\b(textile|technical textile|apparel|garment|cloth|cotton|spinning|weaving|dyeing|fabric|yarn|loom)\b", TEXTILES, None),
    (r"\b(renewable energy|green energy|solar|wind power|biofuel|biogas|biodiesel|ethanol|battery storage)\b", GREEN_ENERGY, None),
    (r"\b(logistics|warehousing|warehouse|distribution centre|distribution center|cold storage|fulfilment|fulfillment)\b", LOGISTICS, None),
    (r"\b(automobile|auto components?|automotive|car parts|motor vehicle|vehicle manufacturing|gearbox manufacturing|engine manufacturing|stamping|casting|forging)\b", AUTOMOBILE, None),
    (r"\b(pharma|pharmaceutical|drug manufacturing|medicine manufacturing|active pharmaceutical ingredient|api manufacturing|formulation|bulk drug|specialty chemicals?|petrochemicals?|syrup|tablet manufacturing)\b", PHARMACEUTICALS, None),
    (r"\b(gem|jewell?ery|jewellery|diamond|goldsmith|ornament|precious stone)\b", GEMS_JEWELLERY, None),
    (r"\b(engineering|capital goods|machine shop|machinery|fabrication|industrial equipment|light engineering|machine tools)\b", ENGINEERING, None),
    (r"\b(cement|steel|iron and steel|sponge iron|steel plant|rebar|rolling mill)\b", CEMENT_STEEL, None),
    (r"\b(mineral|mining|forest.?based|timber|sawmill|wood processing|paper mill|mineral processing)\b", MINERAL_FOREST, None),
    (r"\b(real estate|construction|builder|township|property development|infrastructure development)\b", REAL_ESTATE_CONSTRUCTION, None),
    (r"\b(industry 4\.?0|artificial intelligence|\bai\b|robotics?|internet of things|\biot\b|3d printing|nanotechnology|additive manufacturing)\b", INDUSTRY_4_0, None),
    (r"\b(dairy|sugar mill|sugar processing|agro.?cooperative|cooperative processing|milk processing|sugar factory)\b", DAIRY_SUGAR, None),
    (r"\b(data cent(?:er|re)|server farm|colocation|cloud infrastructure)\b", DATA_CENTRES, "White"),
    (r"\b(global capability cent(?:er|re)|gcc|shared services cent(?:er|re)|offshore capability cent(?:er|re))\b", GLOBAL_CAPABILITY_CENTRES, None)
]

SUBSECTOR_QUESTIONS = {
    AUTOMOBILE: "Does the unit include a paint shop or foundry?",
    TEXTILES: "Does the textile activity include processing or dyeing?",
    ENGINEERING: "Is the activity light assembly, foundry, or forging?",
    GREEN_ENERGY: "Does the project include power generation?",
    AEROSPACE_DEFENCE: "Does the activity include aerospace MRO?",
    REAL_ESTATE_CONSTRUCTION: "Is this a large township project?",
    LOGISTICS: "Is this dry storage or another logistics activity?",
}

class SessionService:

    @staticmethod
    def get_or_create_session(session_id: Optional[str] = None) -> Tuple[str, BusinessProfile]:
        now = datetime.utcnow()
        for expired_id, meta in list(_SESSION_META.items()):
            if now - meta["updated_at"] > SESSION_TTL:
                _EXPIRED_SESSIONS.add(expired_id)
                _SESSION_META.pop(expired_id, None)
                _SESSION_STORE.pop(expired_id, None)
        if not session_id or session_id not in _SESSION_STORE:
            new_id = str(uuid.uuid4())
            profile = BusinessProfile()
            _SESSION_STORE[new_id] = profile
            _SESSION_META[new_id] = {"updated_at": now, "last_asked_field": None}
            return new_id, profile
        return session_id, _SESSION_STORE[session_id]

    @staticmethod
    def update_profile(session_id: str, profile: BusinessProfile) -> BusinessProfile:
        _SESSION_STORE[session_id] = profile
        _SESSION_META.setdefault(session_id, {})["updated_at"] = datetime.utcnow()
        return profile

    @classmethod
    def check_out_of_scope(cls, text: str) -> Optional[str]:
        text_lower = text.lower()
        district_present = any(re.search(rf"\b{re.escape(key)}\b", text_lower) for key in sorted(MAHARASHTRA_DISTRICTS, key=len, reverse=True))
        if district_present:
            return None
        for state in NON_MAHARASHTRA_STATES:
            if re.search(rf"\b{state}\b", text_lower):
                return state.title()
        return None

    @classmethod
    def mentioned_other_state(cls, text: str) -> Optional[str]:
        text_lower = text.lower()
        return next((state.title() for state in NON_MAHARASHTRA_STATES
                     if re.search(rf"\b{re.escape(state)}\b", text_lower)), None)

    @classmethod
    def extract_entities_from_message(cls, text: str, current_profile: BusinessProfile, session_id: Optional[str] = None) -> BusinessProfile:
        text_lower = text.lower()
        profile = current_profile.model_copy(deep=True)

        # 1. Industry match. Let an explicit sector in a later message replace
        # an earlier guess so a session cannot stay stuck on its first industry.
        explicit_new_business = bool(re.search(r"\b(actually|instead|new business|make it|setting up|manufactur(?:e|ing)|production unit|factory|plant)\b", text_lower))
        for pattern, ind_name, default_pollution in INDUSTRY_PATTERNS:
            if re.search(pattern, text_lower):
                if profile.industry and profile.industry != ind_name and not explicit_new_business:
                    break
                industry_changed = profile.industry != ind_name
                profile.industry = ind_name
                if industry_changed:
                    profile.pollution_category = None
                    profile.pollution_category_inferred = None
                if default_pollution:
                    profile.pollution_category_inferred = default_pollution
                if ind_name == "Pharmaceuticals & Chemicals" and profile.hazardous_materials is None and re.search(r"\b(pharma|pharmaceutical|chemical|api|bulk drug|solvent)\b", text_lower):
                    profile.hazardous_materials = True
                break

        # 2. District match
        for keyword, district_name in sorted(MAHARASHTRA_DISTRICTS.items(), key=lambda item: len(item[0]), reverse=True):
            if re.search(rf"\b{re.escape(keyword)}\b", text_lower):
                profile.district = district_name
                break

        # 3. Investment match
        if True:
            cr_match = re.search(r"([\d,]+(?:\.\d+)?)\s*(?:cr|crore|crores)\b", text_lower)
            lakh_match = re.search(r"([\d,]+(?:\.\d+)?)\s*(?:lakh|lakhs|lac|lacs|l)\b", text_lower)
            numeric_match = re.search(r"(?:rs\.?|inr|₹)?\s*([\d,]{6,14})\b", text_lower)

            if cr_match:
                val = float(cr_match.group(1).replace(",", ""))
                profile.investment_inr = val * 10_000_000
                profile.investment_display = f"₹{val:.2f} Crore".replace(".00", "")
            elif lakh_match:
                val = float(lakh_match.group(1).replace(",", ""))
                profile.investment_inr = val * 100_000
                profile.investment_display = f"₹{val:.2f} Lakhs".replace(".00", "")
            elif numeric_match:
                val = float(numeric_match.group(1).replace(",", ""))
                profile.investment_inr = val
                if val >= 10_000_000:
                    profile.investment_display = f"₹{val / 10_000_000:.2f} Crore"
                else:
                    profile.investment_display = f"₹{val / 100_000:.2f} Lakhs"

        # 4. Employee match
        if True:
            emp_match = re.search(r"(?:over\s+|more than\s+)?(\d+)(?:\s*[-–]\s*\d+|\s*\+)?\s*(?:employees|workers|people|staff|labour|labor|persons)\b", text_lower)
            if not emp_match:
                emp_match = re.search(r"workforce\s+of\s+(\d+)\b", text_lower)
            if not emp_match and _SESSION_META.get(session_id, {}).get("last_asked_field") == "employee_count":
                emp_match = re.fullmatch(r"\s*(\d+)\s*", text_lower)
            if emp_match:
                profile.employee_count = int(emp_match.group(1))
                _SESSION_META.get(session_id, {})["last_asked_field"] = None

        activity_terms = [term for term in ("paint shop", "foundry", "mro", "dyeing", "plating", "forging", "casting", "light assembly", "generation", "dry storage", "large township", "processing") if re.search(rf"\b{re.escape(term)}\b", text_lower)]
        if activity_terms:
            profile.activity = "; ".join(activity_terms)
            profile.sub_sector = profile.activity

        # 5. Construction match
        if profile.construction_required is None:
            if re.search(r"\b(new construction|constructing|build a factory|construct a shed|fresh building|setup on open plot)\b", text_lower):
                profile.construction_required = True
            elif re.search(r"\b(leased shed|rented premises|existing building|ready shed|no construction)\b", text_lower):
                profile.construction_required = False

        # 6. Hazardous match
        if profile.hazardous_materials is None:
            if re.search(r"\b(hazardous|chemicals|flammable|toxic chemicals|solvent storage|heavy boiler)\b", text_lower):
                profile.hazardous_materials = True
            elif re.search(r"\b(no hazardous|non-toxic|eco friendly|green product|dry assembly)\b", text_lower):
                profile.hazardous_materials = False

        return profile

    @classmethod
    def get_missing_critical_fields(cls, profile: BusinessProfile) -> List[str]:
        missing = []
        if not profile.industry:
            missing.append("industry")
        if not profile.district:
            missing.append("district")
        if not profile.investment_inr:
            missing.append("investment")
        if profile.employee_count is None and profile.industry not in ["Information Technology (IT) & IT-Enabled Services (ITeS)", "Global Capability Centres (GCC)"]:
            missing.append("employee_count")
        if profile.industry in SUBSECTOR_QUESTIONS and not (profile.sub_sector or profile.activity):
            missing.append("sub_sector")
        return missing

    @classmethod
    def _dataset_answer(cls, db, session_id, user_message, profile):
        if db is None:
            return None
        text = user_message.casefold()
        meta = _SESSION_META.setdefault(session_id, {})
        if any(term in text for term in ("subsid", "tax rate", "taxes", "legal advice")):
            return "This is not covered in the Samanvay dataset. I can answer questions about Maharashtra industries, approvals, documents, and listed industrial locations.\nSource: Samanvay workbook scope. Verification date not recorded in source dataset."
        approval_words = any(word in text for word in ("approval", "licence", "license", "registration", "consent", "clearance", "noc", "fssai", "udyam", "gst", "stpi", "sez", "boiler", "drug", "factory", "cto", "cte", "fire"))
        asks_fact = any(word in text for word in ("fee", "cost", "take", "long", "time", "valid", "renew", "department", "portal", "source", "purpose", "process", "what is", "tell me about", "which documents", "documents needed", "document"))
        approval = Knowledge.get_approval(db, user_message) if approval_words else None
        if not approval and any(word in text for word in ("its validity", "and how long", "what about the fee", "how long does it take")):
            approval = db.query(Approval).filter(Approval.id == meta.get("last_approval")).first() if meta.get("last_approval") else None
        if approval and (asks_fact or approval_words):
            meta["last_approval"] = approval.id
            lines = [f"**{approval.name}**"]
            if "document" in text:
                docs = Knowledge.get_documents(db, approval=approval)
                lines.append("**Indicative document list - verify with the authority:**")
                lines.extend(f"- {doc.name}" for doc in docs) if docs else lines.append("The dataset has no document mapping for this approval.")
            else:
                fields = (("fee", "Fee", approval.fee), ("processing_time", "Processing time", approval.processing_time),
                          ("validity", "Validity", approval.validity), ("renewal", "Renewal required", "Yes" if approval.renewal_required else "No"),
                          ("department", "Department", approval.department.name if approval.department else None),
                          ("purpose", "Purpose", approval.purpose), ("process", "Application process", approval.description))
                requested = []
                if "fee" in text or "cost" in text:
                    requested.append(next(entry for entry in fields if entry[0] == "fee"))
                if any(word in text for word in ("how long", "take", "processing", "time")):
                    requested.append(next(entry for entry in fields if entry[0] == "processing_time"))
                if "valid" in text:
                    requested.append(next(entry for entry in fields if entry[0] == "validity"))
                    requested.append(next(entry for entry in fields if entry[0] == "renewal"))
                if "renew" in text:
                    requested.append(next(entry for entry in fields if entry[0] == "renewal"))
                if "department" in text:
                    requested.append(next(entry for entry in fields if entry[0] == "department"))
                if "portal" in text:
                    requested.append(("portal", "Official portal", ", ".join(approval.official_portal_urls or []) if approval.official_portal_urls else None))
                if "source" in text:
                    requested.append(("source", "Official source", approval.official_source))
                if "purpose" in text:
                    requested.append(next(entry for entry in fields if entry[0] == "purpose"))
                if "process" in text:
                    requested.append(next(entry for entry in fields if entry[0] == "process"))
                if approval.id == "APR010" and ("fee" in text or "cost" in text):
                    requested = [entry for entry in fields if entry[0] in {"fee", "processing_time", "validity", "renewal"}]
                if not any(entry[0] == "department" for entry in requested):
                    requested.append(next(entry for entry in fields if entry[0] == "department"))
                if not requested:
                    requested = [entry for entry in fields if entry[2] is not None]
                for _, label, value in requested:
                    lines.append(f"- **{label}:** {value if value is not None else 'This is not covered in the Samanvay dataset.'}")
                if not Knowledge.explain_rules_for(db, approval):
                    lines.append("- Applicability: No applicability rule in the dataset; verify whether it applies.")
                if "need" in text or "required" in text or "apply" in text:
                    for rule in Knowledge.explain_rules_for(db, approval):
                        thresholds = []
                        if rule.employee_min is not None: thresholds.append(f"{rule.employee_min}+ workers")
                        if rule.employee_max is not None: thresholds.append(f"up to {rule.employee_max} workers")
                        if thresholds: lines.append(f"- Rule {rule.id}: {'; '.join(thresholds)} — {rule.applicability}.")
                        note = (rule.conditions or {}).get("notes") if isinstance(rule.conditions, dict) else None
                        if note: lines.append(f"  - Why: {note}")
                if approval.id == "APR003" and "valid" in text:
                    lines.append("- White category: no CTO is needed; only intimation, according to the source dataset.")
                    renewal_marker = "Renewal notes:"
                    if approval.description and renewal_marker in approval.description:
                        lines.append(f"- Renewal terms: {approval.description.split(renewal_marker, 1)[1].strip()}")
            verification = f"Verification date: {approval.last_verified}" if approval.last_verified else "Verification date not recorded in source dataset"
            lines.append(f"Source: {approval.official_source}. {verification}.")
            return "\n".join(lines)
        if "list all" in text and ("mpcb" in text or "consent" in text):
            records = [item for item in Knowledge.list_approvals(db) if "consent" in item.name.casefold() or "mpcb" in (item.department.name.casefold() if item.department else "")]
            body = "\n".join(f"- {item.id}: {item.name} ({item.department.name if item.department else 'department not recorded'})" for item in records)
            return f"MPCB approvals in the dataset:\n{body}\nSource: Approvals sheet in the Samanvay workbook. Verification date not recorded in source dataset."
        industry = Knowledge.get_industry(db, user_message)
        if industry and any(word in text for word in ("what does", "basic requirements", "what are the requirements", "tell me about", "requirements for")):
            meta["last_industry"] = industry.name
            requirements = (industry.basic_setup_information or {}).get("summary")
            matching_rules = Knowledge.explain_rules_for_industry(db, industry.name)
            rule_lines = [f"- {rule.approval_id} {rule.approval_name}: {rule.applicability}" + (f" [{rule.sub_sector}]" if rule.sub_sector else "") + (f" — {rule.activity}" if rule.activity else "") + (f" in {rule.district}" if rule.district else "") for rule in matching_rules]
            rules_text = "\n\nWorkbook rule records:\n" + "\n".join(rule_lines) if rule_lines else ""
            message = f"**{industry.name}**\n\n{requirements or 'This is not covered in the Samanvay dataset.'}{rules_text}\n\nSource: Industries and Approval_Rules sheets in the Samanvay workbook. Verification date not recorded in source dataset."
            return message
        if "industrial area" in text or "industrial areas" in text:
            district = next((name for name in sorted(MAHARASHTRA_DISTRICTS, key=len, reverse=True) if name in text), None)
            district = MAHARASHTRA_DISTRICTS.get(district, district.title() if district else None)
            rows = Knowledge.get_locations(db, district=district) if district else []
            if rows:
                meta["last_district"] = district
                lines = [f"Industrial areas in {district}:"]
                lines.extend(f"- {row.industrial_area or row.city or row.taluka} ({row.taluka or 'taluka not recorded'})" + (f" — {row.special_conditions.get('summary')}" if row.special_conditions and row.special_conditions.get("summary") else "") for row in rows)
                lines.append("Source: Locations sheet in the Samanvay workbook. Verification date not recorded in source dataset.")
                return "\n".join(lines)
        return None

    @classmethod
    def process_chat_message(cls, session_id: Optional[str], user_message: str, db=None) -> ChatResponse:
        if session_id and session_id in _SESSION_META and datetime.utcnow() - _SESSION_META[session_id]["updated_at"] > SESSION_TTL:
            _EXPIRED_SESSIONS.add(session_id)
        expired_session = bool(session_id and (session_id not in _SESSION_STORE or session_id in _EXPIRED_SESSIONS))
        if expired_session:
            _EXPIRED_SESSIONS.discard(session_id)
        if session_id and db is not None and session_id not in _SESSION_STORE:
            stored = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
            if stored and datetime.utcnow() - stored.updated_at <= SESSION_TTL:
                _SESSION_STORE[session_id] = BusinessProfile.model_validate(stored.profile_json)
                _SESSION_META[session_id] = {"updated_at": stored.updated_at, "last_asked_field": None, **(stored.last_entities or {})}
        session_id, current_profile = cls.get_or_create_session(session_id)

        dataset_answer = cls._dataset_answer(db, session_id, user_message, current_profile)
        if dataset_answer:
            cls._persist_session(db, session_id, current_profile)
            return ChatResponse(session_id=session_id, message=dataset_answer, extracted_profile=current_profile,
                                missing_fields=cls.get_missing_critical_fields(current_profile), response_type="knowledge")

        if re.search(r"\bchange investment amount\b", user_message.lower().strip()):
            _SESSION_META.setdefault(session_id, {})["last_asked_field"] = "investment"
            _SESSION_META[session_id]["updated_at"] = datetime.utcnow()
            return ChatResponse(
                session_id=session_id,
                message="What is the new total capital investment (in Lakhs or Crores)?",
                extracted_profile=current_profile,
                missing_fields=cls.get_missing_critical_fields(current_profile),
                quick_suggestions=["5 crore", "10 crore"],
                ready_for_recommendation=False,
                out_of_scope=False,
            )

        # Answer website navigation questions without changing the approval profile.
        website_faq = find_website_faq(user_message)
        if website_faq:
            return ChatResponse(
                session_id=session_id,
                message=website_faq["answer"],
                extracted_profile=current_profile,
                missing_fields=cls.get_missing_critical_fields(current_profile),
                quick_suggestions=["How do I register a project?", "What can this website do?"],
                ready_for_recommendation=False,
                out_of_scope=False,
                response_type="website_faq",
            )

        # 1. Out-of-scope check (Scenario 9)
        detected_state = cls.check_out_of_scope(user_message)
        if detected_state:
            return ChatResponse(
                session_id=session_id,
                message=(
                    f"**Scope notice:** Questions about {detected_state} are not covered in the Samanvay dataset, which contains Maharashtra records. "
                    "I can help with Maharashtra approvals, industries, documents, and industrial locations."
                ),
                extracted_profile=current_profile,
                missing_fields=cls.get_missing_critical_fields(current_profile),
                quick_suggestions=["Food processing in Pune", "Automobile unit in Sambhajinagar", "IT company in Mumbai"],
                out_of_scope=True,
                scope_notice=f"Location '{detected_state}' is outside Maharashtra scope."
            )

        # 2. Extract entities
        updated_profile = cls.extract_entities_from_message(user_message, current_profile, session_id)
        mentioned_state = cls.mentioned_other_state(user_message)
        has_maharashtra_district = any(re.search(rf"\b{re.escape(key)}\b", user_message.lower())
                                       for key in MAHARASHTRA_DISTRICTS)
        if mentioned_state and has_maharashtra_district:
            updated_profile.additional_attributes["scope_note"] = f"The message also mentioned {mentioned_state}; recommendations below apply only to Maharashtra."
        if db is not None and updated_profile.district and not Knowledge.get_locations(db, district=updated_profile.district):
            updated_profile.additional_attributes["location_data_gap"] = f"There is no industrial-area data for {updated_profile.district} in the Samanvay dataset."
        cls.update_profile(session_id, updated_profile)
        if updated_profile.industry:
            _SESSION_META[session_id]["last_industry"] = updated_profile.industry
        if updated_profile.district:
            _SESSION_META[session_id]["last_district"] = updated_profile.district
        cls._persist_session(db, session_id, updated_profile)

        # 3. Missing fields
        missing_fields = cls.get_missing_critical_fields(updated_profile)
        ready = not missing_fields

        if ready:
            emp_info = f" with approximately {updated_profile.employee_count} workers" if updated_profile.employee_count else ""
            reply_text = (
                f"I have recorded your business profile for a **{updated_profile.industry}** unit in **{updated_profile.district}**, Maharashtra, "
                f"with a planned capital investment of **{updated_profile.investment_display or f'₹{updated_profile.investment_inr:,.0f}'}**{emp_info}.\n\n"
                f"All core details are gathered! We are ready to run our deterministic rules engine to calculate your exact statutory approvals, MPCB pollution consents, required documents, and next steps."
            )
            quick_suggestions = ["Generate Required Approvals & Checklist", "Change Investment Amount", "Add Construction Details"]
        else:
            follow_ups = []
            quick_suggestions = []

            if "industry" in missing_fields:
                follow_ups.append(
                    "What **industry sector or manufacturing activity** are you setting up? (e.g., Food Processing, Auto Components, Textiles, IT/ITES, Pharmaceuticals, Light Engineering)"
                )
                quick_suggestions = ["Food Processing", "Auto Components", "Textiles", "IT/ITES", "Pharmaceuticals"]
            elif "district" in missing_fields:
                follow_ups.append(
                    f"Which **district in Maharashtra** are you planning to locate your {updated_profile.industry or 'unit'} in? (e.g., Pune, Nashik, Chhatrapati Sambhajinagar, Mumbai, Thane, Raigad)"
                )
                quick_suggestions = ["Pune", "Nashik", "Chhatrapati Sambhajinagar", "Mumbai", "Thane", "Raigad"]
            elif "investment" in missing_fields:
                follow_ups.append(
                    f"What is your **estimated total capital investment** (in Lakhs or Crores)? This is required to determine your MSME category and MPCB government fee brackets."
                )
                quick_suggestions = ["₹50 Lakhs", "₹2.5 Crore", "₹10 Crore", "₹25 Crore"]
            elif "employee_count" in missing_fields:
                follow_ups.append(
                    "How many **workers/employees** do you anticipate hiring? (Units with 10 or more workers with power require a DISH Factory License under the Factories Act)."
                )
                quick_suggestions = ["5 employees", "15 employees", "35 employees", "100+ workers"]
            elif "sub_sector" in missing_fields:
                follow_ups.append(SUBSECTOR_QUESTIONS[updated_profile.industry])

            _SESSION_META.setdefault(session_id, {})["last_asked_field"] = missing_fields[0] if missing_fields else None

            reply_text = " ".join(follow_ups)

        scope_note = updated_profile.additional_attributes.get("scope_note")
        if scope_note and mentioned_state and has_maharashtra_district:
            reply_text += f"\n\n**Scope note:** {scope_note}"
        location_gap = updated_profile.additional_attributes.get("location_data_gap")
        if location_gap:
            reply_text += f"\n\n**Location data gap:** {location_gap}"

        if expired_session:
            reply_text = "Your previous chat session expired, so I started a new one. " + reply_text

        return ChatResponse(
            session_id=session_id,
            message=reply_text,
            extracted_profile=updated_profile,
            missing_fields=missing_fields,
            quick_suggestions=quick_suggestions,
            ready_for_recommendation=ready,
            out_of_scope=False
        )

    @staticmethod
    def _persist_session(db, session_id, profile):
        if db is None:
            return
        meta = _SESSION_META.setdefault(session_id, {})
        row = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        entities = {key: value for key, value in meta.items() if key.startswith("last_")}
        if row is None:
            row = ChatSession(session_id=session_id, profile_json=profile.model_dump(), last_entities=entities, updated_at=datetime.utcnow())
            db.add(row)
        else:
            row.profile_json = profile.model_dump()
            row.last_entities = entities
            row.updated_at = datetime.utcnow()
        db.commit()
