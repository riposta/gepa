import dspy
import json
import uuid
from pathlib import Path


class GenerujPrzykladWyceny(dspy.Signature):
    """Wygeneruj realistyczny przykład projektu IT do wyceny dla Orange Polska."""

    kontekst: str = dspy.InputField(desc="Typ projektu i technologie do użycia")

    opis_projektu: str = dspy.OutputField(desc="Realistyczny opis wymagań projektu IT")
    rzeczywiste_godziny: int = dspy.OutputField(desc="Rzeczywista liczba roboczogodzin (100-2000)")
    typ_projektu: str = dspy.OutputField(desc="nowy | legacy | migracja | ai")
    technologie: str = dspy.OutputField(desc="Lista technologii jako JSON array string")
    uzasadnienie: str = dspy.OutputField(desc="Krótkie uzasadnienie liczby godzin")


KONTEKSTY = [
    "nowy projekt webowy REST API Python",
    "migracja systemu legacy Java 8 do Java 17",
    "integracja z systemem SAP ERP",
    "projekt AI/ML pipeline na danych telco",
    "aplikacja mobilna React Native",
    "portal self-service dla klientów telco",
    "mikroserwisy na Kubernetes AWS",
    "system raportowania BI z Spark",
    "modernizacja bazy danych Oracle do PostgreSQL",
    "chatbot obsługa klienta LLM",
]


def generate(n: int, output_dir: str) -> int:
    generator = dspy.Predict(GenerujPrzykladWyceny)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for i in range(n):
        kontekst = KONTEKSTY[i % len(KONTEKSTY)]
        result = generator(kontekst=kontekst)
        example = {
            "opis_projektu": result.opis_projektu,
            "rzeczywiste_godziny": result.rzeczywiste_godziny,
            "typ_projektu": result.typ_projektu,
            "technologie": result.technologie,
            "uzasadnienie": result.uzasadnienie,
            "zrodlo": "synthetic",
        }
        fname = out / f"synthetic_{uuid.uuid4().hex[:8]}.json"
        fname.write_text(json.dumps(example, ensure_ascii=False, indent=2))

    return n


if __name__ == "__main__":
    import sys
    from gepa.config.settings import settings
    lm = dspy.LM(
        model=settings.llm_model,
        api_key=settings.llm_api_key.get_secret_value() or None,
    )
    dspy.configure(lm=lm)
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    count = generate(n=n, output_dir="gepa/data/training")
    print(f"Wygenerowano {count} przykładów syntetycznych.")
