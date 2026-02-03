# bot/ai/paid_gate.py

paid_tokens: set[int] = set()

def grant_token(user_id: int) -> None:
    paid_tokens.add(user_id)

def has_token(user_id: int) -> bool:
    return user_id in paid_tokens

def consume_token(user_id: int) -> None:
    paid_tokens.discard(user_id)
