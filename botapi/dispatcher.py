from botapi.handlers import (
    MessageHandler,
    CallbackQueryHandler,
    InlineQueryHandler,
    ChosenInlineResultHandler,
    Handler
)
from botapi.filters import Filter
from pydantic import BaseModel
from typing import Optional, Callable, List
from pathlib import Path

import importlib
import logging

log = logging.getLogger(__name__)

class Dispatcher(BaseModel):
    handlers_path: Path
    handlers: List[Handler] = []

    class Config:
        arbitrary_types_allowed = True

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
