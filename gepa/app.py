import streamlit as st
import httpx

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="GEPA — Wycena IT", layout="wide")

tab_wycena, tab_dashboard = st.tabs(["Wycena projektu", "Dashboard"])

# ─── TAB 1: WYCENA ────────────────────────────────────────────

with tab_wycena:
    st.title("Agent Wyceny Projektów IT")

    if "phase" not in st.session_state:
        st.session_state.phase = "input"
        st.session_state.result = None
        st.session_state.session_id = None

    if st.session_state.phase == "input":
        with st.form("wycena_form"):
            klient = st.text_input("Nazwa klienta", placeholder="np. Orange Polska")
            opis = st.text_area(
                "Opis projektu",
                height=200,
                placeholder="Opisz wymagania projektu, technologie, zakres...",
            )
            submitted = st.form_submit_button("Wyceń projekt")

        if submitted and klient and opis:
            with st.spinner("Generuję wycenę..."):
                try:
                    resp = httpx.post(
                        f"{API_BASE}/estimate",
                        json={"klient": klient, "opis_projektu": opis},
                        timeout=60,
                    )
                    if resp.status_code == 200:
                        st.session_state.result = resp.json()
                        st.session_state.session_id = resp.json()["session_id"]
                        st.session_state.phase = "review"
                        st.rerun()
                    else:
                        st.error(f"Błąd API ({resp.status_code}): {resp.text}")
                except httpx.ConnectError:
                    st.error("Nie można połączyć z API. Czy FastAPI działa?")

    elif st.session_state.phase == "review":
        r = st.session_state.result
        st.subheader("Wynik wyceny")

        col1, col2, col3 = st.columns(3)
        col1.metric("Szacunek (godz.)", r["szacunek_godzin"])
        col2.metric("Pewność", f"{r['pewnosc']:.0%}")
        col3.metric("Sesja", r["session_id"][:8] + "...")

        st.markdown("**Uzasadnienie:**")
        st.info(r["uzasadnienie"])

        st.divider()
        st.subheader("Ocena PM")

        with st.form("approve_form"):
            decision = st.radio("Decyzja", ["Zatwierdź", "Koryguj"])
            korekta = None
            komentarz = ""
            if decision == "Koryguj":
                korekta = st.number_input(
                    "Rzeczywista liczba godzin",
                    min_value=1,
                    value=r["szacunek_godzin"],
                )
                komentarz = st.text_area("Komentarz (opcjonalny)")
            submitted = st.form_submit_button("Zatwierdź i zapisz")

        if submitted:
            payload = {
                "session_id": st.session_state.session_id,
                "zatwierdzone": True,
                "korekta_pm": int(korekta) if korekta else None,
                "komentarz_pm": komentarz or None,
            }
            with st.spinner("Zapisuję..."):
                try:
                    resp = httpx.post(f"{API_BASE}/approve", json=payload, timeout=30)
                    if resp.status_code == 200:
                        st.success("Wycena zapisana w pamięci agenta.")
                        st.session_state.phase = "input"
                        st.session_state.result = None
                        st.rerun()
                    else:
                        st.error(f"Błąd zapisu: {resp.text}")
                except httpx.ConnectError:
                    st.error("Nie można połączyć z API.")

# ─── TAB 2: DASHBOARD ─────────────────────────────────────────

with tab_dashboard:
    st.title("Dashboard Modelu")

    try:
        info_resp = httpx.get(f"{API_BASE}/model/info", timeout=5)
        if info_resp.status_code == 200:
            info = info_resp.json()
            col1, col2 = st.columns(2)
            col1.metric("Wersja programu", info["program_version"])
            col2.metric("Ścieżka", info["program_path"] or "baseline (DSPy default)")
        else:
            st.warning("Nie można pobrać info o modelu.")
    except httpx.ConnectError:
        st.warning("API niedostępne — uruchom `uvicorn gepa.api:app --reload`")

    st.divider()

    col_reload, col_info = st.columns(2)
    with col_reload:
        if st.button("Załaduj najnowszy program (hot-swap)"):
            try:
                resp = httpx.post(f"{API_BASE}/model/reload", timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    if data["status"] == "reloaded":
                        st.success(f"Program załadowany: {data['program']}")
                    else:
                        st.info(data.get("message", "Brak zoptymalizowanego programu."))
            except httpx.ConnectError:
                st.error("API niedostępne.")

    st.divider()
    st.subheader("Jak uruchomić optymalizację ręcznie")
    st.code("""
# Gdy masz 50+ przykładów treningowych w gepa/data/training/:
.venv/bin/python -c "
from gepa.optimization.optimizer import OptimizerRunner
from gepa.dspy_modules.estimator import create_estimator
import dspy
from gepa.config.settings import settings

lm = dspy.LM(model=settings.llm_model, api_key=settings.llm_api_key.get_secret_value())
dspy.configure(lm=lm)

runner = OptimizerRunner()
student = create_estimator()
path = runner.run(student, 'gepa/data/training')
print(f'Program zapisany: {path}')
"
""", language="bash")
