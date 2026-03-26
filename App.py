import streamlit as st
from streamlit_calendar import calendar
from datetime import datetime
import pandas as pd

# --- SETUP ---
st.set_page_config(page_title="Pfoten-Planer Pro", layout="wide", page_icon="🐾")

# Initialisierung der Daten (Wird bei Cloud-Anbindung durch Datenbank-Abfrage ersetzt)
if 'trainings' not in st.session_state:
    st.session_state.trainings = [] 
if 'vorlagen' not in st.session_state:
    st.session_state.vorlagen = [{"name": "Leinenführigkeit", "dauer": 15, "material": "Schleppleine"}]
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = datetime.now().strftime("%Y-%m-%d")

# Hilfswerkzeuge für Bewertungen
smiley_map = {"❌": 1, "😐": 2, "🙂": 3, "🤩": 4}
reverse_smiley_map = {1: "❌", 2: "😐", 3: "🙂", 4: "🤩"}

# --- NAVIGATION ---
tab1, tab2, tab3 = st.tabs(["📅 Kalender & Planung", "⚙️ Vorlagen", "📊 Statistik"])

# --- TAB 1: KALENDER (UNVERÄNDERT) ---
with tab1:
    cal_options = {
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,listWeek"},
        "initialView": "dayGridMonth",
        "selectable": True,
        "locale": "de",
        "firstDay": 1,
    }
    state = calendar(events=st.session_state.trainings, options=cal_options, key="dog_calendar")
    # --- ABSOLUT SICHERE DATUMS-LOGIK ---
    if state.get("dateClick"):
        # Wir nehmen den String, trennen ihn am "T" und nehmen nur den ersten Teil (YYYY-MM-DD)
        raw_date = state["dateClick"]["date"]
        if "T" in raw_date:
            st.session_state.selected_date = raw_date.split("T")[0]
        else:
            st.session_state.selected_date = raw_date
            
    elif state.get("eventClick"):
        raw_event_date = state["eventClick"]["event"]["start"]
        if "T" in raw_event_date:
            st.session_state.selected_date = raw_event_date.split("T")[0]
        else:
            st.session_state.selected_date = raw_event_date

    # Zur Sicherheit: Falls das Datum dennoch falsch formatiert ankommt, 
    # erzwingen wir hier nochmal das richtige Format
    try:
        temp_date = pd.to_datetime(st.session_state.selected_date).date()
        st.session_state.selected_date = str(temp_date)
    except:
        pass
        

    st.divider()
    sel_date = st.session_state.selected_date
    date_obj = datetime.strptime(sel_date, "%Y-%m-%d")
    st.markdown(f"### 📍 Fokus: {date_obj.strftime('%A, %d.%m.%Y')}")

    training_heute = next((t for t in st.session_state.trainings if t["start"] == sel_date), None)

    if training_heute:
        with st.container(border=True):
            st.markdown(f"#### 🐶 Übung: {training_heute['title']}")
            st.write(f"**Dauer:** {training_heute['dauer']} Min | **Material:** {training_heute['material']}")
            with st.expander("Bewerten & Notizen", expanded=True):
                u_status = st.checkbox("Training erledigt? ✅", value=(training_heute['status'] == "✅"))
                u_rating = st.select_slider("Wie war's?", options=["❌", "😐", "🙂", "🤩"], value=training_heute.get('rating', "😐"))
                u_notes = st.text_area("Notizen", value=training_heute.get('notes', ""))
                c1, c2 = st.columns(2)
                if c1.button("Speichern", use_container_width=True, type="primary"):
                    training_heute.update({"status": "✅" if u_status else "⏳", "rating": u_rating, "notes": u_notes, "color": "#28a745" if u_status else "#ff851b"})
                    st.rerun()
                if c2.button("Löschen", use_container_width=True):
                    st.session_state.trainings = [t for t in st.session_state.trainings if t["start"] != sel_date]
                    st.rerun()
    else:
        st.info("Noch kein Training geplant.")
        with st.form("planung_form"):
            auswahl = st.selectbox("Vorlage wählen", [v['name'] for v in st.session_state.vorlagen])
            if st.form_submit_button("Training eintragen"):
                v = next(item for item in st.session_state.vorlagen if item['name'] == auswahl)
                st.session_state.trainings.append({"title": v['name'], "start": sel_date, "dauer": v['dauer'], "material": v['material'], "status": "⏳", "color": "#ff851b", "notes": "", "rating": "😐"})
                st.rerun()

# --- TAB 2: VORLAGEN (UNVERÄNDERT) ---
with tab2:
    st.subheader("Übungsvorlagen")
    for idx, v in enumerate(st.session_state.vorlagen):
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.write(f"**{v['name']}** ({v['dauer']} Min)")
            if c2.button("🗑️", key=f"del_v_{idx}"):
                st.session_state.vorlagen.pop(idx)
                st.rerun()
    with st.expander("➕ Neue Vorlage"):
        with st.form("neue_vorlage"):
            n = st.text_input("Name")
            d = st.number_input("Dauer", 5, 60, 15)
            m = st.text_input("Material")
            if st.form_submit_button("Speichern"):
                if n: st.session_state.vorlagen.append({"name": n, "dauer": d, "material": m})
                st.rerun()

# --- TAB 3: STATISTIK (NEU MIT FILTER) ---
with tab3:
    st.subheader("📊 Trainings-Statistiken")
    
    if not st.session_state.trainings:
        st.info("Noch keine Daten verfügbar.")
    else:
        # Filter-Optionen
        zeitraum = st.radio("Zeitraum wählen:", ["Gesamtzeit", "Aktueller Monat"], horizontal=True)
        
        df = pd.DataFrame(st.session_state.trainings)
        df['start'] = pd.to_datetime(df['start'])
        
        if zeitraum == "Aktueller Monat":
            jetzt = datetime.now()
            df = df[(df['start'].dt.month == jetzt.month) & (df['start'].dt.year == jetzt.year)]
            st.caption(f"Anzeige für: {jetzt.strftime('%B %Y')}")

        if df.empty:
            st.warning("Keine Trainings im gewählten Zeitraum gefunden.")
        else:
            # Metriken
            erledigt = len(df[df['status'] == "✅"])
            df['rating_num'] = df['rating'].map(smiley_map)
            avg_val = df[df['status'] == "✅"]['rating_num'].mean()
            
            m1, m2 = st.columns(2)
            m1.metric("Absolvierte Übungen", erledigt)
            if not pd.isna(avg_val):
                m2.metric("Schnitt-Erfolg", reverse_smiley_map[round(avg_val)])

            st.divider()
            
            # Tabelle nach Übung
            stats = df[df['status'] == "✅"].groupby('title').agg(
                Anzahl=('title', 'count'),
                Erfolg=('rating_num', 'mean')
            ).reset_index()
            
            if not stats.empty:
                stats['Erfolg'] = stats['Erfolg'].apply(lambda x: reverse_smiley_map[round(x)])
                st.markdown("**Erfolg pro Übung:**")
                st.table(stats)
            else:
                st.write("Schließe Trainings ab, um Details zu sehen!")
                
