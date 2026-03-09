from aiogram.fsm.state import State, StatesGroup


class PartnerApplyFSM(StatesGroup):
    business_name = State()
    category = State()
    request = State()
    contact = State()
    confirm = State()