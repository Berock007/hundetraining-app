import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar as py_cal
from streamlit_gsheets import GSheetsConnection

# --- SETUP ---
st.set_page_config(
    page_title="Pfoten-Planer", 
    page_icon="🐾", 
    layout="centered"
)

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

# --- GEÄNDERTER ABSCHNITT FÜR TAB 1: PLANUNG ---

with tab1:
    st.markdown(f"<h3 style='text-align: center;'>{st.session_state.view_date.strftime('%B %Y')}</h3>", unsafe_allow_html=True)
    # ... (Navigations-Buttons wie vorher) ...

    # Kalender Grid (Wie vorher, zeigt Pfoten an, wenn MINDESTENS ein Training existiert)
    # ... (Kalender-Code-Block hier einfügen) ...
    
    st.divider()
    
    # DETAIL-ANSICHT (Mehrere Trainings pro Tag)
    sel_date = st.session_state.selected_date
    st.subheader(f"📍 Trainings am {datetime.strptime(sel_date, '%Y-%m-%d').strftime('%d.%m.%Y')}")

    # Alle Trainings für diesen speziellen Tag filtern
    day_trainings = trainings_df[trainings_df['datum'] == sel_date]

    if not day_trainings.empty:
        for idx, t in day_trainings.iterrows():
            # Jedes Training in einer eigenen kleinen Box (Expander oder Container)
            with st.container(border=True):
                col_a, col_b = st.columns([3, 1])
                status_icon = "✅" if t['status'] == "✅" else "⏳"
                col_a.markdown(f"**{status_icon} {t['title']}** ({t['dauer']} Min)")
                
                # Bearbeitungs-Modus in einem Expander verstecken, um Platz zu sparen
                with st.expander("Details bearbeiten / Notizen"):
                    u_status = st.checkbox("Erledigt", value=(t['status'] == "✅"), key=f"chk_{idx}")
                    u_rating = st.select_slider("Erfolg:", options=["❌", "😐", "🙂", "🤩"], value=t['rating'], key=f"rate_{idx}")
                    u_notes = st.text_area("Notizen:", value=t['notes'], key=f"note_{idx}")
                    
                    c1, c2 = st.columns(2)
                    if c1.button("Speichern", key=f"save_{idx}", type="primary"):
                        trainings_df.at[idx, 'status'] = "✅" if u_status else "⏳"
                        trainings_df.at[idx, 'rating'] = u_rating
                        trainings_df.at[idx, 'notes'] = u_notes
                        conn.update(worksheet="trainings", data=trainings_df)
                        st.rerun()
                    if c2.button("Löschen", key=f"del_{idx}"):
                        trainings_df = trainings_df.drop(idx)
                        conn.update(worksheet="trainings", data=trainings_df)
                        st.rerun()
    else:
        st.info("Noch kein Training für heute geplant.")

    # IMMER ANZEIGEN: Button zum Hinzufügen (egal ob schon eins existiert)
    with st.expander("➕ Neues Training hinzufügen"):
        if not vorlagen_df.empty:
            auswahl = st.selectbox("Vorlage wählen:", vorlagen_df['name'].tolist(), key="new_sel")
            if st.button("Hinzufügen", use_container_width=True):
                v = vorlagen_df[vorlagen_df['name'] == auswahl].iloc[0]
                new_row = pd.DataFrame([{
                    "datum": sel_date, 
                    "title": v['name'], 
                    "dauer": v['dauer'], 
                    "material": v['material'], 
                    "status": "⏳", 
                    "notes": "", 
                    "rating": "😐"
                }])
                trainings_df = pd.concat([trainings_df, new_row], ignore_index=True)
                conn.update(worksheet="trainings", data=trainings_df)
                st.rerun()
        else:
            st.warning("Bitte erst Vorlagen im Tab '⚙️ Vorlagen' erstellen!")


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

# --- TAB 3: STATISTIK (VOLLSTÄNDIG & REPARIERT) ---
with tab3:
    st.subheader("📊 Statistik")
    
    if not trainings_df.empty:
        # Kopie der Daten erstellen und Datum umwandeln
        df_stats = trainings_df.copy()
        df_stats['datum'] = pd.to_datetime(df_stats['datum'])
        
        # Auswahl des Zeitraums
        zeitraum = st.radio("Zeitraum auswählen:", ["Gesamt", "Aktueller Monat"], horizontal=True)
        
        # Filter anwenden
        if zeitraum == "Aktueller Monat":
            jetzt = datetime.now()
            df_stats = df_stats[(df_stats['datum'].dt.month == jetzt.month) & 
                                (df_stats['datum'].dt.year == jetzt.year)]

        # Nur erledigte Trainings zählen
        erledigt_df = df_stats[df_stats['status'] == "✅"].copy()
        
        # Metriken anzeigen
        m1, m2 = st.columns(2)
        m1.metric("Erledigt", len(erledigt_df))
        
        if not erledigt_df.empty:
            # Bewertung in Zahlen umwandeln
            erledigt_df['rating_num'] = erledigt_df['rating'].map(smiley_map)
            
            # Durchschnittlicher Erfolg (Gesamt-Smiley)
            avg_val = round(erledigt_df['rating_num'].mean())
            m2.metric("Schnitt-Erfolg", reverse_smiley_map.get(avg_val, "😐"))
            
            # Gruppierung nach Übung
            stats = erledigt_df.groupby('title').agg(
                Anzahl=('title', 'count'), 
                Schnitt=('rating_num', 'mean')
            ).reset_index()
            
            # Zurück in Smileys wandeln
            stats['Ergebnis'] = stats['Schnitt'].apply(lambda x: reverse_smiley_map.get(round(x), "😐"))
            
            # Tabelle anzeigen
            st.table(stats[['title', 'Anzahl', 'Ergebnis']])
        else:
            st.info("In diesem Zeitraum wurden noch keine Trainings als 'Erledigt' markiert.")
    else:
        st.info("Noch keine Trainingsdaten in der Cloud gefunden.")
        
