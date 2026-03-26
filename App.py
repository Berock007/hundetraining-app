import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- SETUP ---
st.set_page_config(page_title="Pfoten-Planer", layout="centered", page_icon="🐾")

# Initialisierung der Daten (Solange keine Cloud-Anbindung da ist)
if 'trainings' not in st.session_state:
    st.session_state.trainings = {} # Key: "YYYY-MM-DD"
if 'vorlagen' not in st.session_state:
    st.session_state.vorlagen = [{"name": "Leinenführigkeit", "dauer": 15, "material": "Schleppleine"}]

# --- NAVIGATION ---
st.title("🐾 Pfoten-Planer")
menu = st.radio("Ansicht wählen:", ["Wochenplan", "Monatsübersicht", "Vorlagen"], horizontal=True)

# --- FUNKTION: TRAINING-CARD ANZEIGEN ---
def show_training_card(datum_str, tag_name):
    with st.container(border=True):
        # Header des Tages - Immer sichtbar
        col_t, col_s = st.columns([3, 1])
        with col_t:
            st.markdown(f"### {tag_name}")
        
        if datum_str in st.session_state.trainings:
            t = st.session_state.trainings[datum_str]
            # Sofort sichtbare Info
            st.markdown(f"**🐶 {t['title']}** ({t['dauer']} Min.)")
            st.caption(f"Status: {t['status']} | Material: {t['material']}")
            
            # Details zum Ausklappen für Notizen/Bewertung
            with st.expander("Details & Bewertung"):
                u_status = st.checkbox("Erledigt ✅", value=(t['status'] == "✅"), key=f"check_{datum_str}")
                u_rating = st.select_slider("Wie war's?", options=["❌", "😐", "🙂", "🤩"], key=f"rate_{datum_str}")
                u_notes = st.text_area("Notizen", value=t.get('notes', ""), key=f"note_{datum_str}")
                
                if st.button("Speichern", key=f"btn_save_{datum_str}"):
                    st.session_state.trainings[datum_str].update({
                        "status": "✅" if u_status else "⏳",
                        "notes": u_notes,
                        "rating": u_rating
                    })
                    st.rerun()
                if st.button("🗑️ Löschen", key=f"btn_del_{datum_str}"):
                    del st.session_state.trainings[datum_str]
                    st.rerun()
        else:
            st.write("Kein Training geplant.")
            if st.session_state.vorlagen:
                with st.expander("➕ Training planen"):
                    auswahl = st.selectbox("Vorlage", [v['name'] for v in st.session_state.vorlagen], key=f"sel_{datum_str}")
                    if st.button("Hinzufügen", key=f"add_{datum_str}"):
                        v = next(item for item in st.session_state.vorlagen if item['name'] == auswahl)
                        st.session_state.trainings[datum_str] = {
                            "title": v['name'], "dauer": v['dauer'], 
                            "material": v['material'], "status": "⏳", "notes": ""
                        }
                        st.rerun()

# --- LOGIK: ANSICHTEN ---
if menu == "Wochenplan":
    # Wochen-Navigator
    c1, c2, c3 = st.columns([1, 2, 1])
    if 'offset' not in st.session_state: st.session_state.offset = 0
    
    with c1: 
        if st.button("⬅️ Letzte Woche"): st.session_state.offset -= 7
    with c3: 
        if st.button("Nächste Woche ➡️"): st.session_state.offset += 7
    with c2:
        heute = datetime.now() + timedelta(days=st.session_state.offset)
        start_der_woche = heute - timedelta(days=heute.weekday())
        st.markdown(f"<center>KW {start_der_woche.isocalendar()[1]}</center>", unsafe_allow_html=True)

    for i in range(7):
        tag = start_der_woche + timedelta(days=i)
        show_training_card(tag.strftime("%Y-%m-%d"), tag.strftime("%A, %d.%m."))

elif menu == "Monatsübersicht":
    st.subheader("Kalender-Pick")
    gewaehltes_datum = st.date_input("Wähle einen Tag für die Details:", datetime.now())
    show_training_card(gewaehltes_datum.strftime("%Y-%m-%d"), gewaehltes_datum.strftime("%A, %d.%m."))

elif menu == "Vorlagen":
    st.subheader("Deine Übungen")
    # Hier wie gehabt: Vorlagen anzeigen & neue Formulare
    for idx, v in enumerate(st.session_state.vorlagen):
        st.write(f"**{v['name']}** - {v['dauer']} min")
    
    with st.form("Neue Vorlage"):
        n = st.text_input("Name")
        d = st.number_input("Dauer", 5, 60, 15)
        m = st.text_input("Material")
        if st.form_submit_button("Speichern"):
            st.session_state.vorlagen.append({"name": n, "dauer": d, "material": m})
            st.rerun()
            
