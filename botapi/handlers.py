from typing import Callable

from botapi.filters import Filter
from botapi.types import Update

import botapi

class Handler:
    def __init__(
        self,
        callback: Callable,
        filters: Filter,
    ):
        self.callback = callback
        self.filters = filters

    def check(
        self,
        api: botapi.BotAPI,
        update: Update
    ):
        pass

class MessageHandler(Handler):
    def check(
        self,
        api: botapi.BotAPI,
        update: Update
    ):
        if not bool(update.message):
            return False
        if callable(self.filters):
            return self.filters(api, update)
        return True

class CallbackQueryHandler(Handler):
    def check(
        self,
        api: botapi.BotAPI,
        update: Update
    ):
        if not bool(update.callback_query):
            return False
        if callable(self.filters):
            return self.filters(api, update)
        return True

class InlineQueryHandler(Handler):
    def check(
        self,
        api: botapi.BotAPI,
        update: Update
    ):
        if not bool(update.inline_query):
            return False
        if callable(self.filters):
            return self.filters(api, update)
        return True

class ChosenInlineResultHandler(Handler):
    def check(
        self,
        api: botapi.BotAPI,
        update: Update
    ):
        if not bool(update.chosen_inline_result):
            return False
        if callable(self.filters):
            return self.filters(api, update)
        return True
    
class PreCheckoutQueryHandler(Handler):
    def check(
        self,
        api: botapi.BotAPI,
        update: Update
    ):
        if not bool(update.pre_checkout_query):
            return False
        if callable(self.filters):
            return self.filters(api, update)
        return True