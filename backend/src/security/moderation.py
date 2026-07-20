from detoxify import Detoxify

_model = None

# Thresholds - tune these based on testing. Detoxify scores range 0-1.
TOXICITY_THRESHOLD = 0.7

def get_moderation_model():
    global _model
    if _model is None:
        print("Loading content moderation model (first call only)...")
        _model = Detoxify('original')
    return _model


def check_content(text: str) -> dict:
    """
    Run toxicity/content checks on a piece of text.
    Returns: {"flagged": bool, "categories": dict, "max_score": float}
    """
    model = get_moderation_model()
    results = model.predict(text)

    # results is a dict like {"toxicity": 0.02, "severe_toxicity": 0.01, "obscene": 0.03, ...}
    max_category = max(results, key=results.get)
    max_score = results[max_category]

    flagged = max_score >= TOXICITY_THRESHOLD

    return {
        "flagged": flagged,
        "categories": {k: float(v) for k, v in results.items()},
        "max_category": max_category,
        "max_score": float(max_score),
    }


if __name__ == "__main__":
    test_inputs = [
        "How many days of annual leave do I get?",
        "You are so stupid, I hate this company",
    ]

    for text in test_inputs:
        result = check_content(text)
        print(f"\nInput: {text}")
        print(f"Flagged: {result['flagged']}")
        print(f"Top category: {result['max_category']} ({result['max_score']:.4f})")