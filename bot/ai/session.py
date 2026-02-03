# bot/ai/session.py

awaiting_ai_query: set[int] = set()

def set_awaiting(user_id: int) -> None:
    awaiting_ai_query.add(user_id)

def is_awaiting(user_id: int) -> bool:
    return user_id in awaiting_ai_query

def clear_awaiting(user_id: int) -> None:
    awaiting_ai_query.discard(user_id)
