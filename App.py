import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar as py_cal
from streamlit_gsheets import GSheetsConnection
import streamlit.components.v1 as components

# --- 1. SETUP (Name & Icon) ---
st.set_page_config(
    page_title="Pfoten-Planer",
    page_icon="https://raw.githubusercontent.com/Berock007/hundetraining-app/main/10361.png",
    layout="centered"
)

# --- 2. DER "ERZWINGEN"-TRICK FÜR CHROME & ANDROID ---
# Dieser Block injiziert JavaScript, um den App-Namen und das Icon im Browser-Header zu fixieren.
components.html(
    f"""
    <script>
        window.parent.document.title = "Pfoten-Planer";
        var link = window.parent.document.querySelector("link[rel*='icon']") || window.parent.document.createElement('link');
        link.type = 'image/png';
        link.rel = 'shortcut icon';
        link.href = 'https://raw.githubusercontent.com/Berock007/hundetraining-app/main/10361.png';
        window.parent.document.getElementsByTagName('head')[0].appendChild(link);
    </script>
    """,
    height=0,
)

# --- 3. HANDY-OPTIMIERUNG (CSS) ---
st.markdown("""
    <style>
    [data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 2px !important; }
    [data-testid="stHorizontalBlock"] > div { min-width: 0px !important; flex: 1 1 0% !important; }
    .stButton button { width: 100% !important; padding: 2px !important; height: 45px !important; font-size: 12px !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; margin-top: 10px; }
    .block-container { padding-top: 1.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. CLOUD-VERBINDUNG ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        t_df = conn.read(worksheet="trainings", ttl="0s")
        v_df = conn.read(worksheet="vorlagen", ttl="0s")
        return t_df.dropna(how='all'), v_df.dropna(how='all')
    except:
        return pd.DataFrame(columns=['datum', 'title', 'dauer', 'material', 'status', 'notes', 'rating']), \
               pd.DataFrame(columns=['name', 'dauer', 'material'])

trainings_df, vorlagen_df = load_data()

# Hilfswerkzeuge
smiley_map = {"❌": 1, "😐": 2, "🙂": 3, "🤩": 4}
reverse_smiley_map = {1: "❌", 2: "😐", 3: "🙂", 4: "🤩"}

if 'view_date' not in st.session_state: st.session_state.view_date = datetime.now().date()
if 'selected_date' not in st.session_state: st.session_state.selected_date = str(datetime.now().date())

tab1, tab2, tab3 = st.tabs(["📅 Plan", "⚙️ Vorlagen", "📊 Statistik"])

# --- TAB 1: PLANUNG ---
with tab1:
    st.markdown(f"<h3 style='text-align: center;'>{st.session_state.view_date.strftime('%B %Y')}</h3>", unsafe_allow_html=True)
    c_nav1, c_nav2 = st.columns(2)
    with c_nav1:
        if st.button("⬅️ Zurück"): 
            st.session_state.view_date -= timedelta(days=30); st.rerun()
    with c_nav2:
        if st.button("Vor ➡️"): 
            st.session_state.view_date += timedelta(days=30); st.rerun()

    # Kalender Grid
    days_header = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    cols_h = st.columns(7)
    for i, day in enumerate(days_header):
        cols_h[i].markdown(f"<p style='text-align:center; font-size:10px; font-weight:bold;'>{day}</p>", unsafe_allow_html=True)

    cal = py_cal.Calendar(firstweekday=0)
    month_days = cal.monthdatescalendar(st.session_state.view_date.year, st.session_state.view_date.month)

    for week in month_days:
        cols = st.columns(7)
        for i, day in enumerate(week):
            date_str = str(day)
            label = f"{day.day}"
            day_data = trainings_df[trainings_df['datum'] == date_str]
            if not day_data.empty:
                label += "\n✅" if all(day_data['status'] == "✅") else "\n🐾"
            
            if day.month == st.session_state.view_date.month:
                if cols[i].button(label, key=f"d_{date_str}"):
                    st.session_state.selected_date = date_str
            else:
                cols[i].button(label, key=f"d_{date_str}", disabled=True)

    st.divider()
    
    # Detail-Liste
    sel_date = st.session_state.selected_date
    st.subheader(f"📍 {datetime.strptime(sel_date, '%Y-%m-%d').strftime('%d.%m.%Y')}")

    day_trainings = trainings_df[trainings_df['datum'] == sel_date]

    if not day_trainings.empty:
        for idx, t in day_trainings.iterrows():
            with st.container(border=True):
                st.markdown(f"**{t['title']}** ({t['dauer']} Min)")
                with st.expander("Details / Notizen"):
                    u_status = st.checkbox("Erledigt", value=(t['status'] == "✅"), key=f"st_{idx}")
                    u_rating = st.select_slider("Erfolg:", options=["❌", "😐", "🙂", "🤩"], value=t['rating'] if pd.notna(t['rating']) else "😐", key=f"ra_{idx}")
                    u_notes = st.text_area("Notizen:", value=str(t['notes']) if pd.notna(t['notes']) else "", key=f"no_{idx}")
                    
                    c1, c2 = st.columns(2)
                    if c1.button("Speichern", key=f"sv_{idx}", type="primary"):
                        trainings_df.at[idx, 'status'] = "✅" if u_status else "⏳"
                        trainings_df.at[idx, 'rating'] = u_rating
                        trainings_df.at[idx, 'notes'] = u_notes
                        conn.update(worksheet="trainings", data=trainings_df); st.rerun()
                    if c2.button("Löschen", key=f"del_{idx}"):
                        trainings_df = trainings_df.drop(idx)
                        conn.update(worksheet="trainings", data=trainings_df); st.rerun()
    else:
        st.info("Noch kein Training geplant.")

    with st.expander("➕ Weiteres Training hinzufügen"):
        if not vorlagen_df.empty:
            auswahl = st.selectbox("Vorlage:", vorlagen_df['name'].tolist())
            if st.button("In Plan eintragen", use_container_width=True):
                v = vorlagen_df[vorlagen_df['name'] == auswahl].iloc[0]
                new_row = pd.DataFrame([{"datum": sel_date, "title": v['name'], "dauer": v['dauer'], "material": v['material'], "status": "⏳", "notes": "", "rating": "😐"}])
                trainings_df = pd.concat([trainings_df, new_row], ignore_index=True)
                conn.update(worksheet="trainings", data=trainings_df); st.rerun()

# --- TAB 2: VORLAGEN ---
with tab2:
    st.subheader("Übungsvorlagen")
    if not vorlagen_df.empty:
        for idx, v in vorlagen_df.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{v['name']}** ({v['dauer']} Min)")
                if c2.button("🗑️", key=f"dv_{idx}"):
                    vorlagen_df = vorlagen_df.drop(idx)
                    conn.update(worksheet="vorlagen", data=vorlagen_df); st.rerun()
    with st.form("neue_v"):
        n = st.text_input("Übungsname")
        d = st.number_input("Dauer (Min)", 5, 60, 15)
        m = st.text_input("Material")
        if st.form_submit_button("Vorlage speichern"):
            if n:
                new_v = pd.DataFrame([{"name": n, "dauer": d, "material": m}])
                vorlagen_df = pd.concat([vorlagen_df, new_v], ignore_index=True)
                conn.update(worksheet="vorlagen", data=vorlagen_df); st.rerun()

# --- TAB 3: STATISTIK ---
with tab3:
    st.subheader("📊 Statistik")
    if not trainings_df.empty:
        df_stats = trainings_df.copy()
        df_stats['datum'] = pd.to_datetime(df_stats['datum'])
        zeitraum = st.radio("Zeitraum:", ["Gesamt", "Aktueller Monat"], horizontal=True)
        if zeitraum == "Aktueller Monat":
            jetzt = datetime.now()
            df_stats = df_stats[(df_stats['datum'].dt.month == jetzt.month) & (df_stats['datum'].dt.year == jetzt.year)]
        
        erledigt_df = df_stats[df_stats['status'] == "✅"].copy()
        if not erledigt_df.empty:
            erledigt_df['rating_num'] = erledigt_df['rating'].map(smiley_map)
            stats = erledigt_df.groupby('title').agg(Anzahl=('title', 'count'), Schnitt=('rating_num', 'mean')).reset_index()
            stats['Ergebnis'] = stats['Schnitt'].apply(lambda x: reverse_smiley_map.get(round(x), "😐"))
            st.table(stats[['title', 'Anzahl', 'Ergebnis']])
        else:
            st.info("Keine erledigten Trainings.")
            
