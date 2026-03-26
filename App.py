import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- SETUP ---
st.set_page_config(page_title="Pfoten-Planer", layout="centered", page_icon="🐾")

# Initialisierung der Daten
if 'vorlagen' not in st.session_state:
    st.session_state.vorlagen = [
        {"name": "Leinenführigkeit", "dauer": 15, "material": "Schleppleine"},
        {"name": "Rückruf", "dauer": 10, "material": "Pfeife"}
    ]

if 'trainings' not in st.session_state:
    st.session_state.trainings = {} # Wir nutzen ein Dictionary mit Datum als Key

# --- NAVIGATION ---
tab1, tab2 = st.tabs(["📅 Wochenplan", "⚙️ Vorlagen"])

# --- TAB 1: WOCHENPLAN (TAGE UNTEREINANDER) ---
with tab1:
    st.subheader("Deine Trainingswoche")
    
    # Aktuelle Woche berechnen
    heute = datetime.now()
    start_der_woche = heute - timedelta(days=heute.weekday())
    
    for i in range(7):
        tag = start_der_woche + timedelta(days=i)
        datum_str = tag.strftime("%Y-%m-%d")
        tag_name = tag.strftime("%A, %d.%m.") # z.B. Montag, 23.03.
        
        # Jeder Tag bekommt einen eigenen Bereich (Expander)
        with st.expander(f"📅 {tag_name}", expanded=(datum_str == heute.strftime("%Y-%m-%d"))):
            
            if datum_str in st.session_state.trainings:
                t = st.session_state.trainings[datum_str]
                st.markdown(f"**Übung:** {t['title']} ({t['dauer']} Min.)")
                st.markdown(f"**Material:** {t['material']}")
                
                c1, c2 = st.columns(2)
                with c1:
                    status = st.selectbox("Status", ["⏳ Geplant", "✅ Erledigt"], 
                                         index=0 if t['status'] == "⏳" else 1, key=f"stat_{datum_str}")
                with c2:
                    bewertung = st.select_slider("Bewertung", options=["❌", "😐", "🙂", "🤩"], key=f"rate_{datum_str}")
                
                notiz = st.text_area("Notiz", value=t.get('notes', ""), key=f"note_{datum_str}")
                
                if st.button("Speichern", key=f"save_{datum_str}"):
                    st.session_state.trainings[datum_str].update({
                        "status": "✅" if "Erledigt" in status else "⏳",
                        "notes": notiz,
                        "rating": bewertung
                    })
                    st.success("Gespeichert!")
                
                if st.button("🗑️ Training löschen", key=f"del_{datum_str}"):
                    del st.session_state.trainings[datum_str]
                    st.rerun()
            
            else:
                st.info("Kein Training geplant.")
                if st.session_state.vorlagen:
                    auswahl = st.selectbox("Vorlage wählen", [v['name'] for v in st.session_state.vorlagen], key=f"sel_{datum_str}")
                    if st.button(f"Planen für {tag.strftime('%d.%m.')}", key=f"btn_{datum_str}"):
                        v_daten = next(v for v in st.session_state.vorlagen if v['name'] == auswahl)
                        st.session_state.trainings[datum_str] = {
                            "title": v_daten['name'],
                            "dauer": v_daten['dauer'],
                            "material": v_daten['material'],
                            "status": "⏳",
                            "notes": ""
                        }
                        st.rerun()

# --- TAB 2: VORLAGEN (BEARBEITEN & HINZUFÜGEN) ---
with tab2:
    st.subheader("Übungsvorlagen verwalten")
    
    for idx, v in enumerate(st.session_state.vorlagen):
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{v['name']}** ({v['dauer']} Min)")
                st.caption(f"Material: {v['material']}")
            with col2:
                if st.button("Löschen", key=f"del_v_{idx}"):
                    st.session_state.vorlagen.pop(idx)
                    st.rerun()

    st.divider()
    st.markdown("### 🆕 Neue Vorlage erstellen")
    n = st.text_input("Name der Übung")
    d = st.number_input("Dauer (Min)", 5, 60, 15)
    m = st.text_input("Material")
    if st.button("Vorlage hinzufügen"):
        if n:
            st.session_state.vorlagen.append({"name": n, "dauer": d, "material": m})
            st.rerun()
            
