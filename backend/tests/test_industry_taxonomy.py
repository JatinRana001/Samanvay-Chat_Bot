import pytest

from app.industry_taxonomy import (
    AGRO_FOOD,
    AUTOMOBILE,
    CANONICAL_INDUSTRIES,
    ENGINEERING,
    INFORMATION_TECHNOLOGY,
    PHARMACEUTICALS,
    TEXTILES,
    normalize_industry,
    normalize_rule_industry,
)


@pytest.mark.parametrize(
    "legacy,canonical",
    [
        ("Food Processing", AGRO_FOOD),
        ("Textile & Apparel Manufacturing", TEXTILES),
        ("Textiles & Garments", TEXTILES),
        ("Automobile & Engineering", AUTOMOBILE),
        ("IT / ITES & Software Development", INFORMATION_TECHNOLOGY),
        ("IT & Software Services", INFORMATION_TECHNOLOGY),
        ("Pharmaceuticals & Bulk Drugs", PHARMACEUTICALS),
        ("Small Scale Light Manufacturing", ENGINEERING),
    ],
)
def test_legacy_industry_names_resolve_to_canonical_names(legacy, canonical):
    assert normalize_industry(legacy) == (canonical, None)


@pytest.mark.parametrize(
    "legacy,canonical,qualifier",
    [
        ("Aerospace & Defence Manufacturing - MRO", "Aerospace & Defence Manufacturing", "MRO"),
        ("Automobile & Auto Components (paint shop)", AUTOMOBILE, "paint shop"),
        ("Textiles (incl. Technical Textiles) - processing/dyeing", TEXTILES, "processing/dyeing"),
        ("IT & Software Services - BPO", INFORMATION_TECHNOLOGY, "BPO"),
    ],
)
def test_industry_rule_qualifiers_are_preserved_as_subsector(legacy, canonical, qualifier):
    assert normalize_industry(legacy) == (canonical, qualifier)
    assert normalize_rule_industry(legacy) == (canonical, qualifier)


def test_canonical_catalog_has_all_twenty_workbook_industries():
    assert len(CANONICAL_INDUSTRIES) == 20
