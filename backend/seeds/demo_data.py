from datetime import date
from app.industry_taxonomy import (
    AGRO_FOOD, AUTOMOBILE, CANONICAL_INDUSTRIES, ENGINEERING,
    INFORMATION_TECHNOLOGY, PHARMACEUTICALS, TEXTILES,
)

DEMO_DEPARTMENTS = [
    {
        "id": "dept-mpcb-001",
        "name": "Maharashtra Pollution Control Board (MPCB)",
        "description": "Statutory authority for environmental pollution control and industrial consents in Maharashtra.",
        "website": "https://mpcb.gov.in",
        "portal": "https://ecmpcb.mpcb.gov.in",
        "contact_information": "Kalpataru Point, 3rd and 4th floor, Opp. PVR Cinema, Sion Circle, Mumbai-400022. Tel: 022-24010437"
    },
    {
        "id": "dept-dish-002",
        "name": "Directorate of Industrial Safety & Health (DISH)",
        "description": "Regulates safety, health, and welfare of factory workers under the Factories Act, 1948 in Maharashtra.",
        "website": "https://dish.maharashtra.gov.in",
        "portal": "https://dish.maharashtra.gov.in",
        "contact_information": "Kamgar Bhavan, 5th Floor, C-20, E-Block, Bandra-Kurla Complex, Bandra (East), Mumbai-400051."
    },
    {
        "id": "dept-midc-003",
        "name": "Maharashtra Industrial Development Corporation (MIDC)",
        "description": "Apex industrial infrastructure development agency providing land allotment, water supply, and building plan approvals.",
        "website": "https://midcindia.org",
        "portal": "https://services.midcindia.org",
        "contact_information": "Udyog Bhavan, Mahakali Caves Road, Andheri (E), Mumbai-400093."
    },
    {
        "id": "dept-ind-004",
        "name": "Directorate of Industries, Maharashtra",
        "description": "Nodal agency for MSME registration, industrial policy incentives (PSI), and Single Window Facilitation (MAITRI).",
        "website": "https://industry.maharashtra.gov.in",
        "portal": "https://maitri.mahaonline.gov.in",
        "contact_information": "New Administrative Building, 2nd Floor, Madam Cama Road, Opp. Mantralaya, Mumbai-400032."
    },
    {
        "id": "dept-msedcl-005",
        "name": "Maharashtra State Electricity Distribution Co. Ltd. (MSEDCL)",
        "description": "State power distribution utility providing LT and HT industrial power connections.",
        "website": "https://mahadiscom.in",
        "portal": "https://wss.mahadiscom.in",
        "contact_information": "Hongkong Bank Building, M.G. Road, Fort, Mumbai-400001."
    },
    {
        "id": "dept-fda-006",
        "name": "Food and Drugs Administration (FDA), Maharashtra",
        "description": "Regulatory authority for food business licensing and pharmaceutical manufacturing licenses.",
        "website": "https://fda.maharashtra.gov.in",
        "portal": "https://foscos.fssai.gov.in",
        "contact_information": "Survey No. 341, Bandra-Kurla Complex, Madhusudan Kalelkar Marg, Bandra (E), Mumbai-400051."
    },
    {
        "id": "dept-fire-007",
        "name": "Maharashtra Fire Services (Directorate of Fire)",
        "description": "Issues provisional and final fire safety No Objection Certificates (NOC) for industrial buildings.",
        "website": "https://nfs.maharashtra.gov.in",
        "portal": "https://maitri.mahaonline.gov.in",
        "contact_information": "Maharashtra Fire Academy, Vidyanagari, Kalina, Santacruz (E), Mumbai-400098."
    }
]

