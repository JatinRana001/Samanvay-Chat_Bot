from typing import Any, Dict, Optional, Tuple
from app.schemas.profile import BusinessProfile

class ConditionEvaluator:

    @staticmethod
    def match_range(val: Optional[float], min_val: Optional[float], max_val: Optional[float]) -> bool:
        if val is None:
            # If value is unspecified, condition cannot be definitively satisfied
            return True if (min_val is None and max_val is None) else False
        if min_val is not None and val < min_val:
            return False
        if max_val is not None and val > max_val:
            return False
        return True

    @staticmethod
    def evaluate_rule_conditions(rule_conditions: Dict[str, Any], profile: BusinessProfile) -> Tuple[bool, Optional[str]]:
        """
        Evaluate custom JSON conditions like category_in, stage_in, etc.
        """
        if not rule_conditions:
            return True, None

        # Check pollution category in list
        if "category_in" in rule_conditions:
            allowed = rule_conditions["category_in"]
            if profile.pollution_category and profile.pollution_category.lower() not in {value.lower() for value in allowed}:
                return False, f"Requires pollution category in {allowed}, got {profile.pollution_category}"

        # Check stage in list
        if "stage_in" in rule_conditions:
            allowed_stages = rule_conditions["stage_in"]
            if profile.project_stage and profile.project_stage.lower() not in {value.lower() for value in allowed_stages}:
                return False, f"Applicable during {allowed_stages} stage"

        return True, rule_conditions.get("notes")
