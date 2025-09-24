from typing import List
from converter import Converter
from register_python_converters import register_python_converters
from register_external_converters import register_external_converters


def register_converters():
    converters: List[Converter] = register_python_converters()
    converters.extend(register_external_converters())
    return converters