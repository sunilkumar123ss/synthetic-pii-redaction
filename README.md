# Synthetic PII redaction evaluator

Evaluate a small regex redactor against character-offset annotations, reporting exact-span precision/recall/F1 and redacted text. The supplied email addresses and phone numbers are synthetic examples.

~~~sh
python3 main.py --input example.json
python3 -m unittest -v
~~~

The detector covers conventional ASCII emails and a limited set of phone formats. It intentionally illustrates limitations: a ten-digit order number can be a false positive and an obfuscated email can be missed. Offsets use Python Unicode code-point positions, not UTF-8 byte offsets. Empty truth/prediction denominators receive precision/recall 1, with raw counts also shown.

This is not a production privacy filter. Names, addresses, IDs, Unicode email forms, many phone formats, contextual ambiguity, and adversarial obfuscation are unsupported. Output can still contain missed sensitive text; use synthetic data for the demo and do not treat regex redaction as anonymization.

## Scope

This is an educational implementation with synthetic fixtures. Run the tests and inspect the documented limits before adapting it.

## Repository checks

```sh
python3 verify.py
```

This runs the isolated test suite, synthetic example, and CLI help. The included GitHub Actions workflow repeats these checks when the repository is published. No hosted CI result is claimed by the local verification report.
