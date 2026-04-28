import dspy

TYPY_PROJEKTOW = ["legacy", "nowy", "ai", "migracja"]


class KlasyfikacjaTypu(dspy.Signature):
    """Sklasyfikuj typ projektu IT na podstawie jego opisu."""

    opis_projektu: str = dspy.InputField(
        desc="Opis projektu IT"
    )
    typ_projektu: str = dspy.OutputField(
        desc=(
            "Typ projektu — JEDNO słowo: "
            "legacy (modernizacja/utrzymanie starego systemu), "
            "nowy (nowy system od zera), "
            "ai (projekt z ML/AI/LLM), "
            "migracja (przeniesienie do chmury lub nowej platformy)"
        )
    )


def create_classifier() -> dspy.ChainOfThought:
    return dspy.ChainOfThought(KlasyfikacjaTypu)


def normalize_type(raw: str) -> str:
    cleaned = raw.lower().strip()
    for typ in TYPY_PROJEKTOW:
        if typ in cleaned:
            return typ
    return "nowy"
