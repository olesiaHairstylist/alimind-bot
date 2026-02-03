# bot/ai/client.py

class LLMNotConfigured(Exception):
    pass


def call_llm(system_prompt: str, user_prompt: str, timeout_sec: int = 20) -> str:
    """
    Optional LLM call.
    IMPORTANT: This project must run even if LLM is not configured.
    So by default we raise a controlled exception.
    """
    raise LLMNotConfigured("LLM is not configured (safe mode).")
