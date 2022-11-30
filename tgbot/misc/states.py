"""Describes the state for the FSM (Final State Machine)"""

from aiogram.dispatcher.filters.state import StatesGroup, State


class WeatherSetupDialog(StatesGroup):
    """Describes the steps of the weather setup dialog"""

    EnterCityName = State()
