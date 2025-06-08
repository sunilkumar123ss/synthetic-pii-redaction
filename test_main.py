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

