import streamlit as st
from streamlit_calendar import calendar
import pandas as pd

# --- SETUP ---
st.set_page_config(page_title="Pfoten-Planer", layout="wide", page_icon="🐾")

# Initialisierung der Daten (Session State)
if 'vorlagen' not in st.session_state:
    st.session_state.vorlagen = [
        {"name": "Leinenführigkeit", "dauer": 15, "material": "Schleppleine, Leckerli"},
        {"name": "Rückruf", "dauer": 10, "material": "Pfeife, Super-Belohnung"}
    ]

if 'trainings' not in st.session_state:
    st.session_state.trainings = []

# --- NAVIGATION ---
tab1, tab2 = st.tabs(["📅 Wochenplan (Liste)", "⚙️ Vorlagen-Verwaltung"])

# --- TAB 1: WOCHENPLAN (UNTEREINANDER) ---
with tab1:
    st.subheader("Trainingswoche")
    
    # Hier nutzen wir 'listWeek' statt 'dayGridMonth'
    # Das stellt die Tage untereinander dar, ideal fürs Handy!
    cal_options = {
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "listWeek,dayGridMonth" # Man kann zwischen Liste und Monat wechseln
        },
        "initialView": "listWeek", # Standardmäßig die Liste untereinander
        "selectable": True,
        "locale": "de", # Deutsche Wochentage
        "buttonText": {"today": "Heute", "month": "Monat", "week": "Woche", "list": "Liste"}
    }
    
    # Kalender Widget
    state = calendar(events=st.session_state.trainings, options=cal_options)

    # Logik für Klick auf Tag oder Event
    # Bei der Listenansicht nutzen wir dateClick für neue Planung
    if state.get("dateClick") or state.get("eventClick"):
        # Datum ermitteln, egal ob auf Termin oder leeren Tag geklickt wurde
        if state.get("eventClick"):
            clicked_date = state["eventClick"]["event"]["start"].split("T")[0]
        else:
            clicked_date = state["dateClick"]["date"].split("T")[0]
            
        st.divider()
        st.markdown(f"### 📍 Details für {clicked_date}")
        
        training_heute = next((t for t in st.session_state.trainings if t["start"] == clicked_date), None)
        
        if training_heute:
            with st.container(border=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Übung:** {training_heute['title']}")
                    st.write(f"**Dauer:** {training_heute.get('dauer', '??')} Min.")
                with col2:
                    st.write(f"**Material:** {training_heute.get('material', 'Keines')}")
                    st.write(f"**Status:** {training_heute['status']}")
                
                st.info(f"**Notizen:** {training_heute.get('notes', 'Keine Notizen.')}")
                
                # Bearbeitung
                with st.expander("Training bearbeiten / Abschließen"):
                    u_status = st.checkbox("Erledigt ✅", value=(training_heute['status'] == "✅"))
                    u_rating = st.select_slider("Bewertung", options=["❌", "😐", "🙂", "🤩"])
                    u_notes = st.text_area("Notiz hinzufügen", value=training_heute.get('notes', ""))
                    
                    if st.button("Speichern"):
                        training_heute['status'] = "✅" if u_status else "⏳"
                        training_heute['rating'] = u_rating
                        training_heute['notes'] = u_notes
                        training_heute['color'] = "#28a745" if u_status else "#ff851b"
                        st.rerun()
                        
                if st.button("Training löschen", type="secondary"):
                    st.session_state.trainings = [t for t in st.session_state.trainings if t["start"] != clicked_date]
                    st.rerun()
        else:
            st.write("Noch nichts geplant.")
            if st.session_state.vorlagen:
                auswahl = st.selectbox("Vorlage wählen", [v['name'] for v in st.session_state.vorlagen])
                if st.button(f"{auswahl} festlegen"):
                    v_daten = next(v for v in st.session_state.vorlagen if v['name'] == auswahl)
                    st.session_state.trainings.append({
                        "title": v_daten['name'],
                        "start": clicked_date,
                        "dauer": v_daten['dauer'],
                        "material": v_daten['material'],
                        "status": "⏳",
                        "color": "#ff851b",
                        "notes": ""
                    })
                    st.rerun()

# --- TAB 2: VORLAGEN-VERWALTUNG (unverändert) ---
with tab2:
    st.subheader("Deine Übungsvorlagen")
    if st.session_state.vorlagen:
        st.dataframe(pd.DataFrame(st.session_state.vorlagen), use_container_width=True)
        # Löschfunktion für Vorlagen
        del_name = st.selectbox("Vorlage löschen?", [v['name'] for v in st.session_state.vorlagen])
        if st.button("Löschen"):
            st.session_state.vorlagen = [v for v in st.session_state.vorlagen if v['name'] != del_name]
            st.rerun()
    
    st.divider()
    st.markdown("### Neue Vorlage erstellen")
    n = st.text_input("Name")
    d = st.number_input("Dauer (Min)", 5, 60, 15)
    m = st.text_input("Material")
    if st.button("Speichern"):
        if n:
            st.session_state.vorlagen.append({"name": n, "dauer": d, "material": m})
            st.rerun()
            
