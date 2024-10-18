from typing import Optional, Any, Callable
from botapi.types import Update

import botapi

import re

class Filter:
    def __call__(
        self,
        client: botapi.BotAPI,
        update: Update
    ):
        return NotImplementedError

    def __invert__(self):
        return InvertFilter(self)

    def __and__(self, other):
        return AndFilter(self, other)

    def __or__(self, other):
        return OrFilter(self, other)

class InvertFilter(Filter):
    def __init__(self, filter: Filter):
        self.filter = filter

    def __call__(
        self,
        client: botapi.BotAPI,
        update: Update
    ):
        return not self.filter(client, update)

class AndFilter(Filter):
    def __init__(self, *filters: Filter):
        self.filters = filters

    def __call__(
        self,
        client: botapi.BotAPI,
        update: Update
    ):
        return all(
            filter(client, update)
            for filter in self.filters
        )

class OrFilter(Filter):
    def __init__(self, *filters: Filter):
        self.filters = filters

    def __call__(
        self,
        client: botapi.BotAPI,
        update: Update
    ):
        return any(
            filter(client, update)
            for filter in self.filters
        )

def create_filter(
    func: Callable,
    name: Optional[str] = None,
    **kwargs
) -> Filter:
    filter = type(
        name or func.__name__ or "CustomFilter",
        (Filter,),
        {"__call__": func, **kwargs}
    )
    return filter()

def text_filter(_, __, update: Update) -> bool:
    return (
        bool(update.message)
        and bool(update.message.text)
    )
text = create_filter(text_filter)
"""Filter for text messages"""

def successfull_payment_filter(_, __, update: Update) -> bool:
    return (
        bool(update.message) and
        bool(update.message.successful_payment)
    )
successfull_payment = create_filter(successfull_payment_filter)
"""Filter for successful payments"""

def document_filter(_, __, update: Update) -> bool:
    return (
        bool(update.message)
        and bool(update.message.document)
    )
document = create_filter(document_filter)
"""Filter for documents"""

def private_filter(_, __, update: Update) -> bool:
    return (
        bool(update.message)
        and update.message.chat.type == "private"
    ) or (
        bool(update.callback_query)
        and bool(update.callback_query.message)
        and bool(update.callback_query.message.chat)
        and update.callback_query.message.chat.type == "private"
    )
private = create_filter(private_filter)
"""Filter for private chats"""

def group_filter(_, __, update: Update) -> bool:
    return (
        bool(update.message)
        and update.message.chat.type in {"group", "supergroup"}
    ) or (
        bool(update.callback_query)
        and update.callback_query.message.chat.type in {"group", "supergroup"}
    )
group = create_filter(group_filter)
"""Filter for group chats"""

def url_filter(_, __, update: Update) -> bool:
    return (
        bool(update.message) and
        bool(update.message.entities) and
        any((
            entity for entity in update.message.entities
            if entity.type == "url"
        ))
    ) or (
        bool(update.inline_query) and
        bool(update.inline_query.query) and
        update.inline_query.query.startswith("http")
    )
url = create_filter(url_filter)
"""Filter for URLs"""

def sudo_filter(_, api: botapi.BotAPI, update: Update) -> bool:
    return (
        bool(update.message) and
        bool(update.message.from_user) and
        update.message.from_user.id in api.sudoers
    ) or (
        bool(update.callback_query) and
        bool(update.callback_query.from_user) and
        update.callback_query.from_user.id in api.sudoers
    )
sudo = create_filter(sudo_filter)
"""Filter for sudo users"""

def command(
    command: str | re.Pattern,
    case_sensitive: bool = True
) -> Filter:
    """
    Filter for commands.
    """
    def func(flt: Any, api: botapi.BotAPI, update: Update) -> bool:
        if not text_filter(flt, api, update):
            return False
        if not update.message.text.startswith("/"):
            return False
        command_string = update.message.text.split(maxsplit=1)[0]
        if isinstance(flt.command, str):
            if not flt.case_sensitive:
                command_string = command_string.lower()
                flt.command = flt.command.lower()
            return bool(command_string == ("/" + flt.command))
        elif isinstance(flt.command, re.Pattern):
            return bool(flt.command.match(command_string))

    return create_filter(
        func,
        name="CommandFilter",
        command=command,
        case_sensitive=case_sensitive
    )

def start_value(value: str | re.Pattern) -> Filter:
    """
    Filter for the start command with a specific value.
    """
    def func(flt: Any, api: botapi.BotAPI, update: Update) -> bool:
        if not text_filter(flt, api, update):
            return False
        command_args = update.message.text.split()
        if not len(command_args) > 1:
            return False
        if command_args[0] != "/start":
            return False
        if isinstance(value, str):
            return command_args[1] == value
        elif isinstance(value, re.Pattern):
            return flt.value.match(command_args[1])

    return create_filter(
        func,
        name="StartValueFilter",
        value=value
    )

def regex(pattern: str | re.Pattern) -> Filter:
    """
    Filter for regex patterns.
    """
    def func(flt: Any, api: botapi.BotAPI, update: Update) -> bool:
        return (
            text_filter(flt, api, update) and
            (re.match(flt.pattern, update.message.text) if
            isinstance(flt.pattern , str) else
            flt.pattern.match(update.message.text))
        ) or (
            bool(update.callback_query) and
            (re.match(flt.pattern, update.callback_query.data)
            if isinstance(flt.pattern, str) else
            flt.pattern.match(update.callback_query.data))
        )
    return create_filter(
        func,
        name="RegexFilter",
        pattern=pattern
    )