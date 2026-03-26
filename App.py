import streamlit as st
from streamlit_calendar import calendar
import pandas as pd

# --- SETUP ---
st.set_page_config(page_title="Pfoten-Planer", layout="wide", page_icon="🐾")

# Initialisierung der Daten (Solange wir noch keine DB haben, nutzen wir Session State)
if 'vorlagen' not in st.session_state:
    st.session_state.vorlagen = [
        {"name": "Leinenführigkeit", "dauer": 15, "material": "Schleppleine, Leckerli"},
        {"name": "Rückruf", "dauer": 10, "material": "Pfeife, Super-Belohnung"}
    ]

if 'trainings' not in st.session_state:
    st.session_state.trainings = []

# --- NAVIGATION ---
tab1, tab2 = st.tabs(["📅 Kalender & Training", "⚙️ Vorlagen-Verwaltung"])

# --- TAB 1: KALENDER & DETAILS ---
with tab1:
    st.subheader("Dein Trainingsplan")
    
    cal_options = {
        "headerToolbar": {"left": "today prev,next", "center": "title", "right": "dayGridMonth,dayGridWeek"},
        "selectable": True,
    }
    
    # Kalender Widget
    state = calendar(events=st.session_state.trainings, options=cal_options)

    # Wenn ein Tag angeklickt wird
    if state.get("dateClick"):
        clicked_date = state["dateClick"]["date"].split("T")[0]
        st.divider()
        st.markdown(f"### 📍 Details für den {clicked_date}")
        
        # Suche Training für diesen Tag
        training_heute = next((t for t in st.session_state.trainings if t["start"] == clicked_date), None)
        
        if training_heute:
            # AUSFÜHRLICHE ANZEIGE
            with st.container(border=True):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Übung:** {training_heute['title']}")
                    st.markdown(f"**Dauer:** {training_heute.get('dauer', '??')} Min.")
                    st.markdown(f"**Material:** {training_heute.get('material', 'Keines')}")
                with c2:
                    st.markdown(f"**Status:** {training_heute['status']}")
                    st.markdown(f"**Bewertung:** {training_heute.get('rating', 'Noch keine')}")
                
                st.info(f"**Notizen:** {training_heute.get('notes', 'Keine Notizen vorhanden.')}")
                
                # Bearbeitungs-Modus innerhalb des Klicks
                with st.expander("Training bearbeiten / Abschließen"):
                    u_status = st.checkbox("Erledigt ✅", value=(training_heute['status'] == "✅"))
                    u_rating = st.select_slider("Wie lief es?", options=["❌", "😐", "🙂", "🤩"])
                    u_notes = st.text_area("Notizen hinzufügen", value=training_heute.get('notes', ""))
                    
                    if st.button("Speichern"):
                        training_heute['status'] = "✅" if u_status else "⏳"
                        training_heute['rating'] = u_rating
                        training_heute['notes'] = u_notes
                        training_heute['color'] = "#28a745" if u_status else "#ff851b" # Grün wenn fertig
                        st.rerun()
        else:
            st.write("Kein Training geplant.")
            if st.session_state.vorlagen:
                auswahl = st.selectbox("Vorlage wählen", [v['name'] for v in st.session_state.vorlagen])
                if st.button(f"{auswahl} für heute planen"):
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
            else:
                st.warning("Bitte erstelle zuerst eine Vorlage im Menü 'Vorlagen-Verwaltung'.")

# --- TAB 2: VORLAGEN-VERWALTUNG ---
with tab2:
    st.subheader("Deine Übungsvorlagen")
    
    # Vorhandene Vorlagen anzeigen/löschen
    if st.session_state.vorlagen:
        df_vorlagen = pd.DataFrame(st.session_state.vorlagen)
        st.table(df_vorlagen)
        
        loesch_auswahl = st.selectbox("Vorlage zum Löschen auswählen", [v['name'] for v in st.session_state.vorlagen])
        if st.button("Vorlage entfernen"):
            st.session_state.vorlagen = [v for v in st.session_state.vorlagen if v['name'] != loesch_auswahl]
            st.rerun()
    
    st.divider()
    st.markdown("### Neue Vorlage erstellen")
    new_n = st.text_input("Name der Übung (z.B. Impulskontrolle)")
    new_d = st.number_input("Dauer in Minuten", 1, 120, 15)
    new_m = st.text_input("Benötigtes Material")
    
    if st.button("Vorlage hinzufügen"):
        if new_n:
            st.session_state.vorlagen.append({"name": new_n, "dauer": new_d, "material": new_m})
            st.success(f"Vorlage '{new_n}' wurde erstellt!")
            st.rerun()
            
