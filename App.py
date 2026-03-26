import streamlit as st
from streamlit_calendar import calendar
import datetime

# --- SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Hunde-Trainer Pro", layout="wide")
st.title("🐾 Unser Hunde-Trainingsplan")

# --- 1. VORLAGEN-VERWALTUNG ---
with st.sidebar:
    st.header("📋 Übungs-Vorlagen")
    with st.expander("Neue Vorlage erstellen"):
        v_name = st.text_input("Name der Übung")
        v_dauer = st.number_input("Dauer (Min)", min_value=5, step=5)
        v_sachen = st.text_area("Benötigte Sachen")
        if st.button("Vorlage speichern"):
            # Hier käme die Logik zum Speichern in die Cloud
            st.success(f"'{v_name}' wurde als Vorlage gesichert!")

# --- 2. KALENDER-ANSICHT (Google Style) ---
st.subheader("📅 Trainings-Kalender")

# Beispiel-Daten für den Kalender
calendar_events = [
    {
        "title": "Leinenführigkeit (15 min)",
        "start": "2026-03-27T10:00:00",
        "end": "2026-03-27T10:15:00",
        "color": "#3D9970",  # Grün für erledigt
    },
    {
        "title": "Rückruf-Training",
        "start": "2026-03-28T14:00:00",
        "end": "2026-03-28T14:20:00",
        "color": "#FF851B",  # Orange für geplant
    }
]

calendar_options = {
    "editable": "true",
    "selectable": "true",
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek",
    },
    "initialView": "dayGridMonth",
}

# Das Kalender-Widget anzeigen
state = calendar(events=calendar_events, options=calendar_options)

# --- 3. TRAINING LOGGEN & BEWERTEN ---
st.divider()
st.subheader("✍️ Training auswerten")

col1, col2 = st.columns(2)
with col1:
    check_done = st.checkbox("Training erledigt?")
    bewertung = st.select_slider("Wie lief es?", options=["❌", "🤨", "😐", "🙂", "✅"])
with col2:
    notiz = st.text_area("Notizen zum Training", placeholder="Besonderheiten heute...")

if st.button("Cloud-Update senden"):
    st.balloons()
    st.info("Daten werden mit deiner Frau synchronisiert...")
  
