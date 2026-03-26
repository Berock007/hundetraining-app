import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar as py_cal

# --- SETUP ---
st.set_page_config(page_title="Pfoten-Planer Pro", layout="centered", page_icon="🐾")

# --- PRÄZISER HANDY-FIX (Nur für den Kalender-Bereich) ---
st.markdown("""
    <style>
    /* Nur die Spalten innerhalb des Kalender-Grids fixieren */
    .stColumn {
        min-width: 0px !important;
    }
    
    /* Spezielles Styling für die Buttons im Kalender-Tab */
    div[data-testid="stHorizontalBlock"] {
        gap: 2px !important;
    }

    /* Die Tabs (Reiter) wieder normal positionieren */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        margin-top: 10px;
    }

    /* Kalender-Buttons kompakt, aber Tabs-Buttons normal */
    div[data-testid="column"] button {
        width: 100% !important;
        padding: 2px !important;
        height: 48px !important;
        font-size: 11px !important;
    }

    /* Padding für den Hauptinhalt korrigieren */
    .block-container {
        padding-top: 2rem !important;
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

smiley_map = {"❌": 1, "😐": 2, "🙂": 3, "🤩": 4}
reverse_smiley_map = {1: "❌", 2: "😐", 3: "🙂", 4: "🤩"}

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📅 Planung", "⚙️ Vorlagen", "📊 Statistik"])

# --- TAB 1: PLANUNG ---
with tab1:
    st.markdown(f"<h3 style='text-align: center;'>{st.session_state.view_date.strftime('%B %Y')}</h3>", unsafe_allow_html=True)
    
    c_nav1, c_nav2 = st.columns(2)
    with c_nav1:
        if st.button("⬅️ Letzter Monat", use_container_width=True): 
            st.session_state.view_date -= timedelta(days=30)
            st.rerun()
    with c_nav2:
        if st.button("Nächster Monat ➡️", use_container_width=True): 
            st.session_state.view_date += timedelta(days=30)
            st.rerun()

    st.write("") 

    # Kalender Header
    days_header = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    cols_h = st.columns(7)
    for i, day in enumerate(days_header):
        cols_h[i].markdown(f"<p style='text-align:center; font-weight:bold; font-size:10px; margin:0;'>{day}</p>", unsafe_allow_html=True)

    # Kalender Tage
    cal = py_cal.Calendar(firstweekday=0)
    month_days = cal.monthdatescalendar(st.session_state.view_date.year, st.session_state.view_date.month)

    for week in month_days:
        cols = st.columns(7)
        for i, day in enumerate(week):
            date_str = str(day)
            label = f"{day.day}"
            
            if date_str in st.session_state.trainings:
                t_item = st.session_state.trainings[date_str]
                label += "\n🐾" if t_item['status'] == "⏳" else "\n✅"
            
            if day.month == st.session_state.view_date.month:
                if cols[i].button(label, key=f"d_{date_str}"):
                    st.session_state.selected_date = date_str
            else:
                cols[i].button(label, key=f"d_{date_str}", disabled=True)

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
            
            if st.button("Speichern", type="primary", use_container_width=True):
                st.session_state.trainings[sel_date].update({"status": "✅" if u_status else "⏳", "rating": u_rating, "notes": u_notes})
                st.rerun()
            if st.button("🗑️ Training löschen", use_container_width=True):
                del st.session_state.trainings[sel_date]
                st.rerun()
    else:
        with st.expander("➕ Training planen"):
            auswahl = st.selectbox("Vorlage:", [v['name'] for v in st.session_state.vorlagen])
            if st.button("In Plan eintragen", use_container_width=True):
                v = next(i for i in st.session_state.vorlagen if i['name'] == auswahl)
                st.session_state.trainings[sel_date] = {"title": v['name'], "dauer": v['dauer'], "material": v['material'], "status": "⏳", "notes": "", "rating": "😐"}
                st.rerun()

# --- TAB 2 & 3 (Wie vorher, Statistiken sind korrigiert) ---
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
        d = st.number_input("Dauer (Min)", 5, 60, 15)
        m = st.text_input("Material")
        if st.form_submit_button("Vorlage hinzufügen"):
            if n: st.session_state.vorlagen.append({"name": n, "dauer": d, "material": m})
            st.rerun()

with tab3:
    st.subheader("📊 Statistik")
    if not st.session_state.trainings:
        st.info("Noch keine Daten.")
    else:
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
            st.metric("Erledigt", len(erledigte_df))
            
            if not erledigte_df.empty:
                avg_val = round(erledigte_df['rating_num'].mean())
                st.metric("Schnitt-Erfolg", reverse_smiley_map.get(avg_val, "😐"))
                
                stats = erledigte_df.groupby('title').agg(Anzahl=('title', 'count'), Erfolg_Num=('rating_num', 'mean')).reset_index()
                stats['Ergebnis'] = stats['Erfolg_Num'].apply(lambda x: reverse_smiley_map.get(round(x), "😐"))
                st.table(stats[['title', 'Anzahl', 'Ergebnis']])
                
