from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

_analyzer = None
_anonymizer = None


def get_analyzer():
    global _analyzer
    if _analyzer is None:
        print("Loading PII analyzer (first call only)...")
        _analyzer = AnalyzerEngine()
    return _analyzer


def get_anonymizer():
    global _anonymizer
    if _anonymizer is None:
        _anonymizer = AnonymizerEngine()
    return _anonymizer


def detect_pii(text: str, score_threshold: float = 0.5, entities_to_redact: list = None) -> list:
    if entities_to_redact is None:
        entities_to_redact = [
            "EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD",
            "US_SSN", "PERSON", "IBAN_CODE", "US_BANK_NUMBER"
        ]
    analyzer = get_analyzer()
    return analyzer.analyze(text=text, language="en", entities=entities_to_redact, score_threshold=score_threshold)

def redact_pii(text: str, score_threshold: float = 0.5, entities_to_redact: list = None) -> str:
    """
    Detect and redact PII in text. Only redacts entities above the confidence threshold,
    and only for specified entity types (default: the genuinely sensitive ones).
    """
    if entities_to_redact is None:
        entities_to_redact = [
            "EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD",
            "US_SSN", "PERSON", "IBAN_CODE", "US_BANK_NUMBER"
        ]

    analyzer = get_analyzer()
    anonymizer = get_anonymizer()

    analyzer_results = analyzer.analyze(
        text=text,
        language="en",
        entities=entities_to_redact,
        score_threshold=score_threshold,
    )
    anonymized = anonymizer.anonymize(text=text, analyzer_results=analyzer_results)

    return anonymized.text

def has_pii(text: str) -> bool:
    """Quick boolean check for whether text contains any detected PII."""
    return len(detect_pii(text)) > 0


if __name__ == "__main__":
    test_inputs = [
        "How many days of annual leave do I get?",
        "My email is john.smith@company.com and my phone is 555-123-4567",
        "Contact Sarah Johnson at sarah.j@email.com for the salary details",
    ]

    for text in test_inputs:
        entities = detect_pii(text)
        redacted = redact_pii(text)
        print(f"\nInput: {text}")
        print(f"PII detected: {len(entities)} entities")
        print(f"Redacted: {redacted}")