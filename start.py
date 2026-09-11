# from langchain.chat_models import init_chat_model
from langchain_anthropic import ChatAnthropic

from app.config.config import settings

print(settings)


# Set the API key as an environment variable for LangChain
# os.environ["ANTHROPIC_API_KEY"] = settings.ANTHROPIC_API_KEY # type: ignore

# model = init_chat_model(
#     model=settings.ANTHROPIC_MODEL,
#     model_provider="anthropic",
#     api_key=settings.ANTHROPIC_API_KEY,
# )

if settings.ANTHROPIC_API_KEY is None:
    raise ValueError("ANTHROPIC_API_KEY is not set in environment")

if settings.ANTHROPIC_MODEL is None:
    raise ValueError("ANTHROPIC_MODEL is not set in environment")

model = ChatAnthropic(
    api_key=settings.ANTHROPIC_API_KEY,
    timeout=30,
    model_name=settings.ANTHROPIC_MODEL,
    stop=None,
)

response = model.invoke("What's the capital of Romania?")

print(response)