DEMO_INDUSTRIES = [
    {
        "id": "ind-food-001",
        "name": AGRO_FOOD,
        "sector": "Agro & Food Processing",
        "description": "Agro-processing, fruit pulping, dairy processing, packaged food products, and cold chain operations.",
        "basic_setup_information": {
            "key_regulators": ["MPCB", "FSSAI / FDA Maharashtra", "MIDC", "Local Municipal Authority"],
            "typical_pollution_category": "Orange",
            "priority_zones": ["Pune (Baramati, Hadapsar)", "Nashik", "Kolhapur", "Chhatrapati Sambhajinagar"],
            "setup_stages": [
                "1. Land selection (MIDC agro food park / agricultural NA)",
                "2. Water sourcing & effluent treatment planning",
                "3. MPCB Consent to Establish (CTE)",
                "4. Building Plan Approval & Fire Provisional NOC",
                "5. FSSAI Central/State License & Factory License",
                "6. MPCB Consent to Operate (CTO)"
            ]
        }
    },
    {
        "id": "ind-textile-002",
        "name": TEXTILES,
        "sector": "Textiles",
        "description": "Cotton ginning, spinning, weaving, garmenting, dyeing and printing.",
        "basic_setup_information": {
            "key_regulators": ["MPCB", "Directorate of Industries", "DISH", "MIDC"],
            "typical_pollution_category": "Red / Orange",
            "priority_zones": ["Nashik (Malegaon)", "Ichalkaranji", "Solapur", "Amravati Textile Park"],
            "setup_stages": [
                "1. Land / Shed acquisition in MIDC or designated textile cluster",
                "2. Zero Liquid Discharge (ZLD) planning for wet units",
                "3. MPCB Consent to Establish (CTE)",
                "4. Maharashtra Textile Policy Incentive Registration",
                "5. Factory License from DISH",
                "6. Consent to Operate (CTO)"
            ]
        }
    },
    {
        "id": "ind-auto-003",
        "name": AUTOMOBILE,
        "sector": "Automotive & Engineering",
        "description": "Auto parts machining, stamping, fabrication, assembly, EV components, and casting.",
        "basic_setup_information": {
            "key_regulators": ["MPCB", "DISH", "MIDC", "MSEDCL", "Fire Dept"],
            "typical_pollution_category": "Orange",
            "priority_zones": ["Chhatrapati Sambhajinagar (AURIC / Shendra-Bidkin)", "Pune (Chakan, Talegaon)", "Nashik"],
            "setup_stages": [
                "1. Industrial plot allotment via MIDC / AURIC portal",
                "2. High-Tension (HT) power feasibility via MSEDCL",
                "3. MPCB Consent to Establish (CTE)",
                "4. Factory building plan approval from DISH",
                "5. Provisional Fire NOC",
                "6. Installation, Trial runs, CTO and Factory Registration"
            ]
        }
    },
    {
        "id": "ind-it-004",
        "name": INFORMATION_TECHNOLOGY,
        "sector": "Information Technology",
        "description": "Software development, data centers, BPO/KPO, electronics design, and IT services.",
        "basic_setup_information": {
            "key_regulators": ["Directorate of Industries", "Local Municipal Corp (MCGM/PMC)", "DoT"],
            "typical_pollution_category": "White",
            "priority_zones": ["Mumbai (BKC, SEEPZ, Navi Mumbai TTC)", "Pune (Hinjawadi, Kharadi)"],
            "setup_stages": [
                "1. Commercial office lease or IT park allotment",
                "2. Shop and Establishment Registration (Gumasta)",
                "3. Maharashtra IT/ITES Policy Registration (Stamp duty waiver)",
                "4. White Category intimation to MPCB (for DG Sets >15 KVA)",
                "5. Professional Tax & GST Registration"
            ]
        }
    },
    {
        "id": "ind-pharma-005",
        "name": PHARMACEUTICALS,
        "sector": "Life Sciences & Pharma",
        "description": "Active Pharmaceutical Ingredients (API), formulations, biopharma, and medical devices.",
        "basic_setup_information": {
            "key_regulators": ["FDA Maharashtra", "MPCB", "DISH", "PESO", "MIDC"],
            "typical_pollution_category": "Red",
            "priority_zones": ["Raigad (Roha, Mahad)", "Chhatrapati Sambhajinagar", "Pune (Kurkumbh)", "Tarapur"],
            "setup_stages": [
                "1. Chemical zone land allotment in chemical MIDC",
                "2. Environmental Clearance (EC) / Prior CTE from MPCB",
                "3. PESO storage license for petroleum solvents",
                "4. Factory plan approval from DISH",
                "5. WHO-GMP inspection and Drug Manufacturing License from FDA Maharashtra",
                "6. MPCB Consent to Operate & Hazardous Waste Authorization"
            ]
        }
    },
    {
        "id": "ind-general-006",
        "name": ENGINEERING,
        "sector": "General Engineering / MSME",
        "description": "Small machine shops, sheet metal fabrication, wooden furniture, packaging and assembly.",
        "basic_setup_information": {
            "key_regulators": ["Directorate of Industries", "MPCB", "Local Municipal Authority", "MSEDCL"],
            "typical_pollution_category": "Green",
            "priority_zones": ["All 36 districts of Maharashtra"],
            "setup_stages": [
                "1. Udyam MSME Registration (Online instant)",
                "2. Municipal Trade License / Gram Panchayat NOC",
                "3. MPCB Green Consent / White Registration",
                "4. Low-Tension (LT) Industrial Power Connection",
                "5. Factory License (if >= 10 workers with power)"
            ]
        }
    }
]

