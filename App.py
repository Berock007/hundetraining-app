import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar as py_cal
from streamlit_gsheets import GSheetsConnection

# --- SETUP ---
st.set_page_config(page_title="Pfoten-Planer Cloud", layout="centered", page_icon="🐾")

# --- HANDY-FIX CSS (Wie zuvor) ---
st.markdown("""
    <style>
    [data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 2px !important; }
    [data-testid="stHorizontalBlock"] > div { min-width: 0px !important; flex: 1 1 0% !important; }
    .stButton button { width: 100% !important; padding: 2px !important; height: 45px !important; font-size: 10px !important; }
    .block-container { padding-top: 2rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CLOUD-VERBINDUNG ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Daten aus Google Sheets laden
def load_data():
    try:
        trainings_df = conn.read(worksheet="trainings", ttl="0s")
        vorlagen_df = conn.read(worksheet="vorlagen", ttl="0s")
        return trainings_df, vorlagen_df
    except:
        # Falls die Tabelle leer ist, leere DataFrames zurückgeben
        return pd.DataFrame(columns=['datum', 'title', 'dauer', 'material', 'status', 'notes', 'rating']), \
               pd.DataFrame(columns=['name', 'dauer', 'material'])

trainings_df, vorlagen_df = load_data()

# Hilfswerkzeuge
smiley_map = {"❌": 1, "😐": 2, "🙂": 3, "🤩": 4}
reverse_smiley_map = {1: "❌", 2: "😐", 3: "🙂", 4: "🤩"}

# State Management
if 'view_date' not in st.session_state: st.session_state.view_date = datetime.now().date()
if 'selected_date' not in st.session_state: st.session_state.selected_date = str(datetime.now().date())

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📅 Planung", "⚙️ Vorlagen", "📊 Statistik"])

# --- TAB 1: PLANUNG ---
with tab1:
    st.markdown(f"<h3 style='text-align: center;'>{st.session_state.view_date.strftime('%B %Y')}</h3>", unsafe_allow_html=True)
    c_nav1, c_nav2 = st.columns(2)
    with c_nav1:
        if st.button("⬅️ Zurück"): 
            st.session_state.view_date -= timedelta(days=30)
            st.rerun()
    with c_nav2:
        if st.button("Vor ➡️"): 
            st.session_state.view_date += timedelta(days=30)
            st.rerun()

    # Kalender Grid
    days_header = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    cols_h = st.columns(7)
    for i, day in enumerate(days_header):
        cols_h[i].markdown(f"<p style='text-align:center; font-size:10px;'>{day}</p>", unsafe_allow_html=True)

    cal = py_cal.Calendar(firstweekday=0)
    month_days = cal.monthdatescalendar(st.session_state.view_date.year, st.session_state.view_date.month)

    for week in month_days:
        cols = st.columns(7)
        for i, day in enumerate(week):
            date_str = str(day)
            label = f"{day.day}"
            
            # Check ob Training existiert
            day_data = trainings_df[trainings_df['datum'] == date_str]
            if not day_data.empty:
                status = day_data.iloc[0]['status']
                label += "\n🐾" if status == "⏳" else "\n✅"
            
            if day.month == st.session_state.view_date.month:
                if cols[i].button(label, key=f"d_{date_str}"):
                    st.session_state.selected_date = date_str
            else:
                cols[i].button(label, key=f"d_{date_str}", disabled=True)

    st.divider()
    
    # Detail-Ansicht & Speichern in Google Sheets
    sel_date = st.session_state.selected_date
    st.subheader(f"📍 {datetime.strptime(sel_date, '%Y-%m-%d').strftime('%d.%m.%Y')}")

    current_training = trainings_df[trainings_df['datum'] == sel_date]

    if not current_training.empty:
        t = current_training.iloc[0]
        with st.container(border=True):
            st.markdown(f"**{t['title']}** ({t['dauer']} Min)")
            u_status = st.checkbox("Erledigt ✅", value=(t['status'] == "✅"))
            u_rating = st.select_slider("Erfolg:", options=["❌", "😐", "🙂", "🤩"], value=t['rating'])
            u_notes = st.text_area("Notizen:", value=t['notes'])
            
            if st.button("Speichern", type="primary"):
                # Zeile aktualisieren
                trainings_df.loc[trainings_df['datum'] == sel_date, ['status', 'rating', 'notes']] = ["✅" if u_status else "⏳", u_rating, u_notes]
                conn.update(worksheet="trainings", data=trainings_df)
                st.success("Cloud aktualisiert!")
                st.rerun()
            if st.button("Löschen"):
                trainings_df = trainings_df[trainings_df['datum'] != sel_date]
                conn.update(worksheet="trainings", data=trainings_df)
                st.rerun()
    else:
        with st.expander("➕ Planen"):
            if not vorlagen_df.empty:
                auswahl = st.selectbox("Vorlage:", vorlagen_df['name'].tolist())
                if st.button("Eintragen"):
                    v = vorlagen_df[vorlagen_df['name'] == auswahl].iloc[0]
                    new_row = pd.DataFrame([{
                        "datum": sel_date, "title": v['name'], "dauer": v['dauer'], 
                        "material": v['material'], "status": "⏳", "notes": "", "rating": "😐"
                    }])
                    trainings_df = pd.concat([trainings_df, new_row], ignore_index=True)
                    conn.update(worksheet="trainings", data=trainings_df)
                    st.rerun()
            else:
                st.write("Erstelle erst Vorlagen!")

# --- TAB 2: VORLAGEN ---
with tab2:
    st.subheader("Übungsvorlagen")
    if not vorlagen_df.empty:
        for idx, v in vorlagen_df.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{v['name']}** ({v['dauer']} Min)")
                if c2.button("🗑️", key=f"del_v_{idx}"):
                    vorlagen_df = vorlagen_df.drop(idx)
                    conn.update(worksheet="vorlagen", data=vorlagen_df)
                    st.rerun()
    
    with st.form("neue_v"):
        n = st.text_input("Name")
        d = st.number_input("Dauer", 5, 60, 15)
        m = st.text_input("Material")
        if st.form_submit_button("Vorlage hinzufügen"):
            if n:
                new_v = pd.DataFrame([{"name": n, "dauer": d, "material": m}])
                vorlagen_df = pd.concat([vorlagen_df, new_v], ignore_index=True)
                conn.update(worksheet="vorlagen", data=vorlagen_df)
                st.rerun()

# --- TAB 3: STATISTIK ---
with tab3:
    st.subheader("📊 Statistik")
    if not trainings_df.empty:
        erledigt = trainings_df[trainings_df['status'] == "✅"]
        st.metric("Erledigt gesamt", len(erledigt))
        if not erledigt.empty:
            erledigt['rating_num'] = erledigt['rating'].map(smiley_map)
            stats = erledigt.groupby('title').agg(Anzahl=('title', 'count'), Schnitt=('rating_num', 'mean')).reset_index()
            stats['Erfolg'] = stats['Schnitt'].apply(lambda x: reverse_smiley_map[round(x)])
            st.table(stats[['title', 'Anzahl', 'Ergebnis']])
            
