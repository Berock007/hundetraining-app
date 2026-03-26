import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar as py_cal

# --- SETUP ---
st.set_page_config(page_title="Pfoten-Planer Pro", layout="centered", page_icon="🐾")

# Initialisierung der Daten
if 'trainings' not in st.session_state:
    st.session_state.trainings = {} # Wir nutzen ein Dict: {"YYYY-MM-DD": {Daten}}
if 'vorlagen' not in st.session_state:
    st.session_state.vorlagen = [{"name": "Leinenführigkeit", "dauer": 15, "material": "Schleppleine"}]
if 'view_date' not in st.session_state:
    st.session_state.view_date = datetime.now().date()
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = str(datetime.now().date())

# --- HELFER: MONATS-NAVIGATOR ---
st.title("🐾 Unser Pfoten-Planer")
tab1, tab2, tab3 = st.tabs(["📅 Planung", "⚙️ Vorlagen", "📊 Statistik"])

with tab1:
    # Monat umschalten
    col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
    with col_nav1:
        if st.button("⬅️"): st.session_state.view_date -= timedelta(days=30)
    with col_nav3:
        if st.button("➡️"): st.session_state.view_date += timedelta(days=30)
    with col_nav2:
        curr_month = st.session_state.view_date
        st.markdown(f"<h3 style='text-align: center;'>{curr_month.strftime('%B %Y')}</h3>", unsafe_allow_html=True)

    # --- DER EIGENE KALENDER (GRID) ---
    # Wochentage Header
    days_header = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    cols = st.columns(7)
    for i, day in enumerate(days_header):
        cols[i].markdown(f"**{day}**")

    # Kalender-Tage berechnen
    cal = py_cal.Calendar(firstweekday=0)
    month_days = cal.monthdatescalendar(curr_month.year, curr_month.month)

    for week in month_days:
        cols = st.columns(7)
        for i, day in enumerate(week):
            date_str = str(day)
            
            # Farbe bestimmen
            btn_label = f"{day.day}"
            btn_type = "secondary"
            
            if date_str in st.session_state.trainings:
                t = st.session_state.trainings[date_str]
                btn_label = f"{day.day}\n🐶"
                btn_type = "primary" if t['status'] == "✅" else "secondary" # Blau/Grün-Logic
            
            # Der Button für den Tag
            if cols[i].button(btn_label, key=f"btn_{date_str}", use_container_width=True):
                st.session_state.selected_date = date_str

    st.divider()
    
    # --- DETAIL-ANSICHT (UNTER DEM KALENDER) ---
    sel_date = st.session_state.selected_date
    d_obj = datetime.strptime(sel_date, "%Y-%m-%d")
    st.subheader(f"📍 Details: {d_obj.strftime('%d.%m.%Y')}")

    if sel_date in st.session_state.trainings:
        t = st.session_state.trainings[sel_date]
        with st.container(border=True):
            st.markdown(f"#### {t['title']} ({t['dauer']} Min)")
            st.write(f"**Material:** {t['material']}")
            
            u_status = st.checkbox("Erledigt ✅", value=(t['status'] == "✅"), key=f"chk_{sel_date}")
            u_rating = st.select_slider("Erfolg:", options=["❌", "😐", "🙂", "🤩"], value=t.get('rating', "😐"), key=f"rate_{sel_date}")
            u_notes = st.text_area("Notizen:", value=t.get('notes', ""), key=f"note_{sel_date}")
            
            c1, c2 = st.columns(2)
            if c1.button("Speichern", type="primary", use_container_width=True):
                st.session_state.trainings[sel_date].update({
                    "status": "✅" if u_status else "⏳",
                    "rating": u_rating, "notes": u_notes
                })
                st.rerun()
            if c2.button("Löschen", use_container_width=True):
                del st.session_state.trainings[sel_date]
                st.rerun()
    else:
        st.info("Noch nichts geplant.")
        with st.expander("➕ Neues Training planen"):
            auswahl = st.selectbox("Vorlage:", [v['name'] for v in st.session_state.vorlagen])
            if st.button("Eintragen"):
                v = next(i for i in st.session_state.vorlagen if i['name'] == auswahl)
                st.session_state.trainings[sel_date] = {
                    "title": v['name'], "dauer": v['dauer'], "material": v['material'],
                    "status": "⏳", "notes": "", "rating": "😐"
                }
                st.rerun()

# --- TAB 2 & 3 bleiben logisch gleich (Code gekürzt für Übersicht) ---
# ... (Hier kommen die Vorlagen- und Statistik-Tabs wie zuvor)


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
                
