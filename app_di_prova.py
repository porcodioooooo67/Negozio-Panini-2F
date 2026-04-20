import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# --- INIZIALIZZAZIONE DATABASE ---
# Crea il database e le tabelle se non esistono
def init_db():
    conn = sqlite3.connect('database_panini.db')
    c = conn.cursor()
    # Tabella per il registro storico di tutte le azioni
    c.execute('''CREATE TABLE IF NOT EXISTS registro 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, data_ora TEXT, utente TEXT, eta INTEGER, azione TEXT)''')
    # Tabella per la sessione (ricorda l'ultimo utente loggato)
    c.execute('''CREATE TABLE IF NOT EXISTS sessione_attiva 
                 (id INTEGER PRIMARY KEY, nome TEXT, eta INTEGER, login_status INTEGER)''')
    conn.commit()
    conn.close()

def salva_azione_db(nome, eta, azione):
    conn = sqlite3.connect('database_panini.db')
    c = conn.cursor()
    ora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    c.execute("INSERT INTO registro (data_ora, utente, eta, azione) VALUES (?, ?, ?, ?)", 
              (ora, nome, eta, azione))
    conn.commit()
    conn.close()

def set_persistenza(nome, eta, status):
    conn = sqlite3.connect('database_panini.db')
    c = conn.cursor()
    c.execute("DELETE FROM sessione_attiva") 
    c.execute("INSERT INTO sessione_attiva (nome, eta, login_status) VALUES (?, ?, ?)", 
              (nome, eta, 1 if status else 0))
    conn.commit()
    conn.close()

def carica_persistenza():
    conn = sqlite3.connect('database_panini.db')
    c = conn.cursor()
    c.execute("SELECT nome, eta, login_status FROM sessione_attiva LIMIT 1")
    res = c.fetchone()
    conn.close()
    return res

# --- AVVIO ---
init_db()
st.set_page_config(page_title="Negozio Panini 2F", page_icon="🍔")

# Carica i dati dal database per vedere se c'è un utente già loggato
dati_salvati = carica_persistenza()

if 'autorizzato' not in st.session_state:
    if dati_salvati and dati_salvati[2] == 1:
        st.session_state.autorizzato = True
        st.session_state.nome_utente = dati_salvati[0]
        st.session_state.eta_utente = dati_salvati[1]
    else:
        st.session_state.autorizzato = False

# --- LOGICA PAGINE ---
if not st.session_state.autorizzato:
    st.title("Negozio panini 2F 🍔")
    st.header("Verifica Identità")
    
    nome = st.text_input("Inserisci il tuo nome")
    age = st.number_input("Inserisci la tua età", min_value=0, max_value=110, value=0)

    if st.button("Entra nel Negozio"):
        if nome != "" and age >= 18:
            st.session_state.autorizzato = True
            st.session_state.nome_utente = nome
            st.session_state.eta_utente = age
            set_persistenza(nome, age, True)
            salva_azione_db(nome, age, "LOGIN EFFETTUATO")
            st.rerun()
        elif age < 18:
            salva_azione_db(nome, age, "ACCESSO NEGATO (MINORENNE)")
            st.error("Accesso vietato ai minori!")
else:
    st.title(f"🍔 Menu di {st.session_state.nome_utente}")
    st.write(f"Stato: Loggato (Database Attivo)")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("I Nostri Panini")
        if st.button("Compra Panino Ignorante (5€)"):
            salva_azione_db(st.session_state.nome_utente, st.session_state.eta_utente, "Comprato Panino Ignorante")
            st.success("Acquistato!")
        
        if st.button("Compra 2F Special (8€)"):
            salva_azione_db(st.session_state.nome_utente, st.session_state.eta_utente, "Comprato 2F Special")
            st.balloons()
            st.success("Il Re è tuo!")

    with col2:
        st.subheader("Le Bevande")
        if st.button("Birra Media (4€)"):
            salva_azione_db(st.session_state.nome_utente, st.session_state.eta_utente, "Comprata Birra")
            st.info("Salute! 🍻")

    st.divider()
    if st.button("Logout"):
        salva_azione_db(st.session_state.nome_utente, st.session_state.eta_utente, "LOGOUT")
        set_persistenza("", 0, False)
        st.session_state.autorizzato = False
        st.rerun()

    # REGISTRO STORICO (Sotto il menu)
    with st.expander("Registro Storico Accessi"):
        conn = sqlite3.connect('database_panini.db')
        df_log = pd.read_sql_query("SELECT * FROM registro ORDER BY id DESC", conn)
        st.dataframe(df_log)
        conn.close()
