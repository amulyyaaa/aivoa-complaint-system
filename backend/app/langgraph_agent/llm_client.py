"""
Thin wrapper around the Groq API (OpenAI-compatible chat completions).
Docs: https://console.groq.com/docs/models
"""
import json
import re
from groq import Groq

from app.config import settings

_client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None


def _get_client() -> Groq:
    global _client
    if _client is None:
        if not settings.GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Create one at https://console.groq.com "
                "and put it in backend/.env"
            )
        _client = Groq(api_key=settings.GROQ_API_KEY)
    return _client


def chat_completion(system_prompt: str, user_prompt: str, model: str = None,
                     temperature: float = 0.2) -> str:
    """Single-turn chat completion. Returns raw text content."""
    client = _get_client()
    model = model or settings.GROQ_MODEL
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
    )
    return resp.choices[0].message.content


def chat_completion_json(system_prompt: str, user_prompt: str, model: str = None,
                          temperature: float = 0.1) -> dict:
    """
    Chat completion that expects a JSON object back. gemma2-9b-it doesn't
    support a strict 'json_object' response_format, so we instruct it firmly
    in the prompt and then defensively parse/repair the output.
    """
    raw = chat_completion(system_prompt, user_prompt, model=model, temperature=temperature)
    return _extract_json(raw)


def _extract_json(raw: str) -> dict:
    # Strip markdown code fences if present
    cleaned = re.sub(r"^```(json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fall back: grab the first {...} block in the text
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        raise ValueError(f"Model did not return valid JSON:\n{raw}")
