"""Graph routing enums."""

from enum import Enum


class NextStep(str, Enum):
    PARSE = "parse"
    END = "end"


class ParseType(str, Enum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
