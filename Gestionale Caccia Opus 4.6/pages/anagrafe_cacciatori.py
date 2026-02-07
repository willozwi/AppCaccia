import streamlit as st
import pandas as pd
import datetime as dt

def show():
    """Mostra la pagina anagrafe cacciatori"""
    st.markdown('<div class="main-header">👥 Anagrafe Cacciatori</div>', unsafe_allow_html=True)
    
    # Tabs per diverse funzionalità
    tab1, tab2, tab3 = st.tabs(["📋 Elenco Cacciatori", "➕ Nuovo Cacciatore", "🔍 Ricerca"])
    
    with tab1:
        show_elenco_cacciatori()
    
    with tab2:
        show_form_nuovo_cacciatore()
    
    with tab3:
        show_ricerca_cacciatori()

def show_elenco_cacciatori():
    """Mostra l'elenco completo dei cacciatori"""
    st.subheader("Elenco Cacciatori Attivi")
    
    # Filtri
    col1, col2 = st.columns([3, 1])
    
    with col1:
        mostra_disattivati = st.checkbox("Mostra anche cacciatori disattivati")
    
    with col2:
        if st.button("🔄 Aggiorna", use_container_width=True):
            st.rerun()
    
    # Recupera cacciatori
    cacciatori = st.session_state.db.get_tutti_cacciatori(solo_attivi=not mostra_disattivati)
    
    if cacciatori:
        # Crea DataFrame per visualizzazione
        df_cacciatori = pd.DataFrame(cacciatori)
        
        # Seleziona e riordina colonne per visualizzazione
        cols_display = ['numero_tessera', 'cognome', 'nome', 'codice_fiscale', 
                       'comune', 'cellulare', 'email']
        
        df_display = df_cacciatori[cols_display].copy()
        df_display.columns = ['N. Tessera', 'Cognome', 'Nome', 'Codice Fiscale', 
                             'Comune', 'Cellulare', 'Email']
        
        st.dataframe(
            df_display,
            use_container_width=True,
            height=400
        )
        
        st.metric("Totale cacciatori", len(cacciatori))
        
        # Azioni sui cacciatori
        st.markdown("---")
        st.subheader("Azioni su Cacciatore")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cacciatore_selezionato = st.selectbox(
                "Seleziona cacciatore",
                options=[(c['id'], f"{c['cognome']} {c['nome']} - {c['numero_tessera']}") 
                        for c in cacciatori],
                format_func=lambda x: x[1]
            )
        
        with col2:
            azione = st.selectbox(
                "Azione",
                ["Visualizza Dettagli", "Modifica Dati", "Disattiva Cacciatore"]
            )
        
        if st.button("Esegui Azione", type="primary", use_container_width=True):
            cacciatore_id = cacciatore_selezionato[0]
            
            if azione == "Visualizza Dettagli":
                show_dettagli_cacciatore(cacciatore_id)
            elif azione == "Modifica Dati":
                st.session_state.modifica_cacciatore_id = cacciatore_id
                st.session_state.show_modifica_form = True
                st.rerun()
            elif azione == "Disattiva Cacciatore":
                if st.confirm("Confermi la disattivazione del cacciatore?"):
                    st.session_state.db.elimina_cacciatore(cacciatore_id)
                    st.success("✅ Cacciatore disattivato correttamente")
                    st.rerun()
        
        # Form di modifica (se richiesto)
        if st.session_state.get('show_modifica_form', False):
            st.markdown("---")
            show_form_modifica_cacciatore(st.session_state.modifica_cacciatore_id)
    
    else:
        st.warning("Nessun cacciatore presente nel database")
        st.info("Utilizza la tab 'Nuovo Cacciatore' per aggiungere il primo cacciatore")

def show_dettagli_cacciatore(cacciatore_id: int):
    """Mostra i dettagli completi di un cacciatore"""
    cacciatore = st.session_state.db.get_cacciatore(cacciatore_id)
    
    if cacciatore:
        st.markdown("---")
        st.subheader(f"👤 Dettagli: {cacciatore['cognome']} {cacciatore['nome']}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Dati Anagrafici**")
            st.text(f"N. Tessera: {cacciatore.get('numero_tessera', 'N/D')}")
            st.text(f"Cognome: {cacciatore.get('cognome', 'N/D')}")
            st.text(f"Nome: {cacciatore.get('nome', 'N/D')}")
            st.text(f"Data di Nascita: {cacciatore.get('data_nascita', 'N/D')}")
            st.text(f"Luogo di Nascita: {cacciatore.get('luogo_nascita', 'N/D')}")
            st.text(f"Codice Fiscale: {cacciatore.get('codice_fiscale', 'N/D')}")
        
        with col2:
            st.markdown("**Recapiti**")
            st.text(f"Indirizzo: {cacciatore.get('indirizzo', 'N/D')}")
            st.text(f"Comune: {cacciatore.get('comune', 'N/D')}")
            st.text(f"Provincia: {cacciatore.get('provincia', 'N/D')}")
            st.text(f"CAP: {cacciatore.get('cap', 'N/D')}")
            st.text(f"Telefono: {cacciatore.get('telefono', 'N/D')}")
            st.text(f"Cellulare: {cacciatore.get('cellulare', 'N/D')}")
            st.text(f"Email: {cacciatore.get('email', 'N/D')}")
        
        if cacciatore.get('note'):
            st.markdown("**Note**")
            st.info(cacciatore['note'])
        
        # Libretti associati
        st.markdown("---")
        st.markdown("**📖 Libretti Regionali**")
        libretti = st.session_state.db.get_libretti_cacciatore(cacciatore_id)
        
        if libretti:
            df_libretti = pd.DataFrame(libretti)
            st.dataframe(
                df_libretti[['anno', 'numero_libretto', 'data_rilascio', 'stato']],
                use_container_width=True
            )
        else:
            st.info("Nessun libretto registrato")
        
        # Autorizzazioni RAS
        st.markdown("**🔐 Autorizzazioni RAS**")
        autorizzazioni = st.session_state.db.get_autorizzazioni_cacciatore(cacciatore_id)
        
        if autorizzazioni:
            df_auth = pd.DataFrame(autorizzazioni)
            st.dataframe(
                df_auth[['anno', 'tipo_autorizzazione', 'data_richiesta', 'stato']],
                use_container_width=True
            )
        else:
            st.info("Nessuna autorizzazione registrata")

