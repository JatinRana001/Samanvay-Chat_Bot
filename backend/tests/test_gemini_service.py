from app.schemas.approval import ApprovalRecommendationResult
from app.schemas.profile import BusinessProfile
from app.services import gemini_service


def sample_result():
    return ApprovalRecommendationResult(
        business_profile=BusinessProfile(industry="Agro & Food Processing", district="Pune"),
        basic_setup_steps=[],
        approvals=[],
        document_checklist={"verified_have": [], "missing_required": [], "info_needed": []},
        next_steps=[],
    )


def test_empty_api_key_uses_deterministic_fallback(monkeypatch):
    monkeypatch.setattr(gemini_service.settings, "GEMINI_API_KEY", "")
    explanation = gemini_service.GeminiExplanationService.generate_explanation(sample_result())
    assert "Food Processing" in explanation
    assert "Business Profile Assessment" in explanation


def test_gemini_api_exception_uses_deterministic_fallback(monkeypatch):
    class BrokenClient:
        def __init__(self, **kwargs):
            self.models = self

        def generate_content(self, *args, **kwargs):
            raise RuntimeError("simulated Gemini outage")

    monkeypatch.setattr(gemini_service.settings, "GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(gemini_service, "GEMINI_AVAILABLE", True)
    monkeypatch.setattr(gemini_service.genai, "Client", BrokenClient)
    monkeypatch.setattr(gemini_service.types, "GenerateContentConfig", lambda **kwargs: kwargs)
    explanation = gemini_service.GeminiExplanationService.generate_explanation(sample_result())
    assert "Food Processing" in explanation
    assert "Business Profile Assessment" in explanation
