from typing import Callable

import botapi.api
import botapi.types

class Handler:
    async def run(
        self,
        api: botapi.api.BotAPI,
        update: botapi.types.Update
    ):
        pass

class MessageHandler(Handler):
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
        if not bool(update.message):
            return False
        if self.filters != None:
            if self.filters(update):
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
        if self.filters != None:
            if self.filters(update):
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
        if self.filters != None:
            if self.filters(update):
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
        if self.filters != None:
            if self.filters(update):
                return await self.callback(api, update)
        else:
            return await self.callback(api, update)
        return False