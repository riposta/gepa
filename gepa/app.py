import streamlit as st
import httpx

from gepa.config.settings import settings

API_BASE = f"http://localhost:{settings.api_port}"

st.set_page_config(page_title="GEPA — IT Estimation", layout="wide")

tab_estimate, tab_dashboard = st.tabs(["Project estimation", "Dashboard"])

# ─── TAB 1: ESTIMATION ────────────────────────────────────────

with tab_estimate:
    st.title("IT Project Estimation Agent")

    if "phase" not in st.session_state:
        st.session_state.phase = "input"
        st.session_state.result = None
        st.session_state.session_id = None

    if st.session_state.phase == "input":
        with st.form("estimation_form"):
            client = st.text_input("Client name", placeholder="e.g. Orange Poland")
            description = st.text_area(
                "Project description",
                height=200,
                placeholder="Describe project requirements, technologies, scope...",
            )
            submitted = st.form_submit_button("Estimate project")

        if submitted and client and description:
            with st.spinner("Generating estimate..."):
                try:
                    resp = httpx.post(
                        f"{API_BASE}/estimate",
                        json={"client": client, "project_description": description},
                        timeout=60,
                    )
                    if resp.status_code == 200:
                        st.session_state.result = resp.json()
                        st.session_state.session_id = resp.json()["session_id"]
                        st.session_state.phase = "review"
                        st.rerun()
                    else:
                        st.error(f"API error ({resp.status_code}): {resp.text}")
                except httpx.ConnectError:
                    st.error("Cannot connect to API. Is FastAPI running?")

    elif st.session_state.phase == "review":
        r = st.session_state.result
        st.subheader("Estimation result")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Estimate (hrs)", r["estimated_hours"])
        col2.metric("Confidence", f"{r['confidence']:.0%}")
        col3.metric("Project type", r.get("project_type", "new").upper())
        col4.metric("Session", r["session_id"][:8] + "...")

        st.markdown("**Reasoning:**")
        st.info(r["reasoning"])

        st.divider()
        st.subheader("PM Review")

        with st.form("approve_form"):
            decision = st.radio("Decision", ["Approve", "Correct"])
            correction = None
            comment = ""
            if decision == "Correct":
                correction = st.number_input(
                    "Actual hours",
                    min_value=1,
                    value=r["estimated_hours"],
                )
                comment = st.text_area("Comment (optional)")
            submitted = st.form_submit_button("Save & confirm")

        if submitted:
            payload = {
                "session_id": st.session_state.session_id,
                "approved": True,
                "pm_correction": int(correction) if correction else None,
                "pm_comment": comment or None,
            }
            with st.spinner("Saving..."):
                try:
                    resp = httpx.post(f"{API_BASE}/approve", json=payload, timeout=30)
                    if resp.status_code == 200:
                        st.success("Estimation saved to agent memory.")
                        st.session_state.phase = "input"
                        st.session_state.result = None
                        st.rerun()
                    else:
                        st.error(f"Save error: {resp.text}")
                except httpx.ConnectError:
                    st.error("Cannot connect to API.")

# ─── TAB 2: DASHBOARD ─────────────────────────────────────────

with tab_dashboard:
    st.title("Model Dashboard")

    try:
        info_resp = httpx.get(f"{API_BASE}/model/info", timeout=5)
        if info_resp.status_code == 200:
            info = info_resp.json()
            col1, col2 = st.columns(2)
            col1.metric("Program version", info["program_version"])
            col2.metric("Path", info["program_path"] or "baseline (DSPy default)")
        else:
            st.warning("Cannot fetch model info.")
    except httpx.ConnectError:
        st.warning("API unavailable — run `uvicorn gepa.api:app --reload`")

    st.divider()

    col_reload, col_info = st.columns(2)
    with col_reload:
        if st.button("Load latest program (hot-swap)"):
            try:
                resp = httpx.post(f"{API_BASE}/model/reload", timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    if data["status"] == "reloaded":
                        st.success(f"Program loaded: {data['program']}")
                    else:
                        st.info(data.get("message", "No optimized program available."))
            except httpx.ConnectError:
                st.error("API unavailable.")

    st.divider()
    st.subheader("How to run optimization manually")
    st.code("""
# When you have 50+ training examples in gepa/data/training/:
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
print(f'Program saved: {path}')
"
""", language="bash")
