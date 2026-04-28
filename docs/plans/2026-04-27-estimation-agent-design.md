# Design: System Wyceny Projektów IT (DSPy + GEPA + Graphiti)

Data: 2026-04-27  
Autor: Adam Dabrowski (AI4IT Lead, Orange Polska)

## Kontekst

Nowy system wyceny projektów IT zastępuje ace-poc. Zachowuje tę samą funkcjonalność domenową (Generator → HITL → uczenie się z korekt) ale używa nowoczesnego stosu: DSPy+GEPA zamiast ręcznych promptów, Graphiti zamiast playbooka JSON, LangGraph zamiast Agno.
1
Dane treningowe z ace-poc (`data/training/*.json`) są migrowane. Brakujące przykłady uzupełnia skrypt generatora danych syntetycznych.

## Stos technologiczny

| Warstwa | Technologia | Uzasadnienie |
|---------|-------------|--------------|
| UI | Streamlit | Szybki start, zero JS |
| Orkiestracja | LangGraph + FastAPI | HITL interrupt, checkpointing, przyszły multi-agent routing |
| Optymalizacja promptów | DSPy 2.x + GEPA | Najlepsza jakość 2026, 35× efektywniej niż RL |
| Pamięć długoterminowa | Graphiti (Zep OSS) | Temporalny graf, self-hosted, EU/GDPR |
| LLM | LiteLLM | Generyczny, switchable (Claude/GPT/Gemini) |
| Monitoring | MLflow + Langfuse | Metryki GEPA + tracing agentów |

## Architektura wysokopoziomowa

```
Streamlit UI
    │  (HTTP)
    ▼
FastAPI (thin bridge)
    │
    ▼
LangGraph Graf
    ├── intake_node         ← zbiera opis projektu
    ├── context_node        ← Graphiti: historia klienta, wzorce ryzyk
    ├── estimation_node     ← DSPy ChainOfThought(WycenaIT)
    ├── [INTERRUPT]         ← PM zatwierdza lub koryguje w Streamlit
    └── store_node          ← Graphiti update + trainset + trigger GEPA
    
    ↓ (co 50 nowych korekt, offline)
    
GEPA re-optymalizacja
    └── programs/v{N}_gepa.json  ← hot-swap w produkcji
```

## DSPy Signature

```python
class WycenaIT(dspy.Signature):
    """Wycena projektu IT w roboczogodzinach."""
    
    opis_projektu: str = dspy.InputField(desc="Pełen opis wymagań projektu")
    historia_klienta: str = dspy.InputField(desc="Historia projektów klienta z Graphiti")
    wzorce_ryzyk: str = dspy.InputField(desc="Wyuczone wzorce ryzyk z Graphiti")
    
    szacunek_godzin: int = dspy.OutputField(desc="Liczba roboczogodzin")
    uzasadnienie: str = dspy.OutputField(desc="Wyjaśnienie metodyki wyceny")
    pewnosc: float = dspy.OutputField(desc="Pewność wyceny 0.0–1.0")
```

## Metryka GEPA

Trzy składowe:
- **Dokładność (50%)** — błąd względny szacunku vs rzeczywiste godziny
- **Uzasadnienie (30%)** — długość i jakość wyjaśnienia
- **Kalibracja pewności (20%)** — czy pewność 0.3–0.9 (nie skrajności)

Tekstowy feedback dla GEPA: np. "szacunek za niski, brak narzutu na testy integracyjne".

## Pętla samouczenia

```
Nowa wycena → PM koryguje → store_node
    │
    ▼
trainset (spec + rzeczywiste godziny)  ← migracja z ace-poc + syntetyczne
    │
    (gdy N >= 50 nowych korekt)
    ▼
GEPA compile (20–50 iteracji)
    │
    ▼
programs/v{N}_gepa.json  → hot-swap
```

## Struktura katalogów

```
gepa/
├── app.py                      # Streamlit UI
├── api.py                      # FastAPI (LangGraph bridge)
├── graph/
│   ├── workflow.py             # LangGraph graf (5 węzłów)
│   └── state.py                # EstimationState (TypedDict)
├── dspy_modules/
│   ├── signatures.py           # WycenaIT
│   ├── estimator.py            # ChainOfThought moduł
│   ├── metrics.py              # metryka GEPA z feedbackiem
│   └── programs/               # v1_baseline.json, v2_gepa.json
├── optimization/
│   ├── gepa_runner.py          # GEPA trigger + compile
│   └── trainset.py             # zarządzanie przykładami
├── memory/
│   ├── graphiti_client.py      # Graphiti integration
│   └── schemas.py              # ProjektIT, Klient, WzorzecRyzyka
├── data/
│   ├── training/               # przeniesione z ace-poc
│   └── generate_synthetic.py   # generator danych syntetycznych
└── config/
    └── settings.py             # LiteLLM config
```

## Roadmapa

### Faza 1 — Fundament (3–4 tygodnie)
**Cel:** działający agent, zbieranie danych  
**Metryka:** agent odpowiada na każde zapytanie, PM może korygować

- Setup infrastruktury: Graphiti self-hosted, LiteLLM config
- DSPy Signatures + ChainOfThought baseline (few-shot z ace-poc)
- LangGraph graf (5 węzłów + HITL interrupt)
- FastAPI bridge + Streamlit UI
- Migracja danych treningowych z ace-poc
- Generator danych syntetycznych

### Faza 2 — Samouczenie (3–4 tygodnie)
**Cel:** pierwszy cykl GEPA  
**Metryka:** 80% szacunków w zakresie ±25% rzeczywistych

- Metryka GEPA z tekstowym feedbackiem
- Pierwszy GEPA compile na syntetycznych danych (50+ przykładów)
- MLflow tracking metryk optymalizacji
- Langfuse tracing każdego wywołania
- A/B: zoptymalizowany agent vs baseline w Streamlit

### Faza 3 — Produkcja (4–6 tygodni)
**Cel:** system uczy się automatycznie  
**Metryka:** 85%+ szacunków w zakresie ±20%, auto-trigger GEPA co 100 nowych wycen

- Auto-trigger GEPA re-optymalizacji
- Specjalizowane agenty per typ projektu (legacy, nowy, AI, migracja)
- LangGraph routing do specjalizowanego agenta
- REST API dla zewnętrznych integracji
- Rozszerzenie schematów Graphiti (wzorce ryzyk, relacje technologiczne)
