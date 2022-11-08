from aiogram.dispatcher.filters.state import StatesGroup, State


class UserInput(StatesGroup):
    """Describes the state for the FSM (Final State Machine)"""
    EnterCityName = State()
