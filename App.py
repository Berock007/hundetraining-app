import streamlit as st
from streamlit_calendar import calendar
from datetime import datetime

# --- SETUP ---
st.set_page_config(page_title="Pfoten-Planer", layout="wide", page_icon="🐾")

# Initialisierung der Daten (Session State)
if 'trainings' not in st.session_state:
    st.session_state.trainings = [] # Liste für den Kalender
if 'vorlagen' not in st.session_state:
    st.session_state.vorlagen = [{"name": "Leinenführigkeit", "dauer": 15, "material": "Schleppleine"}]
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = datetime.now().strftime("%Y-%m-%d")

# --- NAVIGATION ---
tab1, tab2 = st.tabs(["📅 Kalender & Planung", "⚙️ Vorlagen"])

# --- TAB 1: KALENDER & DETAILS ---
with tab1:
    st.subheader("Trainingsübersicht")
    
    # Kalender-Konfiguration (Monatsansicht wie Google)
    cal_options = {
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth"},
        "initialView": "dayGridMonth",
        "selectable": True,
        "locale": "de",
    }
    
    # Der Kalender oben
    state = calendar(events=st.session_state.trainings, options=cal_options, key="main_cal")

    # Logik: Welcher Tag wurde angeklickt?
    if state.get("dateClick"):
        st.session_state.selected_date = state["dateClick"]["date"].split("T")[0]
    elif state.get("eventClick"):
        st.session_state.selected_date = state["eventClick"]["event"]["start"].split("T")[0]

    st.divider()
    
    # DETAIL-ANSICHT UNTER DEM KALENDER (Vertikal)
    sel_date = st.session_state.selected_date
    formatted_date = datetime.strptime(sel_date, "%Y-%m-%d").strftime("%A, %d.%m.%Y")
    st.markdown(f"### 📍 Details für {formatted_date}")

    # Suchen nach Training für dieses Datum
    training_heute = next((t for t in st.session_state.trainings if t["start"] == sel_date), None)

    if training_heute:
        with st.container(border=True):
            # Sofort sichtbare Infos
            st.markdown(f"#### 🐶 {training_heute['title']}")
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Dauer", f"{training_heute['dauer']} Min")
            col_b.metric("Status", training_heute['status'])
            col_c.write(f"**Material:**\n{training_heute['material']}")
            
            # Bewertung & Notizen (Untereinander)
            st.markdown("---")
            u_status = st.checkbox("Als erledigt markieren ✅", value=(training_heute['status'] == "✅"), key="edit_status")
            u_rating = st.select_slider("Wie lief das Training?", options=["❌", "😐", "🙂", "🤩"], value=training_heute.get('rating', "😐"), key="edit_rating")
            u_notes = st.text_area("Notizen zum Training", value=training_heute.get('notes', ""), placeholder="Was hat gut geklappt?", key="edit_notes")
            
            c1, c2 = st.columns(2)
            if c1.button("Änderungen speichern", use_container_width=True, type="primary"):
                training_heute['status'] = "✅" if u_status else "⏳"
                training_heute['rating'] = u_rating
                training_heute['notes'] = u_notes
                training_heute['color'] = "#28a745" if u_status else "#ff851b"
                st.rerun()
            
            if c2.button("Training löschen", use_container_width=True):
                st.session_state.trainings = [t for t in st.session_state.trainings if t["start"] != sel_date]
                st.rerun()
    else:
        st.info("Für diesen Tag ist noch kein Training geplant.")
        if st.session_state.vorlagen:
            with st.expander("➕ Neues Training aus Vorlage planen"):
                auswahl = st.selectbox("Vorlage wählen", [v['name'] for v in st.session_state.vorlagen])
                if st.button("In Kalender eintragen"):
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
        else:
            st.warning("Erstelle im Tab 'Vorlagen' zuerst eine Übung.")

# --- TAB 2: VORLAGEN ---
with tab2:
    st.subheader("Übungsvorlagen verwalten")
    
    # Vorlagen anzeigen
    for idx, v in enumerate(st.session_state.vorlagen):
        with st.container(border=True):
            c_left, c_right = st.columns([4, 1])
            c_left.markdown(f"**{v['name']}** ({v['dauer']} Min)  \n*Material: {v['material']}*")
            if c_right.button("🗑️", key=f"del_v_{idx}"):
                st.session_state.vorlagen.pop(idx)
                st.rerun()

    st.divider()
    st.markdown("### 🆕 Neue Vorlage erstellen")
    with st.form("vorlage_form", clear_on_submit=True):
        n = st.text_input("Name der Übung")
        d = st.number_input("Dauer (Minuten)", 5, 120, 15)
        m = st.text_area("Benötigtes Material")
        if st.form_submit_button("Vorlage speichern"):
            if n:
                st.session_state.vorlagen.append({"name": n, "dauer": d, "material": m})
                st.rerun()
                
