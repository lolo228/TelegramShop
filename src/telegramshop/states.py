"""
FSM состояния для бота
"""
from aiogram.fsm.state import State, StatesGroup


class AddCategoryStates(StatesGroup):
    """Состояния для добавления категории"""
    name = State()
    description = State()


class EditCategoryStates(StatesGroup):
    """Состояния для редактирования категории"""
    choosing_field = State()
    entering_name = State()
    entering_description = State()


class AddProductStates(StatesGroup):
    """Состояния для добавления товара"""
    category = State()
    name = State()
    description = State()
    price = State()


class EditProductStates(StatesGroup):
    """Состояния для редактирования товара"""
    choosing_field = State()
    entering_name = State()
    entering_description = State()
    entering_price = State()


class LoadProductItemsStates(StatesGroup):
    """Состояния для загрузки товарных позиций"""
    selecting_product = State()
    entering_items = State()


class UserBalanceStates(StatesGroup):
    """Состояния для изменения баланса пользователя"""
    entering_amount = State()


class SearchUserStates(StatesGroup):
    """Состояния для поиска пользователя"""
    entering_query = State()


class BroadcastStates(StatesGroup):
    """Состояния для рассылки"""
    entering_message = State()
    adding_buttons = State()
    confirming = State()


class EditInfoTextStates(StatesGroup):
    """Состояния для редактирования информационных текстов"""
    choosing_text = State()
    entering_text = State()

