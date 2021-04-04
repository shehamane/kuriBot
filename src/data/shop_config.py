from aiogram.types import ShippingOption, LabeledPrice

IS_PREPAYMENT = True
CURRENCY = "RUB"
NEED_NAME = False
NEED_PHONE_NUMBER = False
NEED_EMAIL = False
NEED_SHIPPING_ADDRESS = False

RUSSIAN_POST_SHIPPING_OPTION = ShippingOption(id='ru_post', title='Почтой России').add(
    LabeledPrice("Доставка почтой России", 100000)
)
PICKUP_SHIPPING_OPTION = ShippingOption(id='pickup', title="Самовывоз").add(
    LabeledPrice("Самовывоз в Махачкале", 0)
)
