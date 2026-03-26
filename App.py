import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar as py_cal

# --- SETUP ---
st.set_page_config(page_title="Pfoten-Planer Pro", layout="centered", page_icon="🐾")

# CSS für quadratische Buttons (Handy-Optimierung)
st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] { gap: 2px !important; }
    button { 
        padding: 5px !important; 
        height: 50px !important; 
        font-size: 12px !important;
        border-radius: 5px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialisierung der Daten
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

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📅 Planung", "⚙️ Vorlagen", "📊 Statistik"])

# --- TAB 1: PLANUNG ---
with tab1:
    st.title("🐾 Pfoten-Planer")
    
    # Monat umschalten
    c_nav1, c_nav2, c_nav3 = st.columns([1, 3, 1])
    with c_nav1:
        if st.button("⬅️", key="prev"): st.session_state.view_date -= timedelta(days=30)
    with c_nav3:
        if st.button("➡️", key="next"): st.session_state.view_date += timedelta(days=30)
    with c_nav2:
        curr_month = st.session_state.view_date
        st.markdown(f"<h4 style='text-align: center;'>{curr_month.strftime('%B %Y')}</h4>", unsafe_allow_html=True)

    # Kalender-Grid
    days_header = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    cols = st.columns(7)
    for i, day in enumerate(days_header):
        cols[i].caption(day)

    cal = py_cal.Calendar(firstweekday=0)
    month_days = cal.monthdatescalendar(curr_month.year, curr_month.month)

    for week in month_days:
        cols = st.columns(7)
        for i, day in enumerate(week):
            date_str = str(day)
            
            # Button Label & Style
            is_today = (day == datetime.now().date())
            label = f"{day.day}"
            if date_str in st.session_state.trainings:
                label += "\n🐶"
            
            # Button anzeigen
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

# --- TAB 3: STATISTIK (REPARIERT) ---
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
            data_list.append(row)
        
        df = pd.DataFrame(data_list)
        zeitraum = st.radio("Zeitraum:", ["Gesamt", "Monat"], horizontal=True)
        
        if zeitraum == "Monat":
            jetzt = datetime.now()
            df = df[(df['datum'].dt.month == jetzt.month) & (df['datum'].dt.year == jetzt.year)]

        if not df.empty:
            erledigt = len(df[df['status'] == "✅"])
            st.metric("Abgeschlossene Trainings", erledigt)
            
            stats = df[df['status'] == "✅"].groupby('title').size().reset_index(name='Anzahl')
            st.table(stats)
            
