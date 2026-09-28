from types import SimpleNamespace
from unittest.mock import Mock

from app.services import website_faq


def test_regex_faq_hit_does_not_call_gemini(monkeypatch):
    client = Mock()
    monkeypatch.setattr(website_faq, "GEMINI_AVAILABLE", True)
    monkeypatch.setattr(website_faq, "genai", SimpleNamespace(Client=client))

    response = website_faq.answer_website_question("How do I register?")

    assert response["response_type"] == "website_faq"
    assert "Register Project" in response["message"]
    client.assert_not_called()


def test_regulatory_question_is_redirected_without_calling_gemini(monkeypatch):
    client = Mock()
    monkeypatch.setattr(website_faq, "GEMINI_AVAILABLE", True)
    monkeypatch.setattr(website_faq, "genai", SimpleNamespace(Client=client))

    response = website_faq.answer_website_question("What fees apply to my project?")

    assert response["response_type"] == "regulatory_redirect"
    assert response["message"] == website_faq.REGULATORY_REDIRECT
    client.assert_not_called()


def test_ambiguous_question_gets_clarification_without_calling_gemini(monkeypatch):
    client = Mock()
    monkeypatch.setattr(website_faq, "GEMINI_AVAILABLE", True)
    monkeypatch.setattr(website_faq, "genai", SimpleNamespace(Client=client))

    response = website_faq.answer_website_question("How do I find approvals?")

    assert response["response_type"] == "clarification"
    assert response["message"] == website_faq.AMBIGUOUS_QUESTION
    client.assert_not_called()


def test_unmatched_question_uses_gemini_and_website_system_prompt(monkeypatch):
    generate_content = Mock(return_value=SimpleNamespace(text="Use the homepage cards to get started."))
    client = SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))
    client_factory = Mock(return_value=client)
    monkeypatch.setattr(website_faq.settings, "GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(website_faq, "GEMINI_AVAILABLE", True)
    monkeypatch.setattr(website_faq, "genai", SimpleNamespace(Client=client_factory))
    monkeypatch.setattr(
        website_faq,
        "types",
        SimpleNamespace(GenerateContentConfig=lambda **kwargs: kwargs),
    )

    response = website_faq.answer_website_question("Where can I read about the site's purpose?")

    assert response == {
        "response_type": "fallback",
        "message": "Use the homepage cards to get started.",
    }
    client_factory.assert_called_once_with(api_key="test-key")
    config = generate_content.call_args.kwargs["config"]
    assert config["system_instruction"] == website_faq.WEBSITE_ASSISTANT_SYSTEM_PROMPT


def test_unmatched_question_falls_back_when_gemini_key_is_unset(monkeypatch):
    client = Mock()
    monkeypatch.setattr(website_faq.settings, "GEMINI_API_KEY", "")
    monkeypatch.setattr(website_faq, "GEMINI_AVAILABLE", True)
    monkeypatch.setattr(website_faq, "genai", SimpleNamespace(Client=client))

    response = website_faq.answer_website_question("Where can I read about the site's purpose?")

    assert response["response_type"] == "fallback"
    assert response["message"] == website_faq.WEBSITE_FALLBACK
    client.assert_not_called()


def test_unmatched_question_falls_back_when_gemini_call_fails(monkeypatch):
    client_factory = Mock(side_effect=RuntimeError("Gemini unavailable"))
    monkeypatch.setattr(website_faq.settings, "GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(website_faq, "GEMINI_AVAILABLE", True)
    monkeypatch.setattr(website_faq, "genai", SimpleNamespace(Client=client_factory))

    response = website_faq.answer_website_question("Where can I read about the site's purpose?")

    assert response["response_type"] == "fallback"
    assert response["message"] == website_faq.WEBSITE_FALLBACK
