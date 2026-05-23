import os
from functools import lru_cache
from pathlib import Path
from typing import TypeVar

from openai import OpenAI
from pydantic import BaseModel, ValidationError


T = TypeVar("T", bound=BaseModel)


class LLMCallError(RuntimeError):
    """Raised when the LLM call fails or returns an invalid structured response."""


def _read_api_key_from_dotenv() -> str | None:
    repo_root = Path(__file__).resolve().parent.parent
    dotenv_path = repo_root / ".env"

    if not dotenv_path.exists():
        return None

    for line in dotenv_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)
        if key.strip() != "OPENAI_API_KEY":
            continue

        return value.strip().strip("\"'")

    return None


def _resolve_api_key(explicit_api_key: str | None) -> str | None:
    if explicit_api_key:
        return explicit_api_key

    dotenv_api_key = _read_api_key_from_dotenv()
    if dotenv_api_key:
        return dotenv_api_key

    return os.getenv("OPENAI_API_KEY")


class LLMClient:
    def __init__(self, model: str = "gpt-5-mini", api_key: str | None = None) -> None:
        self.model = model
        self._client = OpenAI(api_key=_resolve_api_key(api_key))

    def call_structured(
        self,
        messages: list[dict[str, str]],
        response_model: type[T],
        max_retries: int = 1,
    ) -> T:
        last_error: Exception | None = None

        for _ in range(max_retries + 1):
            try:
                completion = self._client.chat.completions.parse(
                    model=self.model,
                    messages=messages,
                    response_format=response_model,
                )

                if not completion.choices:
                    raise LLMCallError("OpenAI returned no choices")

                choice = completion.choices[0]
                message = choice.message

                if getattr(choice, "finish_reason", None) not in (None, "stop"):
                    raise LLMCallError(
                        f"Incomplete model response: finish_reason={choice.finish_reason}"
                    )

                if getattr(message, "refusal", None):
                    raise LLMCallError(f"Model refused request: {message.refusal}")

                parsed = getattr(message, "parsed", None)
                if parsed is None:
                    raise LLMCallError("Model returned no parsed structured output")

                return parsed

            except (LLMCallError, ValidationError, TypeError, ValueError) as exc:
                raise LLMCallError(f"LLM call failed: {exc}") from exc
            except Exception as exc:
                last_error = exc

        raise LLMCallError(f"LLM call failed after retry: {last_error}") from last_error


@lru_cache(maxsize=1)
def get_default_llm_client() -> LLMClient:
    return LLMClient()
