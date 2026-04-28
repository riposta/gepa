from typing import TypedDict


class EstimationState(TypedDict):
    session_id: str
    klient: str
    opis_projektu: str
    typ_projektu: str
    historia_klienta: str
    wzorce_ryzyk: str
    szacunek_godzin: int | None
    uzasadnienie: str | None
    pewnosc: float | None
    korekta_pm: int | None
    komentarz_pm: str | None
    zatwierdzone: bool