# Expose the same canonical sector catalog in demo mode. These extra catalog
# entries deliberately carry no sector-specific demo claims; the real workbook
# is the source for detailed rules in production.
_detailed_demo_industries = {item["name"] for item in DEMO_INDUSTRIES}
for _index, _name in enumerate(CANONICAL_INDUSTRIES, start=1):
    if _name not in _detailed_demo_industries:
        DEMO_INDUSTRIES.append({
            "id": f"ind-sector-{_index:03d}",
            "name": _name,
            "sector": _name,
            "description": "Industry sector included in the canonical Maharashtra catalog.",
            "basic_setup_information": {
                "summary": "Demo mode has no sector-specific approval rules for this industry; use the imported workbook data for detailed recommendations."
            },
        })

DEMO_LOCATIONS = [
    {"district": "Pune", "taluka": "Haveli", "city": "Pune", "industrial_area": "MIDC Chakan / Hinjawadi", "zone": "Zone A (Industrial)"},
    {"district": "Nashik", "taluka": "Nashik", "city": "Nashik", "industrial_area": "MIDC Ambad / Satpur / Malegaon", "zone": "Zone B"},
    {"district": "Chhatrapati Sambhajinagar", "taluka": "Aurangabad", "city": "Chhatrapati Sambhajinagar", "industrial_area": "AURIC Shendra / Bidkin / Waluj", "zone": "Zone C (Incentive Zone)"},
    {"district": "Mumbai", "taluka": "Mumbai City", "city": "Mumbai", "industrial_area": "SEEPZ / BKC", "zone": "Zone A"},
    {"district": "Mumbai Suburban", "taluka": "Kurla", "city": "Mumbai", "industrial_area": "MIDC Marol / Kanjurmarg", "zone": "Zone A"},
    {"district": "Thane", "taluka": "Thane", "city": "Thane / Navi Mumbai", "industrial_area": "TTC Industrial Area", "zone": "Zone A"},
    {"district": "Raigad", "taluka": "Roha", "city": "Roha / Mahad", "industrial_area": "MIDC Chemical Zone Roha", "zone": "Zone B (Chemical Focus)"},
    {"district": "Nagpur", "taluka": "Nagpur Urban", "city": "Nagpur", "industrial_area": "MIHAN / Butibori MIDC", "zone": "Zone C (Vidarbha Focus)"}
]

DEMO_DOCUMENTS = [
    {
        "id": "doc-siteplan-001",
        "name": "[DEMO] Site Plan & Factory Layout",
        "description": "Architectural site layout indicating plant machinery, raw material storage, effluent treatment plant, and entry/exit points.",
        "issuing_authority": "Registered Architect / Town Planner",
        "validity": "Permanent unless layout modified",
        "format": "CAD Drawing (.dwg / .pdf signed)",
        "notes": "Must show clear distances from plot boundaries.",
        "last_verified": date(2024, 6, 1),
        "is_demo": True
    },
    {
        "id": "doc-dpr-002",
        "name": "[DEMO] Detailed Project Report (DPR)",
        "description": "Comprehensive report on manufacturing process, raw materials, water budget, power requirement, capital investment, and emissions.",
        "issuing_authority": "Chartered Engineer / Project Consultant",
        "validity": "Project Lifecycle",
        "format": "PDF Document",
        "notes": "Required for MPCB Consent to Establish and MAITRI Single Window.",
        "last_verified": date(2024, 6, 1),
        "is_demo": True
    },
    {
        "id": "doc-landtitle-003",
        "name": "[DEMO] Land Allotment Letter / 7/12 Extract & NA Order",
        "description": "Proof of industrial land possession (MIDC lease deed or Revenue non-agricultural NA permission with 7/12 extract).",
        "issuing_authority": "MIDC / District Collector (Revenue Dept)",
        "validity": "Lease duration / Permanent",
        "format": "Certified Copy / DigiLocker PDF",
        "notes": "Agricultural land must have formal Section 44 NA conversion or Section 42 exemption.",
        "last_verified": date(2024, 6, 1),
        "is_demo": True
    },
    {
        "id": "doc-ca-cert-004",
        "name": "[DEMO] CA Certificate for Capital Investment",
        "description": "Audited Certificate by a Chartered Accountant certifying gross capital investment in Plant & Machinery + Land & Building.",
        "issuing_authority": "Practicing Chartered Accountant (with UDIN)",
        "validity": "Financial Year",
        "format": "Signed PDF with UDIN",
        "notes": "Determines MPCB consent fee bracket and MSME classification.",
        "last_verified": date(2024, 6, 1),
        "is_demo": True
    },
    {
        "id": "doc-water-noc-005",
        "name": "[DEMO] Water Supply Commitment / Groundwater NOC",
        "description": "Water connection sanction from MIDC / Municipal body or NOC from Central Ground Water Authority (CGWA) if borewell is used.",
        "issuing_authority": "MIDC Water Dept / CGWA / Local Body",
        "validity": "5 Years",
        "format": "Official Sanction Letter",
        "notes": "Mandatory for high water-consuming industries (Food, Pharma, Textiles).",
        "last_verified": date(2024, 6, 1),
        "is_demo": True
    },
    {
        "id": "doc-outdated-sample-006",
        "name": "[DEMO] Historical Industrial Power Subsidy Guideline",
        "description": "Historical power tariff concession guideline issued under 2013 industrial policy.",
        "issuing_authority": "Directorate of Industries, Maharashtra",
        "validity": "Expired / Under Review",
        "format": "Government Circular",
        "notes": "Deliberately populated with an old verification date to test Scenario 10 outdated record detection.",
        "last_verified": date(2023, 1, 15),
        "is_demo": True
    }
]

