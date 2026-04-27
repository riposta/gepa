import dspy


class WycenaIT(dspy.Signature):
    """Wycena projektu IT w roboczogodzinach na podstawie opisu i historii."""

    opis_projektu: str = dspy.InputField(
        desc="Pełen opis wymagań projektu IT"
    )
    historia_klienta: str = dspy.InputField(
        desc="Historia poprzednich projektów klienta z Graphiti (lub 'Brak historii.')"
    )
    wzorce_ryzyk: str = dspy.InputField(
        desc="Wyuczone wzorce ryzyk z Graphiti (lub 'Brak wzorców.')"
    )

    szacunek_godzin: int = dspy.OutputField(
        desc="Szacunkowa liczba roboczogodzin (liczba całkowita)"
    )
    uzasadnienie: str = dspy.OutputField(
        desc="Szczegółowe wyjaśnienie metodyki wyceny z podziałem na komponenty"
    )
    pewnosc: float = dspy.OutputField(
        desc="Pewność wyceny od 0.0 (brak pewności) do 1.0 (pełna pewność)"
    )
