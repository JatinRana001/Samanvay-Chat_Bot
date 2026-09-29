"""Independent workbook reader used as the ground truth in golden tests."""
import json
from pathlib import Path

from openpyxl import load_workbook

from app.industry_taxonomy import normalize_rule_industry

WORKBOOK = Path(__file__).resolve().parents[1] / "data" / "Maharashtra_Industry_Approvals_Database.xlsx"


def expected_applicable(profile, workbook_path=WORKBOOK):
    book = load_workbook(workbook_path, read_only=True, data_only=True)
    try:
        approval_rows = list(book["Approvals"].values)
        approval_ids = {row[0] for row in approval_rows[1:] if row and row[0]}
        headers = [str(value).strip() if value is not None else "" for value in book["Approval_Rules"].values.__iter__().__next__()]
        result = {}
        for raw in list(book["Approval_Rules"].values)[1:]:
            row = dict(zip(headers, raw))
            approval_id = row.get("approval_id")
            if approval_id not in approval_ids:
                continue
            label = row.get("industry")
            if label and not str(label).casefold().startswith("all "):
                canonical, embedded_scope = normalize_rule_industry(str(label), None)
                requested, _ = normalize_rule_industry(profile.get("industry") or "", None)
                if canonical != requested:
                    continue
                scope = "; ".join(filter(None, (embedded_scope, row.get("activity"))))
                supplied_scope = "; ".join(filter(None, (profile.get("sub_sector"), profile.get("activity")))).casefold()
                if scope and supplied_scope and not all(part.strip().casefold() in supplied_scope for part in scope.split(";")):
                    continue
            district = row.get("district")
            if district and profile.get("district") and str(district).casefold() != str(profile["district"]).casefold():
                continue
            for key, profile_key, low in (("employees_min", "employee_count", True), ("employees_max", "employee_count", False)):
                threshold = row.get(key)
                if threshold is not None and profile.get(profile_key) is not None:
                    if low and profile[profile_key] < threshold or not low and profile[profile_key] > threshold:
                        break
            else:
                category = row.get("pollution_category")
                if category and profile.get("pollution_category") and category.casefold() != profile["pollution_category"].casefold():
                    continue
                for key in ("hazardous_materials", "construction_required"):
                    if row.get(key) is not None and profile.get(key) is not None and bool(row[key]) != bool(profile[key]):
                        break
                else:
                    stages = {part.strip().casefold() for part in str(row.get("project_stage") or "").replace("/", ";").split(";") if part.strip()}
                    requested_stages = {part.strip().casefold() for part in str(profile.get("project_stage") or "").replace("/", ";").split(";") if part.strip()}
                    if stages and requested_stages and not stages.intersection(requested_stages):
                        continue
                    try:
                        notes = json.loads(row.get("conditions") or "{}")
                    except (TypeError, json.JSONDecodeError):
                        notes = {}
                    if notes.get("notes"):
                        # Notes are preserved as an explanation, not interpreted as code.
                        pass
                    result.setdefault(approval_id, set()).add(row.get("applicability"))
        return result
    finally:
        book.close()