DEMO_APPROVALS = [
    {
        "id": "app-mpcb-cte-001",
        "name": "[DEMO] MPCB Consent to Establish (CTE)",
        "description": "Mandatory prior environmental consent before commencing any construction or setup of an industrial plant.",
        "purpose": "Controls industrial pollution, reviews effluent & emission treatment plans, and imposes environmental discharge norms.",
        "department_id": "dept-mpcb-001",
        "official_portal": "https://ecmpcb.mpcb.gov.in",
        "official_source": "Water Act 1974 & Air Act 1981 via MPCB Notification No. MPCB/JD(WPC)/B-123",
        "fee": "Graded by Capital Investment: ₹25,000 (1-5 Cr), ₹50,000 (5-25 Cr), ₹1,00,000 (25-100 Cr)",
        "processing_time": "60 to 90 working days",
        "validity": "5 years or till commissioning of the plant",
        "renewal_required": False,
        "last_verified": date(2024, 6, 15),
        "status": "ACTIVE",
        "is_demo": True
    },
    {
        "id": "app-mpcb-cto-002",
        "name": "[DEMO] MPCB Consent to Operate (CTO)",
        "description": "Mandatory environmental consent required before starting actual commercial production or trial runs.",
        "purpose": "Verifies that effluent treatment plant (ETP) and air pollution control devices (APCD) are installed as per CTE conditions.",
        "department_id": "dept-mpcb-001",
        "official_portal": "https://ecmpcb.mpcb.gov.in",
        "official_source": "MPCB Operational Directives 2020",
        "fee": "Graded by Capital Investment: ₹15,000 to ₹1,50,000 per year",
        "processing_time": "45 to 60 working days",
        "validity": "1 to 5 years (depending on Red/Orange/Green category)",
        "renewal_required": True,
        "last_verified": date(2024, 6, 15),
        "status": "ACTIVE",
        "is_demo": True
    },
    {
        "id": "app-dish-fact-003",
        "name": "[DEMO] Factory Plan Approval & License",
        "description": "Approval of factory building plans and grant of Factory License under the Factories Act, 1948.",
        "purpose": "Ensures occupational safety, ventilation, emergency exits, and worker welfare compliance.",
        "department_id": "dept-dish-002",
        "official_portal": "https://dish.maharashtra.gov.in",
        "official_source": "Maharashtra Factories Rules, 1963, Rule 3 & 4",
        "fee": "₹2,000 to ₹40,000 annually based on installed horsepower (HP) and maximum worker count",
        "processing_time": "30 to 45 working days",
        "validity": "1 to 10 years (renewal option available)",
        "renewal_required": True,
        "last_verified": date(2024, 6, 15),
        "status": "ACTIVE",
        "is_demo": True
    },
    {
        "id": "app-fire-noc-004",
        "name": "[DEMO] Fire Safety Provisional / Final NOC",
        "description": "Fire safety plan appraisal (Provisional NOC) prior to construction, and Final NOC after inspection before occupancy.",
        "purpose": "Verifies fire fighting systems, hydrant placement, fire alarms, and adequate emergency escape routes.",
        "department_id": "dept-fire-007",
        "official_portal": "https://maitri.mahaonline.gov.in",
        "official_source": "Maharashtra Fire Prevention and Life Safety Measures Act, 2006",
        "fee": "₹5 to ₹15 per sq. meter of built-up area",
        "processing_time": "15 to 30 working days",
        "validity": "1 year (Annual renewal for Final NOC)",
        "renewal_required": True,
        "last_verified": date(2024, 6, 15),
        "status": "ACTIVE",
        "is_demo": True
    },
    {
        "id": "app-fda-mfg-005",
        "name": "[DEMO] FDA Drug Manufacturing License (Form 25 / 28)",
        "description": "Statutory manufacturing license for pharmaceuticals, APIs, and formulations in Maharashtra.",
        "purpose": "Ensures strict compliance with Schedule M (GMP) standards for drug production.",
        "department_id": "dept-fda-006",
        "official_portal": "https://fda.maharashtra.gov.in",
        "official_source": "Drugs and Cosmetics Act 1940 and Rules 1945",
        "fee": "₹7,500 application fee + inspection fees per product category",
        "processing_time": "90 to 120 working days",
        "validity": "5 years",
        "renewal_required": True,
        "last_verified": date(2024, 6, 15),
        "status": "ACTIVE",
        "is_demo": True
    },
    {
        "id": "app-fssai-food-006",
        "name": "[DEMO] FSSAI Food Manufacturing License",
        "description": "State or Central Food License for manufacturing, processing, or packaging food products.",
        "purpose": "Enforces food hygiene, sanitary processing, testing protocols, and labeling standards.",
        "department_id": "dept-fda-006",
        "official_portal": "https://foscos.fssai.gov.in",
        "official_source": "Food Safety and Standards Act, 2006",
        "fee": "₹3,000 to ₹7,500 per year based on production turnover / capacity",
        "processing_time": "30 to 45 working days",
        "validity": "1 to 5 years",
        "renewal_required": True,
        "last_verified": date(2024, 6, 15),
        "status": "ACTIVE",
        "is_demo": True
    },
    {
        "id": "app-outdated-sample-007",
        "name": "[DEMO] Historical Special Capital Subsidy NOC",
        "description": "Legacy capital investment subsidy certificate from older industrial package scheme.",
        "purpose": "Deliberately included to verify staleness flagging in Test Scenario 10.",
        "department_id": "dept-ind-004",
        "official_portal": "https://maitri.mahaonline.gov.in",
        "official_source": "Package Scheme of Incentives (PSI) 2013 Notification",
        "fee": "₹1,000 processing fee",
        "processing_time": "60 working days",
        "validity": "3 years",
        "renewal_required": False,
        "last_verified": date(2023, 1, 15),
        "status": "ACTIVE",
        "is_demo": True
    }
]

