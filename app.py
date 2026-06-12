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
    try:
        corsi_testo = []
        with open('database_unito_arricchito.csv', 'r', encoding='latin-1') as f:
            prima_riga = f.readline()
            # Capisce da solo se usare la virgola o il punto e virgola
            separatore = ';' if ';' in prima_riga else ','
            f.seek(0)
            
            lettore = csv.DictReader(f, delimiter=separatore)
            for riga in lettore:
                # Estrae i dati al sicuro da eventuali errori di battitura nelle colonne
                ateneo = riga.get('Università', riga.get('Universita', 'Ateneo Sconosciuto'))
                nome = riga.get('Nome Corso', 'Corso Sconosciuto')
                info = riga.get('Descrizione per IA', 'Nessuna info')
                link = riga.get('Link', 'Nessun link')
                
                corsi_testo.append(f"- ATENEO: {ateneo} | CORSO: {nome} | INFO: {info} | LINK: {link}")
                
        return "\n".join(corsi_testo)
        
    except Exception as e:
        # Se qualcosa va storto, blocca tutto e ci fa vedere l'errore esatto a schermo
        st.error(f"🚨 ALLARME ROSSO DATABASE: {e}")
        st.stop()

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
            Hai a disposizione ESCLUSIVAMENTE il seguente database ufficiale dei corsi:
            {libro_di_testo}
            
            Il tuo compito:
            1. Leggi la richiesta dello studente.
            2. Trova i 2 o 3 corsi più adatti a lui nel database.
            3. Spiega in modo incoraggiante perché li hai scelti.
            4. Scrivi SEMPRE in grassetto il nome dell'Università che eroga il corso (es. **Università di Torino** o **Politecnico di Torino**).
            5. Fornisci sempre il Link ufficiale alla fine.
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