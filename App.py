import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar as py_cal

# --- SETUP ---
st.set_page_config(page_title="Pfoten-Planer Pro", layout="centered", page_icon="🐾")

# EXTREMES HANDY-CSS: Erwirkt, dass 7 Spalten nebeneinander passen
st.markdown("""
    <style>
    /* Spaltenabstände minimieren */
    [data-testid="stHorizontalBlock"] {
        gap: 2px !important;
    }
    /* Buttons schmaler und Text kleiner für Handy */
    .stButton button {
        width: 100% !important;
        padding: 0px !important;
        height: 45px !important;
        font-size: 11px !important;
        line-height: 1.2 !important;
    }
    /* Padding der Seite verringern */
    .block-container {
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialisierung
if 'trainings' not in st.session_state:
    st.session_state.trainings = {} 
if 'vorlagen' not in st.session_state:
    st.session_state.vorlagen = [{"name": "Leinenführigkeit", "dauer": 15, "material": "Schleppleine"}]
if 'view_date' not in st.session_state:
    st.session_state.view_date = datetime.now().date()
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = str(datetime.now().date())

# Hilfswerkzeuge
smiley_map = {"❌": 1, "😐": 2, "🙂": 3, "🤩": 4}
reverse_smiley_map = {1: "❌", 2: "😐", 3: "🙂", 4: "🤩"}

tab1, tab2, tab3 = st.tabs(["📅 Planung", "⚙️ Vorlagen", "📊 Statistik"])

# --- TAB 1: PLANUNG ---
with tab1:
    c_nav1, c_nav2, c_nav3 = st.columns([1, 3, 1])
    with c_nav1:
        if st.button("⬅️"): st.session_state.view_date -= timedelta(days=30)
    with c_nav3:
        if st.button("➡️"): st.session_state.view_date += timedelta(days=30)
    with c_nav2:
        curr_month = st.session_state.view_date
        st.markdown(f"<p style='text-align: center; font-weight: bold; margin:0;'>{curr_month.strftime('%B %Y')}</p>", unsafe_allow_html=True)

    # Kalender Header
    days_header = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    cols_h = st.columns(7)
    for i, day in enumerate(days_header):
        cols_h[i].markdown(f"<p style='text-align:center; font-size:10px; margin:0;'>{day}</p>", unsafe_allow_html=True)

    cal = py_cal.Calendar(firstweekday=0)
    month_days = cal.monthdatescalendar(curr_month.year, curr_month.month)

    for week in month_days:
        cols = st.columns(7)
        for i, day in enumerate(week):
            date_str = str(day)
            
            # Farbe & Label
            label = f"{day.day}"
            if date_str in st.session_state.trainings:
                t_item = st.session_state.trainings[date_str]
                label = f"{day.day}\n🐾" if t_item['status'] == "⏳" else f"{day.day}\n✅"
            
            # Graue Buttons für Tage außerhalb des Monats
            if day.month != curr_month.month:
                cols[i].button(label, key=f"d_{date_str}", disabled=True, use_container_width=True)
            else:
                if cols[i].button(label, key=f"d_{date_str}", use_container_width=True):
                    st.session_state.selected_date = date_str

    st.divider()
    
    # Detail-Ansicht
    sel_date = st.session_state.selected_date
    d_obj = datetime.strptime(sel_date, "%Y-%m-%d")
    st.subheader(f"📍 {d_obj.strftime('%d.%m.%Y')}")

    if sel_date in st.session_state.trainings:
        t = st.session_state.trainings[sel_date]
        with st.container(border=True):
            st.markdown(f"**{t['title']}** ({t['dauer']} Min)")
            u_status = st.checkbox("Erledigt ✅", value=(t['status'] == "✅"), key=f"chk_{sel_date}")
            u_rating = st.select_slider("Erfolg:", options=["❌", "😐", "🙂", "🤩"], value=t.get('rating', "😐"), key=f"rate_{sel_date}")
            u_notes = st.text_area("Notizen:", value=t.get('notes', ""), key=f"note_{sel_date}")
            
            c1, c2 = st.columns(2)
            if c1.button("Speichern", type="primary", use_container_width=True):
                st.session_state.trainings[sel_date].update({"status": "✅" if u_status else "⏳", "rating": u_rating, "notes": u_notes})
                st.rerun()
            if c2.button("Löschen", use_container_width=True):
                del st.session_state.trainings[sel_date]
                st.rerun()
    else:
        with st.expander("➕ Training planen"):
            auswahl = st.selectbox("Vorlage:", [v['name'] for v in st.session_state.vorlagen])
            if st.button("Hinzufügen"):
                v = next(i for i in st.session_state.vorlagen if i['name'] == auswahl)
                st.session_state.trainings[sel_date] = {"title": v['name'], "dauer": v['dauer'], "material": v['material'], "status": "⏳", "notes": "", "rating": "😐"}
                st.rerun()

# --- TAB 2: VORLAGEN ---
with tab2:
    st.subheader("Übungsvorlagen")
    for idx, v in enumerate(st.session_state.vorlagen):
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.write(f"**{v['name']}** ({v['dauer']} Min)")
            if c2.button("🗑️", key=f"del_v_{idx}"):
                st.session_state.vorlagen.pop(idx)
                st.rerun()
    with st.form("neue_v"):
        n = st.text_input("Name")
        d = st.number_input("Dauer", 5, 60, 15)
        m = st.text_input("Material")
        if st.form_submit_button("Vorlage hinzufügen"):
            if n: st.session_state.vorlagen.append({"name": n, "dauer": d, "material": m})
            st.rerun()

# --- TAB 3: STATISTIK (INKL. ERGEBNIS) ---
with tab3:
    st.subheader("📊 Statistik")
    if not st.session_state.trainings:
        st.info("Noch keine Daten.")
    else:
        # Dictionary in Liste für Pandas umwandeln
        data_list = []
        for d_str, val in st.session_state.trainings.items():
            row = val.copy()
            row['datum'] = pd.to_datetime(d_str)
            row['rating_num'] = smiley_map.get(row.get('rating', "😐"), 2)
            data_list.append(row)
        
        df = pd.DataFrame(data_list)
        zeitraum = st.radio("Zeitraum:", ["Gesamt", "Monat"], horizontal=True)
        
        if zeitraum == "Monat":
            jetzt = datetime.now()
            df = df[(df['datum'].dt.month == jetzt.month) & (df['datum'].dt.year == jetzt.year)]

        if not df.empty:
            erledigte_df = df[df['status'] == "✅"]
            
            m1, m2 = st.columns(2)
            m1.metric("Erledigt", len(erledigte_df))
            
            if not erledigte_df.empty:
                avg_rating = round(erledigte_df['rating_num'].mean())
                m2.metric("Schnitt-Erfolg", reverse_smiley_map.get(avg_rating, "😐"))
                
                st.markdown("### Erfolg pro Übung")
                # Gruppierung mit Anzahl und durchschnittlichem Ergebnis
                stats = erledigte_df.groupby('title').agg(
                    Anzahl=('title', 'count'),
                    Ergebnis_Schnitt=('rating_num', 'mean')
                ).reset_index()
                
                # Zahlen zurück in Smileys wandeln
                stats['Ergebnis'] = stats['Ergebnis_Schnitt'].apply(lambda x: reverse_smiley_map.get(round(x), "😐"))
                st.table(stats[['title', 'Anzahl', 'Ergebnis']])
            else:
                st.write("Schließe Trainings ab, um Ergebnisse zu sehen.")
                
