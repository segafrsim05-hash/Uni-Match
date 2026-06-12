import streamlit as st
import csv
import google.generativeai as genai

# 1. IMPOSTAZIONI GRAFICHE DELLA PAGINA
st.set_page_config(page_title="Il Tuo Orientatore IA", page_icon="🎓", layout="centered")

# INSERISCI QUI LA TUA CHIAVE SEGRETA DI GOOGLE!
CHIAVE_API = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=CHIAVE_API)

# 2. FUNZIONE PER CARICARE IL DATABASE IN MODO EFFICIENTE
@st.cache_data # Questo trucco fa sì che il sito non ricarichi l'Excel ogni volta che clicchi un bottone
def carica_database():
    corsi_testo = []
    try:
        with open("database_unito_arricchito.csv", mode='r', encoding='utf-8') as f:
            lettore = csv.DictReader(f)
            for riga in lettore:
                corsi_testo.append(f"- CORSO: {riga['Nome Corso']} | INFO: {riga['Descrizione per IA']} | LINK: {riga['Link']}")
        return "\n".join(corsi_testo)
    except Exception as e:
        return f"Errore nel caricamento dati: {e}"

libro_di_testo = carica_database()

# 3. LA CARROZZERIA DEL SITO (IL TESTO E I BOTTONI)
st.title("🎓 Trova la tua strada")
st.write("Non sai cosa studiare all'Università di Torino? Racconta all'Intelligenza Artificiale cosa ti appassiona, le tue materie preferite o il lavoro dei tuoi sogni. Penserà lei a trovare il corso perfetto per te.")

st.markdown("---") # Crea una linea divisoria elegante

# La barra di ricerca dove l'utente scrive
domanda_studente = st.text_area("Cosa ti piace fare?", placeholder="Es: Mi piace l'informatica ma anche il mondo della salute...")

# Il bottone per avviare la ricerca
if st.button("Cerca il mio Corso Ideale 🚀"):
    if domanda_studente:
        # Mostra una rotellina di caricamento mentre l'IA pensa
        with st.spinner('Sto analizzando 175 corsi di laurea...'):
            
            istruzioni_per_ia = f"""
            Sei un orientatore universitario amichevole e super esperto.
            Hai a disposizione ESCLUSIVAMENTE il seguente database ufficiale dei corsi dell'Università di Torino:
            {libro_di_testo}
            
            Il tuo compito:
            1. Leggi la richiesta dello studente.
            2. Trova i 2 o 3 corsi più adatti a lui nel database.
            3. Spiega in modo incoraggiante perché li hai scelti.
            4. Fornisci sempre il Link ufficiale alla fine.
            """
            
            try:
                modello = genai.GenerativeModel(
                    model_name="gemini-2.5-flash",
                    system_instruction=istruzioni_per_ia
                )
                risposta = modello.generate_content(domanda_studente)
                
                # Mostra la risposta in un box verde di successo
                st.success("Trovati! Ecco i percorsi migliori per te:")
                st.write(risposta.text)
                
            except Exception as errore:
                st.error(f"C'è stato un problema di connessione: {errore}")
    else:
        # Se l'utente clicca il bottone senza aver scritto nulla
        st.warning("Per favore, scrivi qualcosa prima di cercare!")