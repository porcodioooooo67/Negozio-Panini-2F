import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- FUNZIONE PER IL LOG (REGISTRO) ---
def salva_azione(nome, eta, azione):
    log_file = 'registro_accessi.csv'
    ora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    nuovi_dati = pd.DataFrame([{
        "Data_Ora": ora,
        "Utente": nome,
        "Eta": eta,
        "Azione": azione
    }])

    # Salva sul file CSV (lo crea se non esiste)
    if not os.path.isfile(log_file):
        nuovi_dati.to_csv(log_file, index=False)
    else:
        nuovi_dati.to_csv(log_file, mode='a', index=False, header=False)

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Negozio Panini 2F", page_icon="🍔")

if 'autorizzato' not in st.session_state:
    st.session_state.autorizzato = False

# --- LOGICA DELLE PAGINE ---
if not st.session_state.autorizzato:
    # PAGINA DI ACCESSO
    st.title("Negozio panini 2F 🍔")
    st.header("Verifica la tua identità")

    nome = st.text_input("Inserisci il tuo nome")
    age = st.number_input("Inserisci la tua età", min_value=0, max_value=110, value=0)

    if st.button("Entra nel Negozio"):
        if nome == "":
            st.warning("Per favore, inserisci un nome!")
        elif age >= 18:
            st.session_state.autorizzato = True
            st.session_state.nome_utente = nome
            st.session_state.eta_utente = age
            salva_azione(nome, age, "ACCESSO CONSENTITO")
            st.rerun()
        else:
            salva_azione(nome, age, "ACCESSO NEGATO (MINORENNE)")
            st.error(f"Spiacente {nome}, sei troppo piccolo per queste prelibatezze!")

else:
    # PAGINA DEL NEGOZIO
    st.title(f"🍔 Menu di {st.session_state.nome_utente}")
    st.write(f"Età confermata: {st.session_state.eta_utente} anni")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("I Panini")
        if st.button("Compra Panino Ignorante (5€)"):
            salva_azione(st.session_state.nome_utente, st.session_state.eta_utente, "Comprato Panino Ignorante")
            st.success("Ottima scelta! La panza ringrazia.")
        
        if st.button("Compra 2F Special (8€)"):
            salva_azione(st.session_state.nome_utente, st.session_state.eta_utente, "Comprato 2F Special")
            st.balloons()
            st.success("Hai preso il Re dei panini!")

    with col2:
        st.subheader("Bevande")
        if st.button("Birra Media (4€)"):
            salva_azione(st.session_state.nome_utente, st.session_state.eta_utente, "Comprata Birra")
            st.info("Salute! 🍻")
            
        if st.button("Acqua (1€)"):
            salva_azione(st.session_state.nome_utente, st.session_state.eta_utente, "Comprata Acqua (Errore)")
            st.warning("L'acqua arrugginisce i bulloni, ma ok...")

    st.divider()
    if st.button("Esci e Chiudi Sessione"):
        salva_azione(st.session_state.nome_utente, st.session_state.eta_utente, "LOGOUT")
        st.session_state.autorizzato = False
        st.rerun()

    # Sezione segreta per te (Amministratore)
    with st.expander("Visualizza Registro Accessi (Solo Admin)"):
        if os.path.isfile('registro_accessi.csv'):
            df_log = pd.read_csv('registro_accessi.csv')
            st.dataframe(df_log)
        else:
            st.write("Nessun dato nel registro.")
