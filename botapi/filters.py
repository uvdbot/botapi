from typing import Optional, List

import botapi.types

import re

def text(update: botapi.types.Update) -> bool:
    return (
        bool(update.message)
        and bool(update.message.text)
    )

def payment(update: botapi.types.Update) -> bool:
    return bool(update.message) and \
        bool(update.message.successful_payment)

def document(update: botapi.types.Update) -> bool:
    return bool(update.message) and \
        bool(update.message.document)

def private(update: botapi.types.Update) -> bool:
    return (
        bool(update.message)
        and update.message.chat.type == "private"
    ) or (
        bool(update.callback_query)
        and bool(update.callback_query.message)
        and bool(update.callback_query.message.chat)
        and update.callback_query.message.chat.type == "private"
    )

def group(update: botapi.types.Update) -> bool:
    return (
        bool(update.message)
        and update.message.chat.type in {"group", "supergroup"}
    ) or (
        bool(update.callback_query)
        and update.callback_query.message.chat.type in {"group", "supergroup"}
    )

def command(
    update: botapi.types.Update,
    command: str | re.Pattern,
    case_sensitive: bool = True
) -> Optional[bool]:
    if not text(update):
        return False
    if not update.message.text.startswith("/"):
        return
    command_string = update.message.text.split(maxsplit=1)[0]
    if isinstance(command, str):
        if not case_sensitive:
            command_string = command_string.lower()
            command = command.lower()       
        return command_string == ("/" + command)
    elif isinstance(command, re.Pattern):
        return command.match(command_string)

def url(update: botapi.types.Update) -> bool:
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

def regex(update: botapi.types.Update, pattern: str):
    return (
        text(update) and
        re.match(pattern, update.message.text)
    ) or (
        bool(update.callback_query) and
        re.match(pattern, update.callback_query.data)
    )

def start_value(update: botapi.types.Update, value: str | re.Pattern):
    if not command(update, "start"):
        return False
    command_args = update.message.text.split()
    if not len(command_args) > 1:
        return False
    if isinstance(value, str):
        return command_args[1] == value
    elif isinstance(value, re.Pattern):
        return value.match(command_args[1])

def admin(update: botapi.types.Update, admins: Optional[List[int]] = None):
    if not admins:
        admins = []
    return (
        bool(update.message) and
        bool(update.message.from_user) and
        update.message.from_user.id in admins
    ) or (
        bool(update.callback_query) and
        bool(update.callback_query.from_user) and
        update.callback_query.from_user.id in admins
    )