DEMO_APPROVAL_RULES = [
    {
        "approval_id": "app-mpcb-cte-001",
        "industry": AGRO_FOOD,
        "pollution_category": "Orange",
        "applicability": "Likely applicable",
        "conditions": {"category_in": ["Red", "Orange", "Green"], "stage_in": ["Pre-establishment", "Planning", "Construction"]}
    },
    {
        "approval_id": "app-mpcb-cte-001",
        "industry": TEXTILES,
        "pollution_category": "Red",
        "applicability": "Likely applicable",
        "conditions": {"category_in": ["Red", "Orange"], "stage_in": ["Pre-establishment", "Planning", "Construction"]}
    },
    {
        "approval_id": "app-mpcb-cte-001",
        "industry": AUTOMOBILE,
        "pollution_category": "Orange",
        "applicability": "Likely applicable",
        "conditions": {"category_in": ["Red", "Orange"], "stage_in": ["Pre-establishment", "Planning", "Construction"]}
    },
    {
        "approval_id": "app-mpcb-cte-001",
        "industry": PHARMACEUTICALS,
        "pollution_category": "Red",
        "applicability": "Likely applicable",
        "conditions": {"category_in": ["Red"], "stage_in": ["Pre-establishment", "Planning", "Construction"]}
    },
    {
        "approval_id": "app-mpcb-cte-001",
        "industry": ENGINEERING,
        "pollution_category": "Green",
        "applicability": "Potentially applicable",
        "conditions": {"category_in": ["Green"], "notes": "Green category units may utilize simplified auto-renewal CTE."}
    },
    {
        "approval_id": "app-dish-fact-003",
        "employee_min": 10,
        "construction_required": True,
        "applicability": "Likely applicable",
        "conditions": {"employee_min": 10, "notes": "Mandatory under Section 2(m)(i) of Factories Act if >= 10 workers with power."}
    },
    {
        "approval_id": "app-dish-fact-003",
        "industry": AUTOMOBILE,
        "applicability": "Likely applicable",
        "conditions": {"notes": "Mandatory for automotive manufacturing and assembly plants."}
    },
    {
        "approval_id": "app-dish-fact-003",
        "industry": PHARMACEUTICALS,
        "applicability": "Likely applicable",
        "conditions": {"notes": "Mandatory under Dangerous Operations rules."}
    },
    {
        "approval_id": "app-fire-noc-004",
        "construction_required": True,
        "applicability": "Likely applicable",
        "conditions": {"construction_required": True, "notes": "Mandatory for all new industrial building constructions in MIDC and municipal zones."}
    },
    {
        "approval_id": "app-fire-noc-004",
        "hazardous_materials": True,
        "applicability": "Likely applicable",
        "conditions": {"hazardous_materials": True, "notes": "Mandatory prior clearance when storing hazardous/flammable chemicals."}
    },
    {
        "approval_id": "app-fssai-food-006",
        "industry": AGRO_FOOD,
        "applicability": "Likely applicable",
        "conditions": {"industry_match": AGRO_FOOD, "notes": "Mandatory for all food, beverage, dairy, and agro processing units."}
    },
    {
        "approval_id": "app-fda-mfg-005",
        "industry": PHARMACEUTICALS,
        "applicability": "Likely applicable",
        "conditions": {"industry_match": PHARMACEUTICALS, "notes": "Mandatory prior to manufacturing any bulk drug, API, or formulation."}
    },
    {
        "approval_id": "app-outdated-sample-007",
        "district": "Pune",
        "applicability": "Depends on conditions",
        "conditions": {"district": "Pune", "notes": "Legacy subsidy verification."}
    }
]

