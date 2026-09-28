"""Canonical industry names and compatibility mappings for Samanvay data."""

from typing import Optional, Tuple


ELECTRIC_VEHICLES = "Electric Vehicles (EV) Manufacturing"
AEROSPACE_DEFENCE = "Aerospace & Defence Manufacturing"
INFORMATION_TECHNOLOGY = "Information Technology (IT) & IT-Enabled Services (ITeS)"
ESDM_SEMICONDUCTORS = "Electronic System Design & Manufacturing (ESDM) & Semiconductors"
BIOTECH_MEDICAL = "Biotechnology, Medical & Diagnostic Devices"
AGRO_FOOD = "Agro & Food Processing"
TEXTILES = "Textiles (incl. Technical Textiles)"
GREEN_ENERGY = "Green Energy / Renewable Energy & Biofuel"
LOGISTICS = "Logistics & Warehousing"
AUTOMOBILE = "Automobile & Auto Components"
PHARMACEUTICALS = "Pharmaceuticals & Chemicals"
GEMS_JEWELLERY = "Gems & Jewellery"
ENGINEERING = "Engineering & Capital Goods"
CEMENT_STEEL = "Cement & Steel"
MINERAL_FOREST = "Mineral & Forest-based Industries"
REAL_ESTATE_CONSTRUCTION = "Real Estate & Construction"
INDUSTRY_4_0 = "Industry 4.0 (AI, Robotics, IoT, 3D Printing, Nanotechnology)"
DAIRY_SUGAR = "Dairy, Sugar & Agro-Cooperative Processing"
DATA_CENTRES = "Data Centres"
GLOBAL_CAPABILITY_CENTRES = "Global Capability Centres (GCC)"

CANONICAL_INDUSTRIES = (
    ELECTRIC_VEHICLES,
    AEROSPACE_DEFENCE,
    INFORMATION_TECHNOLOGY,
    ESDM_SEMICONDUCTORS,
    BIOTECH_MEDICAL,
    AGRO_FOOD,
    TEXTILES,
    GREEN_ENERGY,
    LOGISTICS,
    AUTOMOBILE,
    PHARMACEUTICALS,
    GEMS_JEWELLERY,
    ENGINEERING,
    CEMENT_STEEL,
    MINERAL_FOREST,
    REAL_ESTATE_CONSTRUCTION,
    INDUSTRY_4_0,
    DAIRY_SUGAR,
    DATA_CENTRES,
    GLOBAL_CAPABILITY_CENTRES,
)

# Names emitted by the older demo seeders and early workbook revisions.
# Small Scale Light Manufacturing is a broad legacy bucket; mapping it to
# Engineering & Capital Goods is approximate until sector-specific rules exist.
INDUSTRY_ALIASES = {
    "food processing": AGRO_FOOD,
    "textile & apparel manufacturing": TEXTILES,
    "textiles & garments": TEXTILES,
    "textiles": TEXTILES,
    "automobile & engineering": AUTOMOBILE,
    "it / ites & software development": INFORMATION_TECHNOLOGY,
    "it & software services": INFORMATION_TECHNOLOGY,
    "information technology": INFORMATION_TECHNOLOGY,
    "pharmaceuticals & bulk drugs": PHARMACEUTICALS,
    "pharmaceuticals": PHARMACEUTICALS,
    "small scale light manufacturing": ENGINEERING,
}


def normalize_industry(value: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """Return (canonical name, optional legacy qualifier) for an industry label."""
    if not value or not value.strip():
        return None, None

    label = value.strip()
    folded = label.casefold()
    canonical_by_folded = {name.casefold(): name for name in CANONICAL_INDUSTRIES}
    if folded in canonical_by_folded:
        return canonical_by_folded[folded], None

    for canonical in sorted(CANONICAL_INDUSTRIES, key=len, reverse=True):
        folded_canonical = canonical.casefold()
        for separator in (" - ", " (", ": "):
            prefix = folded_canonical + separator
            if folded.startswith(prefix):
                return canonical, label[len(prefix):].rstrip(") ") or None

    aliases = sorted(INDUSTRY_ALIASES.items(), key=lambda item: len(item[0]), reverse=True)
    for alias, canonical in aliases:
        if folded == alias:
            return canonical, None
        for separator in (" - ", " (", ": "):
            prefix = alias + separator
            if folded.startswith(prefix):
                return canonical, label[len(prefix):].rstrip(") ") or None

    return None, None


def normalize_rule_industry(
    value: Optional[str], sub_sector: Optional[str] = None
) -> Tuple[Optional[str], Optional[str]]:
    """Canonicalize a rule label and retain any embedded qualifier as sub-sector."""
    canonical, qualifier = normalize_industry(value)
    if canonical is None:
        return None, sub_sector
    if qualifier:
        if sub_sector and qualifier.casefold() not in sub_sector.casefold():
            sub_sector = f"{sub_sector}; {qualifier}"
        else:
            sub_sector = sub_sector or qualifier
    return canonical, sub_sector
