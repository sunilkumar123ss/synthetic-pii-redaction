"""Evaluate a deliberately limited regex redactor against annotated examples."""
import argparse
import json
from pathlib import Path
import re
import sys

PATTERNS = {
    "EMAIL": re.compile(r"(?<![\w.+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?!\w)"),
    "PHONE": re.compile(r"(?<![\w+])(?:\+\d{1,3}[- ]?)?(?:\d{3}[- ]\d{3}[- ]\d{4}|\d{10})(?!\w)"),
}


def detect(text):
    if not isinstance(text, str):
        raise ValueError("text must be a string")
    candidates = sorted((m.start(), m.end(), kind) for kind, pattern in PATTERNS.items() for m in pattern.finditer(text))
    spans = []
    for start, end, kind in candidates:
        if not spans or start >= spans[-1][1]:
            spans.append((start, end, kind))
    return spans