DEMO_APPROVAL_DOCUMENTS = [
    {"approval_id": "app-mpcb-cte-001", "document_id": "doc-siteplan-001", "mandatory": True, "condition": "Layout showing ETP location."},
    {"approval_id": "app-mpcb-cte-001", "document_id": "doc-dpr-002", "mandatory": True, "condition": "Covering manufacturing process & emissions."},
    {"approval_id": "app-mpcb-cte-001", "document_id": "doc-landtitle-003", "mandatory": True, "condition": "MIDC allotment or registered lease."},
    {"approval_id": "app-mpcb-cte-001", "document_id": "doc-ca-cert-004", "mandatory": True, "condition": "Certifying gross plant & machinery capital investment."},
    {"approval_id": "app-mpcb-cte-001", "document_id": "doc-water-noc-005", "mandatory": False, "condition": "Required if daily water intake > 25 KLD."},
    {"approval_id": "app-dish-fact-003", "document_id": "doc-siteplan-001", "mandatory": True, "condition": "Cross-sectional drawings signed by registered architect."},
    {"approval_id": "app-dish-fact-003", "document_id": "doc-landtitle-003", "mandatory": True, "condition": "Proof of premises ownership/lease."},
    {"approval_id": "app-fire-noc-004", "document_id": "doc-siteplan-001", "mandatory": True, "condition": "Indicating hydrant points and 6m wide driveway."},
    {"approval_id": "app-fssai-food-006", "document_id": "doc-siteplan-001", "mandatory": True, "condition": "Sanitary and food handling layout."},
    {"approval_id": "app-fssai-food-006", "document_id": "doc-water-noc-005", "mandatory": True, "condition": "Potable water test report."},
    {"approval_id": "app-fda-mfg-005", "document_id": "doc-siteplan-001", "mandatory": True, "condition": "Cleanroom & HVAC AHU zoning drawings."},
    {"approval_id": "app-fda-mfg-005", "document_id": "doc-dpr-002", "mandatory": True, "condition": "Drug formulation dossiers & testing lab specs."},
    {"approval_id": "app-fda-mfg-005", "document_id": "doc-landtitle-003", "mandatory": True, "condition": "Approved industrial land title."}
]
