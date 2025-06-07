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


def redact(text, spans):
    result, position = [], 0
    for start, end, kind in spans:
        result.extend((text[position:start], f"[{kind}]"))
        position = end
    return "".join(result) + text[position:]


def evaluate(documents):
    if not isinstance(documents, list) or not documents:
        raise ValueError("documents must be a nonempty list")
    true_positive, false_positive, false_negative, results = 0, 0, 0, []
    for document in documents:
        text, annotations = document["text"], document["annotations"]
        if not isinstance(text, str) or not isinstance(annotations, list):
            raise ValueError("text must be a string and annotations a list")
        expected = []
        for annotation in annotations:
            start, end, kind = annotation["start"], annotation["end"], annotation["kind"]
            if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(text):
                raise ValueError("annotation offsets must select a nonempty text span")
            if kind not in PATTERNS:
                raise ValueError("annotation kind must be EMAIL or PHONE")
            expected.append((start, end, kind))
        expected.sort()
        if any(b[0] < a[1] for a, b in zip(expected, expected[1:])):
            raise ValueError("annotations cannot overlap")
        found = detect(text)
        truth, predicted = set(expected), set(found)
        tp, fp, fn = len(truth & predicted), len(predicted - truth), len(truth - predicted)
        true_positive += tp
        false_positive += fp
        false_negative += fn
        results.append({"redacted_text": redact(text, found), "detected_spans": found,
                        "false_positive_spans": sorted(predicted - truth),
                        "missed_spans": sorted(truth - predicted)})
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 1.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"matching": "exact offsets and kind", "true_positives": true_positive,
            "false_positives": false_positive, "false_negatives": false_negative,
            "precision": precision, "recall": recall, "f1": f1, "documents": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    try:
        input_path = Path(args.input)
        if not input_path.is_absolute():
            input_path = Path(__file__).resolve().parent / input_path
        with input_path.open(encoding="utf-8") as handle:
            data = json.load(handle)
        print(json.dumps(evaluate(data["documents"]), indent=2))
        return 0
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(f"Invalid redaction evaluation: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
