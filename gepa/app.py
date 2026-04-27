import streamlit as st
import httpx

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="GEPA — Wycena IT", layout="wide")
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
                st.error("Nie można połączyć się z API. Czy serwer FastAPI jest uruchomiony?")

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
                "Rzeczywista liczba godzin (Twoja ocena)",
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
                    st.error(f"Błąd zapisu ({resp.status_code}): {resp.text}")
            except httpx.ConnectError:
                st.error("Nie można połączyć się z API.")
