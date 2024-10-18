from botapi.handlers import (
    MessageHandler,
    CallbackQueryHandler,
    InlineQueryHandler,
    ChosenInlineResultHandler,
    Handler
)
from botapi.filters import Filter
from botapi.types import Update
from typing import Optional, Callable, List
from pathlib import Path

import botapi
import importlib
import logging

log = logging.getLogger(__name__)

class Dispatcher:
    def __init__(
        self,
        handlers_path: Path,
    ):
        self.handlers_path: Path = handlers_path
        self.handlers: List[Handler] = []

    # Dynamically import and load every handler
    def load_handlers(self):
        n = 0
        def load(path: Path):
            nonlocal n
            for file in path.glob("*"):
                if file.is_dir():
                    load(file)
                    continue
                if file.suffix != ".py":
                    continue
                module = ".".join(file.parts[:-1]) + "." + file.stem
                importlib.import_module(module)
                n += 1
        load(self.handlers_path)
        log.info(f"Handlers imported ({n})")

    async def handle_update(
        self,
        api: botapi.BotAPI,
        update: Update,
    ):
        for handler in self.handlers:
            await handler.run(api, update)

    def message(self, filters: Optional[Filter] = None):
        def decorator(func: Callable) -> Callable:
            self.handlers.append(
                MessageHandler(
                    callback=func,
                    filters=filters,
                )
            )
            return func
        return decorator

    def callback_query(self, filters: Optional[Filter] = None):
        def decorator(func: Callable) -> Callable:
            self.handlers.append(
                CallbackQueryHandler(
                    callback=func,
                    filters=filters,
                )
            )
            return func
        return decorator

    def inline_query(self, filters: Optional[Filter] = None):
        def decorator(func: Callable) -> Callable:
            self.handlers.append(
                InlineQueryHandler(
                    callback=func,
                    filters=filters,
                )
            )
            return func
        return decorator

    def chosen_inline_result(self, filters: Optional[Filter] = None):
        def decorator(func: Callable) -> Callable:
            self.handlers.append(
                ChosenInlineResultHandler(
                    callback=func,
                    filters=filters,
                )
            )
            return func
        return decorator
