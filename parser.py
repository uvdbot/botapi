from helpers import (
    parse_telegram_type,
    parse_return_value,
    search_by_string,
    is_type,
    is_method,
    INVALID_TYPES,
    TYPE_VALIDATORS,
)

from models import (
    TelegramParameter,
    TelegramType,
    TelegramMethod,
)

from bs4 import BeautifulSoup

import re

def parse_type(soup: BeautifulSoup, item: str) -> TelegramType | None:
    obj = search_by_string(soup, "h4", item)
    if not obj:
        return None
    paragraph = obj.find_next_sibling("p")
    title = obj.text.strip()
    anchor_link = obj.find("a", class_="anchor")
    if anchor_link:
        anchor_link = anchor_link["href"]
    description = paragraph.text.strip()
    if not is_type(title):
        return None
    if title in INVALID_TYPES:
        return None
    type = TelegramType(
        name=title,
        description=description,
        anchor_link=anchor_link,
        parameters=[],
    )
    table = obj.find_next_sibling("table")
    if not table:
        return None
    prev_title = table.find_previous("h4")
    prev_title_text = prev_title.text.strip()
    is_parent = prev_title_text != title
    if is_parent:
        children = obj.find_next("ul")
        prev_chilren_title = children.find_previous("h4")
        if prev_chilren_title.text.strip() != title:
            type.is_empty = True
            return type
        for child in children.find_all("a"):
            type.children.append(child.text.strip())
        TYPE_VALIDATORS.append(type.name)
        return type
    if table:
        rows = table.select("tbody > tr")
        for row in rows:
            columns = row.find_all("td")
            param_name = columns[0].text.strip()
            param_type = columns[1].text.strip()
            param_description = columns[2].text.strip()
            is_required = not param_description.startswith("Optional")
            patterns = [
                r".*always [\"“]([\w_]+)[\"”]$",
                r".*must be ([\w_]+)$",
            ]
            literal = None
            for pattern in patterns:
                match = re.search(pattern, param_description)
                if match:
                    literal = match.group(1).replace("\"", "")
                    break
            parsed_type = parse_telegram_type(param_type)
            type.parameters.append(
                TelegramParameter(
                    name=param_name,
                    type=parsed_type,
                    is_required=is_required,
                    literal=literal
                )
            )
    return type

def parse_method(soup: BeautifulSoup, item: str) -> TelegramMethod | None:
    obj = search_by_string(soup, "h4", item)
    if not obj:
        return None
    paragraph = obj.find_next_sibling("p")
    title = obj.text.strip()
    anchor_link = obj.find("a", class_="anchor")
    if anchor_link:
        anchor_link = anchor_link["href"]
    description = paragraph.text.strip()
    if not is_method(title):
        return None
    return_type = parse_return_value(description)
    method = TelegramMethod(
        name=title,
        description=description,
        anchor_link=anchor_link,
        return_type=return_type,
        parameters=[],
    )
    table = obj.find_next_sibling("table")
    if not table:
        return None
    prev_title = table.find_previous("h4")
    prev_title_text = prev_title.text.strip()
    if prev_title_text != title:
        table = None
    if table:
        rows = table.select("tbody > tr")
        for row in rows:
            columns = row.find_all("td")
            param_name = columns[0].text.strip()
            param_type = columns[1].text.strip()
            is_required = columns[2].text.strip() == "Yes"
            param_description = columns[3].text.strip()

            parsed_type = parse_telegram_type(param_type)
            method.parameters.append(
                TelegramParameter(
                    name=param_name,
                    type=parsed_type,
                    description=param_description,
                    is_required=is_required,
                )
            )
    return method