
import os, time, requests, pandas as pd
import streamlit as st

try:
    import plotly.express as px
    HAS_PLOTLY=True
except Exception:
    HAS_PLOTLY=False

try:
    from streamlit_autorefresh import st_autorefresh
    HAS_AUTOREFRESH=True
except Exception:
    HAS_AUTOREFRESH=False

API = os.getenv("API_BASE","http://api:8000")

st.set_page_config(page_title="Agentic Devline", layout="wide")
st.title("Agentic ontwikkelstraat (AutoGen demo)")

# Sidebar controls
manual = st.sidebar.text_input("Run ID handmatig (bestaande run)", "")
if manual:
    st.session_state["run_id"] = manual
    st.sidebar.success(f"Run ingesteld: {manual}")

with st.sidebar.expander("Nieuwe run starten"):
    with st.form("new_run"):
        project = st.text_input("Projectnaam", "Demo App")
        reqs = st.text_area("Requirements (functioneel)", height=120, value="Als gebruiker wil ik ... zodat ...")
        submit = st.form_submit_button("Start run")
        if submit:
            r = requests.post(f"{API}/runs", json={"project_name": project, "requirements": reqs}, timeout=10)
            r.raise_for_status()
            st.session_state["run_id"] = r.json()["run_id"]
            st.sidebar.success(f"Run gestart: {st.session_state['run_id']}")

run_id = st.session_state.get("run_id")

# Helpers
def fetch_events(run_id: str):
    try:
        ev = requests.get(f"{API}/runs/{run_id}/events", timeout=6).json()
        import pandas as pd
        if not ev:
            return pd.DataFrame(columns=["ts","agent","phase","content"])
        df = pd.DataFrame(ev)
        df["ts"] = pd.to_datetime(df["ts"])
        return df.sort_values("ts")[ ["ts","agent","phase","content"] ]
    except Exception as e:
        st.warning(f"Events ophalen mislukt: {e}")
        import pandas as pd
        return pd.DataFrame(columns=["ts","agent","phase","content"])

def fetch_report(run_id: str) -> str:
    try:
        return requests.get(f"{API}/runs/{run_id}/report", timeout=6).text
    except Exception as e:
        return f"Kon rapport niet ophalen: {e}"

if not run_id:
    st.warning("Nog geen actieve run. Start er één in de sidebar of plak een run_id.")
    st.stop()

st.subheader(f"Run: {run_id}")

tab_live, tab_timeline, tab_report = st.tabs(["🔴 Live log", "📈 Timeline", "🧪 Test rapport"])

with tab_live:
    if HAS_AUTOREFRESH:
        st_autorefresh(interval=1000, limit=120, key="live_autorefresh")
    df = fetch_events(run_id)
    if df.empty:
        st.info("Nog geen events voor deze run.")
    else:
        latest = df.groupby("agent")["phase"].last()
        cols = st.columns(max(len(latest),1))
        for i,(agent,phase) in enumerate(latest.items()):
            color = {"start":"orange","input":"orange","output":"blue","done":"green","error":"red"}.get(phase,"gray")
            cols[i%len(cols)].markdown(f"**{agent}**: <span style='color:{color}'>{phase}</span>", unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, height=460)

with tab_timeline:
    df = fetch_events(run_id)
    if df.empty:
        st.info("Nog geen events voor timeline.")
    elif not HAS_PLOTLY:
        st.info("Plotly ontbreekt (timeline uit).")
    else:
        import plotly.express as px
        starts = df[df["phase"]=="start"].groupby("agent")["ts"].min().rename("start")
        dones  = df[df["phase"]=="done"].groupby("agent")["ts"].max().rename("end")
        tl = (starts.to_frame().join(dones, how='inner')).reset_index()
        if tl.empty:
            st.info("Nog geen volledige agent-rondes (start/done).")
        else:
            fig = px.timeline(tl, x_start="start", x_end="end", y="agent", color="agent")
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)

with tab_report:
    txt = fetch_report(run_id)
    st.text_area("Test rapport", txt, height=420)
