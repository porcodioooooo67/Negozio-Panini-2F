import streamlit as st

# Configurazione pagina
st.set_page_config(page_title="Negozio Panini 2F", page_icon="🍔")

# Inizializziamo lo stato dell'app (se non esiste già)
if 'autorizzato' not in st.session_state:
    st.session_state.autorizzato = False

# --- PAGINA 1: VERIFICA ETÀ ---
if not st.session_state.autorizzato:
    st.title("Negozio panini 2F 🍔")
    st.header("Compra Panini che un po' di panza non fa mai male")

    nome = st.text_input("Inserisci il tuo nome")
    # Usiamo number_input per evitare errori se l'utente scrive lettere invece di numeri
    age = st.number_input("Inserisci la tua età", min_value=0, max_value=120, value=0)

    if st.button("Entra nel negozio"):
        if age >= 18:
            st.session_state.autorizzato = True
            st.session_state.nome_utente = nome
            st.rerun() # Ricarica l'app per passare alla pagina 2
        else:
            st.error(f"Ciao {nome}, hai solo {age} anni. Qui ci sono cose un po' bruttine per te!")

# --- PAGINA 2: IL NEGOZIO ---
else:
    st.title(f"Benvenuto nel reparto Pro, {st.session_state.nome_utente}! 🚀")
    st.subheader("Ecco il nostro menu esclusivo:")
    
    # Usiamo le colonne per rendere l'interfaccia "avanzata"
    col1, col2 = st.columns(2)

    with col1:
        st.write("### 🥪 Panini Classici")
        st.write("- **Panino ignorante**: 5.00€")
        st.write("- **Salamella Deluxe**: 6.50€")
        st.write("- **Il 2F Special**: 8.00€")

    with col2:
        st.write("### 🥤 Bibite")
        st.write("- **Birra Artigianale**: 4.00€")
        st.write("- **Vino della casa**: 3.50€")
        st.write("- **Acqua (per chi sbaglia)**: 1.00€")

    st.divider()
    
    if st.button("Torna alla Home / Esci"):
        st.session_state.autorizzato = False
        st.rerun()