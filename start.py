"""Test Anthropic LLM integration."""

from langchain_anthropic import ChatAnthropic

from app.config.config import settings


def test_anthropic_connection():
    """Test that ChatAnthropic initializes successfully with config."""
    if settings.anthropic_api_key is None:
        raise ValueError("ANTHROPIC_API_KEY is not set in environment")

    if settings.anthropic_model is None:
        raise ValueError("ANTHROPIC_MODEL is not set in environment")

    model = ChatAnthropic(
        api_key=settings.anthropic_api_key,
        timeout=30,
        model_name=settings.anthropic_model,
        stop=None,
    )

    response = model.invoke("What's the capital of Romania?")
    print(f"Response: {response}")
    assert response is not None


if __name__ == "__main__":
    test_anthropic_connection()
