import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURAZIONE E DATABASE ---
DB_NAME = "social_media.db"
UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS posts 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user TEXT, 
                  content TEXT, 
                  file_path TEXT, 
                  file_type TEXT, 
                  timestamp TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- FUNZIONI DI SUPPORTO ---
def save_post(user, text, file):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    file_path = None
    file_type = None
    
    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        file_type = file.type.split('/')[0] # 'image' o 'video'
        
    c.execute("INSERT INTO posts (user, content, file_path, file_type, timestamp) VALUES (?, ?, ?, ?, ?)",
              (user, text, file_path, file_type, datetime.now().strftime("%d/%m/%Y %H:%M")))
    conn.commit()
    conn.close()

# --- INTERFACCIA STREAMLIT ---
st.set_page_config(page_title="Mini Social App", layout="centered")

# Gestione Sessione Utente
if 'username' not in st.session_state:
    st.session_state.username = None

if st.session_state.username is None:
    st.title("🚀 Benvenuto")
    user_input = st.text_input("Inserisci il tuo username per entrare:")
    if st.button("Accedi"):
        if user_input:
            st.session_state.username = user_input
            st.rerun()
else:
    # Sidebar per Logout e Info
    st.sidebar.title(f"Ciao, {st.session_state.username}!")
    if st.sidebar.button("Logout"):
        st.session_state.username = None
        st.rerun()

    # Sezione Creazione Post
    st.header("Crea un nuovo post")
    with st.expander("Scrivi qualcosa..."):
        post_text = st.text_area("Cosa hai in mente?")
        uploaded_file = st.file_uploader("Aggiungi una foto o un video", type=["png", "jpg", "jpeg", "mp4", "mov"])
        
        if st.button("Pubblica"):
            if post_text or uploaded_file:
                save_post(st.session_state.username, post_text, uploaded_file)
                st.success("Post pubblicato!")
                st.rerun()
            else:
                st.warning("Inserisci almeno un testo o un file!")

    st.divider()

    # Visualizzazione Feed
    st.subheader("Feed della Community")
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM posts ORDER BY id DESC", conn)
    conn.close()

    if not df.empty:
        for index, row in df.iterrows():
            with st.container(border=True):
                st.subheader(f"👤 {row['user']}")
                st.caption(f"Pubblicato il: {row['timestamp']}")
                
                if row['content']:
                    st.write(row['content'])
                
                if row['file_path'] and os.path.exists(row['file_path']):
                    if row['file_type'] == 'image':
                        st.image(row['file_path'], use_container_width=True)
                    elif row['file_type'] == 'video':
                        st.video(row['file_path'])
    else:
        st.info("Non ci sono ancora post. Sii il primo a pubblicare!")
