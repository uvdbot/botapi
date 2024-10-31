from typing import List

from bs4 import BeautifulSoup
from pathlib import Path

from models import (
    TelegramType,
    TelegramMethod
)

from helpers import (
    write_generated_file,
    generate_type_string,
    generate_method_string,
    generate_parent_type_string,
    API_URL
)

from parser import (
    parse_method,
    parse_type,
)

import httpx
import copy
import re

types: dict[str, TelegramType] = {}
methods: dict[str, TelegramMethod] = {}

def get_items(soup: BeautifulSoup) -> List[str]:
    items = []
    for item in soup.find_all("h4"):
        if item.find_next_sibling("p"):
            items.append(item.text.strip())
    return items

def generate_types():
    final_file = "from __future__ import annotations\n\n"
    final_file += "from pydantic import BaseModel, Field, ConfigDict\n"
    final_file += "from typing import Union, Optional, Literal, List\n\n"

    for type in copy.deepcopy(types).values():
        if len(type.children) > 0:
            parent = copy.deepcopy(type)
            types.pop(parent.name)
            types[parent.name] = parent
    for type in types.values():
        if len(type.children) > 0:
            final_file += generate_parent_type_string(type)
        else:
            final_file += generate_type_string(type)
        final_file += " \n\n"

    for type in types.values():
        if len(type.children) == 0:
            final_file += f"{type.name}.model_rebuild()\n"

    write_generated_file(
        final_file,
        Path("./botapi/types.py")
    )    

def generate_methods():
    final_file = "from __future__ import annotations\n\n"
    final_file += "from pydantic import TypeAdapter, ValidationError\n"
    final_file += "from typing import Union, Optional, List\n\n"
    final_file += "from botapi.types import ("
    for type in types:
        final_file += "\n" + f"    {type},"
    final_file += "\n)\n\n"
    final_file += "import botapi\n\n"
    final_file += "class Methods:\n"
    for method in methods.values():
        final_file += generate_method_string(method)
        final_file += "\n\n"
    write_generated_file(
        final_file,
        Path("./botapi/methods.py")
    )

if __name__ == "__main__":
    response = httpx.get(API_URL)
    soup = BeautifulSoup(response.content, "html.parser")
    items = get_items(soup)

    for item in items:
        type = parse_type(soup, item)
        if not type:
            continue
        types[type.name] = type

    for item in items:
        method = parse_method(soup, item)
        if not method:
            continue
        methods[method.name] = method

    generate_types()
    generate_methods()