def show_form_nuovo_cacciatore():
    """Mostra il form per aggiungere un nuovo cacciatore"""
    st.subheader("Inserimento Nuovo Cacciatore")
    
    with st.form("form_nuovo_cacciatore", clear_on_submit=True):
        st.markdown("**Dati Anagrafici**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            numero_tessera = st.text_input("N. Tessera *", placeholder="es. 497424")
            cognome = st.text_input("Cognome *", placeholder="es. Rossi")
            nome = st.text_input("Nome *", placeholder="es. Mario")
            data_nascita = st.date_input("Data di Nascita", value=None, format="DD/MM/YYYY")
        
        with col2:
            luogo_nascita = st.text_input("Luogo di Nascita", placeholder="es. Cagliari")
            codice_fiscale = st.text_input("Codice Fiscale", placeholder="es. RSSMRA80A01B354X")
            telefono = st.text_input("Telefono", placeholder="es. 070123456")
            cellulare = st.text_input("Cellulare", placeholder="es. 3331234567")
        
        st.markdown("**Residenza**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            indirizzo = st.text_input("Indirizzo", placeholder="es. Via Roma 123")
        
        with col2:
            comune = st.text_input("Comune", placeholder="es. Serrenti")
        
        with col3:
            provincia = st.text_input("Provincia", placeholder="es. SU", max_chars=2)
        
        cap = st.text_input("CAP", placeholder="es. 09027", max_chars=5)
        email = st.text_input("Email", placeholder="es. mario.rossi@email.com")
        
        note = st.text_area("Note", placeholder="Note aggiuntive...")
        
        st.markdown("---")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            submitted = st.form_submit_button("💾 Salva Cacciatore", 
                                              type="primary", 
                                              use_container_width=True)
        
        if submitted:
            # Validazione
            if not numero_tessera or not cognome or not nome:
                st.error("⚠️ I campi contrassegnati con * sono obbligatori")
            else:
                try:
                    dati = {
                        'numero_tessera': numero_tessera.strip(),
                        'cognome': cognome.strip().upper(),
                        'nome': nome.strip().title(),
                        'data_nascita': data_nascita.strftime('%Y-%m-%d') if data_nascita else None,
                        'luogo_nascita': luogo_nascita.strip() if luogo_nascita else None,
                        'codice_fiscale': codice_fiscale.strip().upper() if codice_fiscale else None,
                        'indirizzo': indirizzo.strip() if indirizzo else None,
                        'comune': comune.strip() if comune else None,
                        'provincia': provincia.strip().upper() if provincia else None,
                        'cap': cap.strip() if cap else None,
                        'telefono': telefono.strip() if telefono else None,
                        'cellulare': cellulare.strip() if cellulare else None,
                        'email': email.strip().lower() if email else None,
                        'note': note.strip() if note else None
                    }
                    
                    cacciatore_id = st.session_state.db.aggiungi_cacciatore(dati)
                    
                    st.success(f"✅ Cacciatore aggiunto correttamente! ID: {cacciatore_id}")
                    st.balloons()
                    
                except Exception as e:
                    if "UNIQUE constraint failed" in str(e):
                        st.error("⚠️ Numero tessera o codice fiscale già esistente!")
                    else:
                        st.error(f"⚠️ Errore durante il salvataggio: {str(e)}")

def show_form_modifica_cacciatore(cacciatore_id: int):
    """Mostra il form per modificare un cacciatore esistente"""
    cacciatore = st.session_state.db.get_cacciatore(cacciatore_id)
    
    if not cacciatore:
        st.error("Cacciatore non trovato")
        return
    
    st.subheader(f"Modifica Dati: {cacciatore['cognome']} {cacciatore['nome']}")
    
    with st.form("form_modifica_cacciatore"):
        st.markdown("**Dati Anagrafici**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            numero_tessera = st.text_input("N. Tessera *", value=cacciatore.get('numero_tessera', ''))
            cognome = st.text_input("Cognome *", value=cacciatore.get('cognome', ''))
            nome = st.text_input("Nome *", value=cacciatore.get('nome', ''))
            
            # Gestione data nascita
            data_nascita_str = cacciatore.get('data_nascita')
            data_nascita_val = dt.datetime.strptime(data_nascita_str, '%Y-%m-%d').date() if data_nascita_str else None
            data_nascita = st.date_input("Data di Nascita", value=data_nascita_val, format="DD/MM/YYYY")
        
        with col2:
            luogo_nascita = st.text_input("Luogo di Nascita", value=cacciatore.get('luogo_nascita', ''))
            codice_fiscale = st.text_input("Codice Fiscale", value=cacciatore.get('codice_fiscale', ''))
            telefono = st.text_input("Telefono", value=cacciatore.get('telefono', ''))
            cellulare = st.text_input("Cellulare", value=cacciatore.get('cellulare', ''))
        
        st.markdown("**Residenza**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            indirizzo = st.text_input("Indirizzo", value=cacciatore.get('indirizzo', ''))
        
        with col2:
            comune = st.text_input("Comune", value=cacciatore.get('comune', ''))
        
        with col3:
            provincia = st.text_input("Provincia", value=cacciatore.get('provincia', ''), max_chars=2)
        
        cap = st.text_input("CAP", value=cacciatore.get('cap', ''), max_chars=5)
        email = st.text_input("Email", value=cacciatore.get('email', ''))
        
        note = st.text_area("Note", value=cacciatore.get('note', ''))
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col2:
            annulla = st.form_submit_button("❌ Annulla", use_container_width=True)
        
        with col3:
            submitted = st.form_submit_button("💾 Salva Modifiche", 
                                              type="primary", 
                                              use_container_width=True)
        
        if annulla:
            st.session_state.show_modifica_form = False
            st.rerun()
        
        if submitted:
            if not numero_tessera or not cognome or not nome:
                st.error("⚠️ I campi contrassegnati con * sono obbligatori")
            else:
                try:
                    dati = {
                        'numero_tessera': numero_tessera.strip(),
                        'cognome': cognome.strip().upper(),
                        'nome': nome.strip().title(),
                        'data_nascita': data_nascita.strftime('%Y-%m-%d') if data_nascita else None,
                        'luogo_nascita': luogo_nascita.strip() if luogo_nascita else None,
                        'codice_fiscale': codice_fiscale.strip().upper() if codice_fiscale else None,
                        'indirizzo': indirizzo.strip() if indirizzo else None,
                        'comune': comune.strip() if comune else None,
                        'provincia': provincia.strip().upper() if provincia else None,
                        'cap': cap.strip() if cap else None,
                        'telefono': telefono.strip() if telefono else None,
                        'cellulare': cellulare.strip() if cellulare else None,
                        'email': email.strip().lower() if email else None,
                        'note': note.strip() if note else None
                    }
                    
                    st.session_state.db.modifica_cacciatore(cacciatore_id, dati)
                    
                    st.success("✅ Dati aggiornati correttamente!")
                    st.session_state.show_modifica_form = False
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"⚠️ Errore durante l'aggiornamento: {str(e)}")

def show_ricerca_cacciatori():
    """Mostra la funzionalità di ricerca cacciatori"""
    st.subheader("Ricerca Cacciatori")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        termine_ricerca = st.text_input(
            "Cerca per nome, cognome, numero tessera o codice fiscale",
            placeholder="Inserisci termine di ricerca..."
        )
    
    with col2:
        cerca = st.button("🔍 Cerca", type="primary", use_container_width=True)
    
    if termine_ricerca and (cerca or len(termine_ricerca) >= 3):
        risultati = st.session_state.db.cerca_cacciatori(termine_ricerca)
        
        if risultati:
            st.success(f"✅ Trovati {len(risultati)} risultati")
            
            # Mostra risultati
            for cacciatore in risultati:
                with st.expander(
                    f"👤 {cacciatore['cognome']} {cacciatore['nome']} - "
                    f"Tessera: {cacciatore['numero_tessera']}"
                ):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.text(f"Codice Fiscale: {cacciatore.get('codice_fiscale', 'N/D')}")
                        st.text(f"Data Nascita: {cacciatore.get('data_nascita', 'N/D')}")
                        st.text(f"Comune: {cacciatore.get('comune', 'N/D')}")
                    
                    with col2:
                        st.text(f"Telefono: {cacciatore.get('telefono', 'N/D')}")
                        st.text(f"Cellulare: {cacciatore.get('cellulare', 'N/D')}")
                        st.text(f"Email: {cacciatore.get('email', 'N/D')}")
                    
                    if st.button(f"Visualizza Dettagli Completi", 
                               key=f"dettagli_{cacciatore['id']}"):
                        show_dettagli_cacciatore(cacciatore['id'])
        else:
            st.warning("Nessun risultato trovato")
    elif termine_ricerca:
        st.info("Inserisci almeno 3 caratteri per avviare la ricerca")
