from aiogram import Dispatcher


# from .is_admin import AdminFilter


def setup(dp: Dispatcher):
    from .is_numeric import IsNumericFilter
    from .is_positive import IsPositiveFilter
    from .is_user import IsUserFilter
    text_messages = [
        dp.message_handlers,
        dp.edited_message_handlers,
        dp.channel_post_handlers,
        dp.edited_channel_post_handlers,
    ]

    dp.filters_factory.bind(IsNumericFilter, event_handlers=text_messages)
    dp.filters_factory.bind(IsPositiveFilter, event_handlers=text_messages)
    dp.filters_factory.bind(IsUserFilter, event_handlers=text_messages)