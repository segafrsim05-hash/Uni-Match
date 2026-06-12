import streamlit as st
import csv
import google.generativeai as genai
# --- INIEZIONE DI DESIGN PREMIUM (CSS Custom) ---
st.markdown("""
    <style>
    /* Nasconde il menu in alto a destra e la scritta "Made with Streamlit" in basso */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Rende il bottone di ricerca enorme, colorato e cliccabile */
    .stButton>button {
        background-color: #2e6bc6; /* Blu Tech Elegante */
        color: white !important;
        border-radius: 10px;
        height: 50px;
        width: 100%;
        font-size: 18px;
        font-weight: bold;
        transition: 0.3s;
    }
    
    /* Effetto quando passi sopra il bottone col mouse */
    .stButton>button:hover {
        background-color: #1a4a90;
        border-color: #1a4a90;
    }
    
    /* Colora lo sfondo della barra laterale e FORZA il testo scuro (Anti-Dark Mode) */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e0e0e0;
    }
    [data-testid="stSidebar"] * {
        color: #1a1a1a !important; /* Costringe tutte le scritte della sidebar a essere nere */
    }
    </style>
""", unsafe_allow_html=True)
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
        # Aggiunto newline='' (trucco tecnico per leggere perfettamente i CSV del Mac)
        with open('database_unito_arricchito.csv', 'r', encoding='latin-1', newline='') as f:
            prima_riga = f.readline()
            separatore = ';' if ';' in prima_riga else ','
            f.seek(0)
            
            lettore = csv.DictReader(f, delimiter=separatore)
            
            for riga in lettore:
                # SPAZZANEVE: prende tutte le chiavi, le mette in minuscolo e toglie gli spazi invisibili!
                riga_pulita = {str(k).strip().lower(): str(v).strip() for k, v in riga.items() if k is not None}
                
                ateneo = riga_pulita.get('università', riga_pulita.get('universita', 'Ateneo Sconosciuto'))
                nome = riga_pulita.get('nome corso', 'Corso Sconosciuto')
                info = riga_pulita.get('descrizione per ia', 'Nessuna info')
                link = riga_pulita.get('link', 'Nessun link')
                
                corsi_testo.append(f"- ATENEO: {ateneo} | CORSO: {nome} | INFO: {info} | LINK: {link}")
                
        # LA TRAPPOLA: se il primo corso non viene letto bene, fermiamo tutto e stampiamo le VERE colonne
        if corsi_testo and "Corso Sconosciuto" in corsi_testo[0]:
            st.error(f"🚨 COLONNE NON RICONOSCIUTE! Excel le ha salvate così: {list(riga.keys())}")
            st.stop()
            
        return "\n".join(corsi_testo)
        
    except Exception as e:
        st.error(f"🚨 ALLARME ROSSO DATABASE: {e}")
        st.stop()

libro_di_testo = carica_database()

# 3. LA CARROZZERIA DEL SITO (IL TESTO E I BOTTONI)
st.title("🎓 Uni-Match")
st.subheader("Trova la tua università ideale a Torino con l'Intelligenza Artificiale")
st.write("Inserisci le tue passioni, i tuoi hobby o cosa ti piacerebbe fare da grande. La nostra IA analizzerà i database ufficiali di **UniTo** e **PoliTo** per trovare il percorso perfetto per te.")


with st.sidebar:
    st.header("⚡ Info Progetto")
    st.write("Uni-Match è un orientatore smart basato su algoritmi RAG e Google Gemini.")
    st.write("🔹 **Atenei scansionati:** 2 (UniTo & PoliTo)")
    st.write("🔹 **Corsi in archivio:** +190")
    st.markdown("---")
    st.caption("Creato con ❤️ dal Team di Uni-Match")
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
                st.info(risposta.text)                
            except Exception as errore:
                st.error(f"C'è stato un problema di connessione: {errore}")
    else:
        # Se l'utente clicca il bottone senza aver scritto nulla
        st.warning("Per favore, scrivi qualcosa prima di cercare!")