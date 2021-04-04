from aiogram.dispatcher.filters.state import StatesGroup, State


class Ordering(StatesGroup):
    AddressConfirmation = State()
    AddressRequest = State()
    PhoneNumberConfirmation = State()
    PhoneNumberRequest = State()
    OrderConfrimation = State()
    Payment = State()
