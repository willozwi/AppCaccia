import streamlit as st
import sys
import datetime as dt

# Configurazione pagina
st.set_page_config(
    page_title="Gestionale Caccia - Polizia Locale",
    page_icon="🦌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizzato
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f4788;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(90deg, #e8f4f8 0%, #b8dbe4 100%);
        border-radius: 10px;
    }
    .stat-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f4788;
        margin: 0.5rem 0;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1f4788;
    }
    .stat-label {
        font-size: 1rem;
        color: #666;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f4788;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Inizializza sessione
if 'db_initialized' not in st.session_state:
    from database import GestionaleCacciaDB
    # Il database verrà creato nella directory corrente dell'applicazione
    st.session_state.db = GestionaleCacciaDB()
    st.session_state.db_initialized = True

def show_home():
    """Mostra la dashboard principale"""
    st.markdown('<div class="main-header">🦌 Gestionale Caccia - Polizia Locale</div>', unsafe_allow_html=True)
    
    # Debug info (opzionale - commentare in produzione)
    if st.checkbox("🔍 Mostra Info Debug", value=False):
        st.info(f"**Database:** {st.session_state.db.db_path}")
        st.info(f"**Database esiste:** {os.path.exists(st.session_state.db.db_path)}")
    
    # Statistiche generali
    stats = st.session_state.db.get_statistiche_generali()
    anno_corrente = dt.datetime.now().year
    
    st.subheader(f"📊 Dashboard - Anno {anno_corrente}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-value">{stats.get('cacciatori_attivi', 0)}</div>
            <div class="stat-label">Cacciatori Attivi</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-value">{stats.get('libretti_anno_corrente', 0)}</div>
            <div class="stat-label">Libretti {anno_corrente}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-value">{stats.get('fogli_anno_corrente', 0)}</div>
            <div class="stat-label">Fogli Caccia {anno_corrente}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-value">{stats.get('autorizzazioni_in_attesa', 0)}</div>
            <div class="stat-label">Autorizzazioni in Attesa</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Statistiche fogli caccia
    st.subheader(f"📄 Stato Fogli Caccia {anno_corrente}")
    
    stats_fogli = st.session_state.db.get_statistiche_fogli(anno_corrente)
    
    if stats_fogli and stats_fogli.get('totale', 0) > 0:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Totale", stats_fogli.get('totale', 0))
        with col2:
            st.metric("Disponibili", stats_fogli.get('disponibili', 0), 
                     delta_color="off")
        with col3:
            st.metric("Consegnati", stats_fogli.get('consegnati', 0), 
                     delta_color="normal")
        with col4:
            st.metric("Rilasciati", stats_fogli.get('rilasciati', 0), 
                     delta_color="normal")
        with col5:
            st.metric("Restituiti", stats_fogli.get('restituiti', 0), 
                     delta_color="off")
    else:
        st.info(f"Nessun foglio caccia presente per l'anno {anno_corrente}")
    
    st.markdown("---")
    
    # Attività recenti
    st.subheader("📋 Attività Recenti")
    
    log = st.session_state.db.get_log_attivita(20)
    
    if log:
        for entry in log[:10]:  # Mostra solo le ultime 10
            data_ora = entry.get('data_ora', '')
            azione = entry.get('azione', '')
            dettagli = entry.get('dettagli', '')
            
            icon = "✅" if azione == "INSERT" else "✏️" if azione == "UPDATE" else "🗑️"
            st.text(f"{icon} {data_ora} - {dettagli}")
    else:
        st.info("Nessuna attività registrata")
    
    st.markdown("---")
    
    # Informazioni sistema
    st.subheader("ℹ️ Informazioni Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **Gestionale Caccia v1.0**
        
        Sistema per la gestione completa di:
        - Anagrafe cacciatori
        - Libretti regionali per anno
        - Fogli caccia A3 annuali
        - Autorizzazioni RAS
        - Documenti e modulistica
        """)
    
    with col2:
        st.success("""
        **Funzionalità Principali**
        
        ✅ Anagrafe cacciatori completa
        
        ✅ Gestione libretti regionali
        
        ✅ Tracciamento fogli caccia
        
        ✅ Generazione documenti automatica
        
        ✅ Reportistica e statistiche
        """)

def main():
    """Funzione principale"""
    
    # Sidebar con menu di navigazione
    st.sidebar.title("📋 Menu Principale")
    
    menu = st.sidebar.radio(
        "Navigazione",
        [
            "🏠 Dashboard",
            "👥 Anagrafe Cacciatori",
            "📖 Libretti Regionali", 
            "📄 Fogli Caccia A3",
            "📥 Import Fogli Massivo",
            "🔐 Autorizzazioni RAS",
            "📁 Documenti",
            "📊 Report e Statistiche"
        ]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"""
    **Sistema Attivo**
    
    Data: {dt.datetime.now().strftime('%d/%m/%Y')}
    
    Ora: {dt.datetime.now().strftime('%H:%M:%S')}
    """)
    
    # Routing delle pagine
    if menu == "🏠 Dashboard":
        show_home()
    elif menu == "👥 Anagrafe Cacciatori":
        from pages import anagrafe_cacciatori
        anagrafe_cacciatori.show()
    elif menu == "📖 Libretti Regionali":
        from pages import libretti_regionali
        libretti_regionali.show()
    elif menu == "📄 Fogli Caccia A3":
        from pages import fogli_caccia
        fogli_caccia.show()
    elif menu == "📥 Import Fogli Massivo":
        from pages import import_fogli
        import_fogli.show()
    elif menu == "🔐 Autorizzazioni RAS":
        from pages import autorizzazioni_ras
        autorizzazioni_ras.show()
    elif menu == "📁 Documenti":
        from pages import documenti
        documenti.show()
    elif menu == "📊 Report e Statistiche":
        from pages import report_statistiche
        report_statistiche.show()

if __name__ == "__main__":
    main()
