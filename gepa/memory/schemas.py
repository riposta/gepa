from pydantic import BaseModel


class ProjektIT(BaseModel):
    nazwa: str
    technologie: list[str]
    typ: str  # "nowy" | "legacy" | "migracja" | "ai"
    budzet_szacowany_godz: float | None = None
    budzet_rzeczywisty_godz: float | None = None
    odchylenie_procent: float | None = None


class Klient(BaseModel):
    nazwa: str
    branza: str
    preferencje_wyceny: str = "szczegółowy"


class WzorzecRyzyka(BaseModel):
    opis: str
    typowy_narzut_procent: float
    kiedy_wystepuje: str
