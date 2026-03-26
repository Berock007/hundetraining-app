import streamlit as st
from streamlit_calendar import calendar
from datetime import datetime

# --- SETUP ---
st.set_page_config(page_title="Pfoten-Planer", layout="wide", page_icon="🐾")

# Initialisierung der Daten (Session State)
if 'trainings' not in st.session_state:
    st.session_state.trainings = [] 
if 'vorlagen' not in st.session_state:
    st.session_state.vorlagen = [{"name": "Leinenführigkeit", "dauer": 15, "material": "Schleppleine"}]
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = datetime.now().strftime("%Y-%m-%d")

# --- NAVIGATION ---
tab1, tab2 = st.tabs(["📅 Kalender & Planung", "⚙️ Vorlagen"])

# --- TAB 1: KALENDER & DETAILS ---
with tab1:
    # KALENDER-EINSTELLUNGEN
    # Hier aktivieren wir die Umschalt-Buttons für Monat und Woche (Liste)
    cal_options = {
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,listWeek" # Button für Monat und vertikale Woche
        },
        "buttonText": {
            "today": "Heute",
            "month": "Monat",
            "list": "Woche"
        },
        "initialView": "dayGridMonth",
        "selectable": True,
        "locale": "de",
    }
    
    # Der interaktive Kalender
    state = calendar(events=st.session_state.trainings, options=cal_options, key="dog_calendar")

    # LOGIK: Klick-Erkennung für neue & bestehende Einträge
    if state.get("dateClick"):
        st.session_state.selected_date = state["dateClick"]["date"].split("T")[0]
    elif state.get("eventClick"):
        st.session_state.selected_date = state["eventClick"]["event"]["start"].split("T")[0]

    st.divider()
    
    # DETAIL-BEREICH (Erscheint beim Klicken)
    sel_date = st.session_state.selected_date
    date_obj = datetime.strptime(sel_date, "%Y-%m-%d")
    st.markdown(f"### 📍 Fokus: {date_obj.strftime('%A, %d.%m.%Y')}")

    # Suchen, ob für das gewählte Datum schon ein Training existiert
    training_heute = next((t for t in st.session_state.trainings if t["start"] == sel_date), None)

    if training_heute:
        with st.container(border=True):
            st.markdown(f"#### 🐶 Übung: {training_heute['title']}")
            
            # Anzeige der Details untereinander
            st.write(f"**Dauer:** {training_heute['dauer']} Min")
            st.write(f"**Material:** {training_heute['material']}")
            st.write(f"**Status:** {training_heute['status']}")
            
            with st.expander("Bewerten & Notizen", expanded=True):
                u_status = st.checkbox("Training erledigt? ✅", value=(training_heute['status'] == "✅"))
                u_rating = st.select_slider("Wie war die Leistung?", options=["❌", "😐", "🙂", "🤩"], value=training_heute.get('rating', "😐"))
                u_notes = st.text_area("Feedback/Notizen", value=training_heute.get('notes', ""))
                
                col_btn1, col_btn2 = st.columns(2)
                if col_btn1.button("Speichern", use_container_width=True, type="primary"):
                    training_heute.update({
                        "status": "✅" if u_status else "⏳",
                        "rating": u_rating,
                        "notes": u_notes,
                        "color": "#28a745" if u_status else "#ff851b"
                    })
                    st.rerun()
                
                if col_btn2.button("Löschen", use_container_width=True):
                    st.session_state.trainings = [t for t in st.session_state.trainings if t["start"] != sel_date]
                    st.rerun()
    else:
        # Menü zum Eintragen, wenn der Tag leer ist
        st.info("Kein Training geplant. Klicke auf 'Planen', um eine Vorlage hinzuzufügen.")
        if st.session_state.vorlagen:
            with st.form("planung_form"):
                auswahl = st.selectbox("Vorlage wählen", [v['name'] for v in st.session_state.vorlagen])
                if st.form_submit_button("Training für diesen Tag eintragen"):
                    v = next(item for item in st.session_state.vorlagen if item['name'] == auswahl)
                    st.session_state.trainings.append({
                        "title": v['name'],
                        "start": sel_date,
                        "dauer": v['dauer'],
                        "material": v['material'],
                        "status": "⏳",
                        "color": "#ff851b",
                        "notes": "",
                        "rating": "😐"
                    })
                    st.rerun()

# --- TAB 2: VORLAGEN ---
with tab2:
    st.subheader("Deine Übungsvorlagen")
    # Liste der Vorlagen
    for idx, v in enumerate(st.session_state.vorlagen):
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.write(f"**{v['name']}** ({v['dauer']} Min) - *{v['material']}*")
            if c2.button("🗑️", key=f"del_v_{idx}"):
                st.session_state.vorlagen.pop(idx)
                st.rerun()

    # Formular für neue Vorlagen
    with st.expander("➕ Neue Vorlage erstellen"):
        with st.form("neue_vorlage"):
            n = st.text_input("Name der Übung")
            d = st.number_input("Dauer (Min)", 5, 60, 15)
            m = st.text_input("Material")
            if st.form_submit_button("Speichern"):
                if n:
                    st.session_state.vorlagen.append({"name": n, "dauer": d, "material": m})
                    st.rerun()
                    
