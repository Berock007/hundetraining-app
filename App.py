import streamlit as st
from streamlit_calendar import calendar
import datetime

# Seiten-Setup
st.set_page_config(page_title="Hunde-Trainer Pro", layout="wide", page_icon="🐾")

# --- STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .main { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🐾 Unser Pfoten-Planer")

# --- INITIALISIERUNG (Session State) ---
if 'trainings' not in st.session_state:
    # Beispiel-Daten (später kommen diese aus der Cloud)
    st.session_state.trainings = [
        {"title": "Leinenführigkeit", "start": "2026-03-27", "status": "✅", "notes": "Super Fokus!"},
        {"title": "Rückruf", "start": "2026-03-28", "status": "⏳", "notes": "Viel Ablenkung."}
    ]

# --- SIDEBAR: VORLAGEN ---
with st.sidebar:
    st.header("📋 Vorlagen")
    vorlage_name = st.text_input("Name der Übung")
    vorlage_dauer = st.number_input("Dauer (Min)", 5, 60, 15)
    vorlage_sachen = st.text_area("Was wird benötigt?")
    if st.button("Als Vorlage speichern"):
        st.success("Vorlage erstellt!")

# --- HAUPTTEIL: KALENDER ---
st.subheader("📅 Trainings-Kalender")
st.info("Tipp: Klicke auf einen Tag, um Details zu sehen oder zu planen!")

calendar_options = {
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "dayGridMonth,dayGridWeek",
    },
    "initialView": "dayGridMonth",
    "selectable": True,
}

# Kalender anzeigen
state = calendar(events=st.session_state.trainings, options=calendar_options)

# --- LOGIK: WAS PASSIERT BEIM KLICK? ---
if state.get("dateClick"):
    clicked_date = state["dateClick"]["date"].split("T")[0]
    
    st.divider()
    st.subheader(f"📍 Details für den {clicked_date}")
    
    # Suchen, ob an diesem Tag schon ein Training existiert
    training_heute = next((t for t in st.session_state.trainings if t["start"] == clicked_date), None)
    
    if training_heute:
        st.write(f"**Geplante Übung:** {training_heute['title']}")
        st.write(f"**Status:** {training_heute['status']}")
        
        col1, col2 = st.columns(2)
        with col1:
            neuer_status = st.checkbox("Als erledigt markieren", value=(training_heute['status'] == "✅"))
        with col2:
            bewertung = st.select_slider("Bewertung", options=["❌", "😐", "🙂", "🤩"])
            
        neue_notiz = st.text_area("Notizen editieren", value=training_heute.get("notes", ""))
        
        if st.button("Änderungen speichern"):
            training_heute['status'] = "✅" if neuer_status else "⏳"
            training_heute['notes'] = neue_notiz
            st.rerun()
            
    else:
        st.write("Noch kein Training geplant.")
        neue_uebung = st.selectbox("Vorlage wählen", ["Leinenführigkeit", "Rückruf", "Sitz/Platz", "Apportieren"])
        if st.button(f"Training für {clicked_date} eintragen"):
            st.session_state.trainings.append({
                "title": neue_uebung,
                "start": clicked_date,
                "status": "⏳",
                "notes": ""
            })
            st.success("Eingetragen!")
            st.rerun()

