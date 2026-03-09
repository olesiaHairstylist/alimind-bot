from aiogram.fsm.state import State, StatesGroup


class BizBotLead(StatesGroup):
    business_name = State()
    business_type = State()
    bot_task = State()
    contact = State()
    confirm = State()