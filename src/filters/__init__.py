from aiogram import Dispatcher


# from .is_admin import AdminFilter


def setup(dp: Dispatcher):
    from .is_numeric import IsNumericFilter
    text_messages = [
        dp.message_handlers,
        dp.edited_message_handlers,
        dp.channel_post_handlers,
        dp.edited_channel_post_handlers,
    ]

    dp.filters_factory.bind(IsNumericFilter, event_handlers=text_messages)
