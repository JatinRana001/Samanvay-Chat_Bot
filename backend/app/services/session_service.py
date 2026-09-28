import re
import uuid
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

_SESSION_STORE: Dict[str, BusinessProfile] = {}

NON_MAHARASHTRA_STATES = [
    "gujarat", "karnataka", "tamil nadu", "delhi", "rajasthan", "telangana",
    "madhya pradesh", "uttar pradesh", "punjab", "haryana", "kerala", "andhra pradesh",
    "west bengal", "bihar", "odisha", "goa", "assam", "jharkhand", "chhattisgarh",
    "himachal pradesh", "uttarakhand"
]

MAHARASHTRA_DISTRICTS = {
    "pune": "Pune",
    "nashik": "Nashik",
    "aurangabad": "Chhatrapati Sambhajinagar (Aurangabad)",
    "chhatrapati sambhajinagar": "Chhatrapati Sambhajinagar (Aurangabad)",
    "sambhajinagar": "Chhatrapati Sambhajinagar (Aurangabad)",
    "mumbai": "Mumbai Suburban",
    "mumbai city": "Mumbai Suburban",
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
    (r"\b(automobile|auto component|automotive|car parts|motor vehicle|vehicle manufacturing|engine|gearbox|stamping|casting|forging)\b", AUTOMOBILE, None),
    (r"\b(pharma|pharmaceutical|drug|medicine|api|formulation|bulk drug|chemical|specialty chemical|petrochemical|syrup|tablet)\b", PHARMACEUTICALS, None),
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

class SessionService:

    @staticmethod
    def get_or_create_session(session_id: Optional[str] = None) -> Tuple[str, BusinessProfile]:
        if not session_id or session_id not in _SESSION_STORE:
            new_id = str(uuid.uuid4())
            profile = BusinessProfile()
            _SESSION_STORE[new_id] = profile
            return new_id, profile
        return session_id, _SESSION_STORE[session_id]

    @staticmethod
    def update_profile(session_id: str, profile: BusinessProfile) -> BusinessProfile:
        _SESSION_STORE[session_id] = profile
        return profile

    @classmethod
    def check_out_of_scope(cls, text: str) -> Optional[str]:
        text_lower = text.lower()
        for state in NON_MAHARASHTRA_STATES:
            if re.search(rf"\b{state}\b", text_lower):
                return state.title()
        return None

    @classmethod
    def extract_entities_from_message(cls, text: str, current_profile: BusinessProfile) -> BusinessProfile:
        text_lower = text.lower()
        profile = current_profile.model_copy(deep=True)

        # 1. Industry match. Let an explicit sector in a later message replace
        # an earlier guess so a session cannot stay stuck on its first industry.
        for pattern, ind_name, default_pollution in INDUSTRY_PATTERNS:
            if re.search(pattern, text_lower):
                industry_changed = profile.industry != ind_name
                profile.industry = ind_name
                if industry_changed:
                    # Clear inferred values from the old sector before applying
                    # the new sector's known defaults.
                    profile.pollution_category = default_pollution
                    profile.hazardous_materials = None
                elif not profile.pollution_category and default_pollution:
                    profile.pollution_category = default_pollution
                if ind_name == "Pharmaceuticals & Chemicals" and profile.hazardous_materials is None and re.search(r"\b(pharma|pharmaceutical|chemical|api|bulk drug|solvent)\b", text_lower):
                    profile.hazardous_materials = True
                break

        # 2. District match
        if not profile.district:
            for keyword, district_name in MAHARASHTRA_DISTRICTS.items():
                if re.search(rf"\b{re.escape(keyword)}\b", text_lower):
                    profile.district = district_name
                    break

        # 3. Investment match
        if not profile.investment_inr:
            cr_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:cr|crore|crores)\b", text_lower)
            lakh_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|lac|lacs|l)\b", text_lower)
            numeric_match = re.search(r"(?:rs\.?|inr|₹)?\s*(\d{6,10})\b", text_lower)

            if cr_match:
                val = float(cr_match.group(1))
                profile.investment_inr = val * 10_000_000
                profile.investment_display = f"₹{val:.2f} Crore".replace(".00", "")
            elif lakh_match:
                val = float(lakh_match.group(1))
                profile.investment_inr = val * 100_000
                profile.investment_display = f"₹{val:.2f} Lakhs".replace(".00", "")
            elif numeric_match:
                val = float(numeric_match.group(1))
                profile.investment_inr = val
                if val >= 10_000_000:
                    profile.investment_display = f"₹{val / 10_000_000:.2f} Crore"
                else:
                    profile.investment_display = f"₹{val / 100_000:.2f} Lakhs"

        # 4. Employee match
        if not profile.employee_count:
            emp_match = re.search(r"(\d+)\s*(?:employees|workers|people|staff|labour|labor|persons)\b", text_lower)
            if emp_match:
                profile.employee_count = int(emp_match.group(1))

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
        return missing

    @classmethod
    def process_chat_message(cls, session_id: Optional[str], user_message: str) -> ChatResponse:
        session_id, current_profile = cls.get_or_create_session(session_id)

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
                    f"**Scope Notice:** Samanvay is strictly configured for the **State of Maharashtra, India**. "
                    f"You mentioned **{detected_state}**, which is outside our current regulatory jurisdiction. "
                    f"For industrial setup in {detected_state}, please consult that state's official Single Window portal. "
                    f"If you also plan to set up operations in Maharashtra (e.g. Pune, Nashik, Chhatrapati Sambhajinagar, Mumbai), please provide the Maharashtra district and industry details!"
                ),
                extracted_profile=current_profile,
                missing_fields=cls.get_missing_critical_fields(current_profile),
                quick_suggestions=["Food processing in Pune", "Automobile unit in Sambhajinagar", "IT company in Mumbai"],
                out_of_scope=True,
                scope_notice=f"Location '{detected_state}' is outside Maharashtra scope."
            )

        # 2. Extract entities
        updated_profile = cls.extract_entities_from_message(user_message, current_profile)
        cls.update_profile(session_id, updated_profile)

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

            reply_text = " ".join(follow_ups)

        return ChatResponse(
            session_id=session_id,
            message=reply_text,
            extracted_profile=updated_profile,
            missing_fields=missing_fields,
            quick_suggestions=quick_suggestions,
            ready_for_recommendation=ready,
            out_of_scope=False
        )
