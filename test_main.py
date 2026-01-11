import unittest
from main import detect, evaluate, redact


class RedactionTests(unittest.TestCase):
    def test_email_and_phone_offsets(self):
        text = "Email ava@example.test or +1-202-555-0134."
        spans = detect(text)
        self.assertEqual([text[a:b] for a, b, _ in spans], ["ava@example.test", "+1-202-555-0134"])
        self.assertEqual(redact(text, spans), "Email [EMAIL] or [PHONE].")
        annotations = [{"start": a, "end": b, "kind": kind} for a, b, kind in spans]
        self.assertEqual(evaluate([{"text": text, "annotations": annotations}])["f1"], 1)

    def test_false_positive_and_missed_span(self):
        result = evaluate([{"text": "ID 1234567890", "annotations": []},
                           {"text": "ava at example dot test", "annotations": [{"start": 0, "end": 23, "kind": "EMAIL"}]}])
        self.assertEqual(result["false_positives"], 1)
        self.assertEqual(result["false_negatives"], 1)
        self.assertEqual(result["f1"], 0)

    def test_empty_clean_text(self):
        result = evaluate([{"text": "", "annotations": []}])
        self.assertEqual((result["precision"], result["recall"]), (1, 1))

