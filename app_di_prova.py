import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# --- INIZIALIZZAZIONE DATABASE ---
def init_db():
    conn = sqlite3.connect('database_panini.db')
    c = conn.cursor()
    # Registro azioni
    c.execute('''CREATE TABLE IF NOT EXISTS registro 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, data_ora TEXT, utente TEXT, eta INTEGER, azione TEXT, spesa REAL)''')
    # Sessione attiva con spesa accumulata
    c.execute('''CREATE TABLE IF NOT EXISTS sessione_attiva 
                 (id INTEGER PRIMARY KEY, nome TEXT, eta INTEGER, login_status INTEGER, totale_accumulato REAL)''')
    conn.commit()
    conn.close()

def salva_azione_db(nome, eta, azione, spesa=0.0):
    conn = sqlite3.connect('database_panini.db')
    c = conn.cursor()
    ora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    c.execute("INSERT INTO registro (data_ora, utente, eta, azione, spesa) VALUES (?, ?, ?, ?, ?)", 
              (ora, nome, eta, azione, spesa))
    
    # Se c'è una spesa, aggiorniamo il totale nella sessione attiva
    if spesa > 0:
        c.execute("UPDATE sessione_attiva SET totale_accumulato = totale_accumulato + ?", (spesa,))
    
    conn.commit()
    conn.close()

def set_persistenza(nome, eta, status):
    conn = sqlite3.connect('database_panini.db')
    c = conn.cursor()
    c.execute("DELETE FROM sessione_attiva") 
    c.execute("INSERT INTO sessione_attiva (nome, eta, login_status, totale_accumulato) VALUES (?, ?, ?, ?)", 
              (nome, eta, 1 if status else 0, 0.0))
    conn.commit()
    conn.close()

def carica_persistenza():
    conn = sqlite3.connect('database_panini.db')
    c = conn.cursor()
    c.execute("SELECT nome, eta, login_status, totale_accumulato FROM sessione_attiva LIMIT 1")
    res = c.fetchone()
    conn.close()
    return res

# --- AVVIO ---
init_db()
st.set_page_config(page_title="Negozio Panini 2F", page_icon="🍔")

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
            st.error("Accesso vietato ai minori!")

else:
    # Recuperiamo il totale aggiornato dal DB
    info_aggiornate = carica_persistenza()
    totale_speso = info_aggiornate[3] if info_aggiornate else 0.0

    st.title(f"🍔 Menu di {st.session_state.nome_utente}")
    
    # BOX DEL CONTO
    st.sidebar.metric(label="Totale Speso", value=f"{totale_speso:.2f} €")
    st.sidebar.write("---")
    if st.sidebar.button("Svuota Carrello/Reset Conto"):
        conn = sqlite3.connect('database_panini.db')
        conn.cursor().execute("UPDATE sessione_attiva SET totale_accumulato = 0.0")
        conn.commit()
        conn.close()
        st.rerun()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("I Nostri Panini")
        if st.button("Compra Panino Ignorante (5.00€)"):
            salva_azione_db(st.session_state.nome_utente, st.session_state.eta_utente, "Panino Ignorante", 5.00)
            st.success("Aggiunto al conto!")
            st.rerun()
        
        if st.button("Compra 2F Special (8.50€)"):
            salva_azione_db(st.session_state.nome_utente, st.session_state.eta_utente, "2F Special", 8.50)
            st.balloons()
            st.rerun()

    with col2:
        st.subheader("Le Bevande")
        if st.button("Birra Media (4.50€)"):
            salva_azione_db(st.session_state.nome_utente, st.session_state.eta_utente, "Birra Media", 4.50)
            st.info("Salute! 🍻")
            st.rerun()

    st.divider()
    if st.button("Logout"):
        salva_azione_db(st.session_state.nome_utente, st.session_state.eta_utente, "LOGOUT")
        set_persistenza("", 0, False)
        st.session_state.autorizzato = False
        st.rerun()

    with st.expander("Registro Storico Accessi e Acquisti"):
        conn = sqlite3.connect('database_panini.db')
        df_log = pd.read_sql_query("SELECT data_ora, utente, azione, spesa FROM registro ORDER BY id DESC", conn)
        st.dataframe(df_log)
        conn.close()
