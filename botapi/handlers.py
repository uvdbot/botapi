from typing import Callable

from botapi.filters import Filter
from botapi.types import Update

import botapi

class Handler:
    async def run(
        self,
        api: botapi.BotAPI,
        update: Update
    ):
        pass

class MessageHandler(Handler):
    def __init__(
        self,
        callback: Callable,
        filters: Filter,
    ):
        self.callback = callback
        self.filters = filters

    async def run(
        self,
        api: botapi.BotAPI,
        update: Update
    ):
        if not bool(update.message):
            return False
        if self.filters is not None:
            if self.filters(api, update):
                return await self.callback(api, update)
        else:
            return await self.callback(api, update)
        return False
    
class CallbackQueryHandler(Handler):
    def __init__(
        self,
        callback: Callable,
        filters: Callable,
    ):
        self.callback = callback
        self.filters = filters

    async def run(
        self,
        api: botapi.api.BotAPI,
        update: botapi.types.Update
    ):
        if not bool(update.callback_query):
            return False
        if self.filters is not None:
            if self.filters(api, update):
                return await self.callback(api, update)
        else:
            return await self.callback(api, update)
        return False
    
class InlineQueryHandler(Handler):
    def __init__(
        self,
        callback: Callable,
        filters: Callable,
    ):
        self.callback = callback
        self.filters = filters

    async def run(
        self,
        api: botapi.api.BotAPI,
        update: botapi.types.Update
    ):
        if not bool(update.inline_query):
            return False
        if self.filters is not None:
            if self.filters(api, update):
                return await self.callback(api, update)
        else:
            return await self.callback(api, update)
        return False
    
class ChosenInlineResultHandler(Handler):
    def __init__(
        self,
        callback: Callable,
        filters: Callable,
    ):
        self.callback = callback
        self.filters = filters
    
    async def run(
        self,
        api: botapi.api.BotAPI,
        update: botapi.types.Update
    ):
        if not bool(update.chosen_inline_result):
            return False
        if self.filters is not None:
            if self.filters(api, update):
                return await self.callback(api, update)
        else:
            return await self.callback(api, update)
        return False