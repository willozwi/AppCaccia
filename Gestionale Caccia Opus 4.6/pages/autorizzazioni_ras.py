import streamlit as st
import pandas as pd
import datetime as dt

def show():
    """Mostra la pagina autorizzazioni RAS"""
    st.markdown('<div class="main-header">🔐 Autorizzazioni RAS</div>', unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2 = st.tabs(["📋 Elenco Autorizzazioni", "➕ Nuova Richiesta"])
    
    with tab1:
        show_elenco_autorizzazioni()
    
    with tab2:
        show_form_nuova_autorizzazione()

def show_elenco_autorizzazioni():
    """Mostra l'elenco delle autorizzazioni"""
    st.subheader("Elenco Autorizzazioni RAS")
    
    # Filtri
    col1, col2, col3 = st.columns(3)
    
    with col1:
        anno_corrente = dt.datetime.now().year
        anni_disponibili = list(range(anno_corrente - 3, anno_corrente + 2))
        anno_selezionato = st.selectbox(
            "Anno",
            options=anni_disponibili,
            index=anni_disponibili.index(anno_corrente)
        )
    
    with col2:
        filtro_stato = st.selectbox(
            "Stato",
            options=['Tutti', 'IN_ATTESA', 'APPROVATO', 'RIFIUTATO', 'IN_LAVORAZIONE']
        )
    
    with col3:
        if st.button("🔄 Aggiorna", use_container_width=True):
            st.rerun()
    
    # Recupera tutte le autorizzazioni
    conn = None
    try:
        conn = st.session_state.db.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT a.*, c.cognome, c.nome, c.numero_tessera
            FROM autorizzazioni_ras a
            JOIN cacciatori c ON a.cacciatore_id = c.id
            WHERE a.anno = ?
        """
        params = [anno_selezionato]

        if filtro_stato != 'Tutti':
            query += " AND a.stato = ?"
            params.append(filtro_stato)

        query += " ORDER BY a.data_richiesta DESC"

        cursor.execute(query, params)
        autorizzazioni = [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        st.error(f"Errore nel recupero autorizzazioni: {str(e)}")
        autorizzazioni = []
    finally:
        if conn:
            conn.close()
    
    if autorizzazioni:
        st.success(f"🔐 Trovate {len(autorizzazioni)} autorizzazioni per l'anno {anno_selezionato}")
        
        # Statistiche rapide
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            in_attesa = len([a for a in autorizzazioni if a.get('stato') == 'IN_ATTESA'])
            st.metric("In Attesa", in_attesa, delta_color="off")
        
        with col2:
            in_lavorazione = len([a for a in autorizzazioni if a.get('stato') == 'IN_LAVORAZIONE'])
            st.metric("In Lavorazione", in_lavorazione, delta_color="normal")
        
        with col3:
            approvate = len([a for a in autorizzazioni if a.get('stato') == 'APPROVATO'])
            st.metric("Approvate", approvate, delta_color="normal")
        
        with col4:
            rifiutate = len([a for a in autorizzazioni if a.get('stato') == 'RIFIUTATO'])
            st.metric("Rifiutate", rifiutate, delta_color="inverse")
        
        st.markdown("---")
        
        # Tabella autorizzazioni
        df_auth = pd.DataFrame(autorizzazioni)
        
        cols_display = ['cognome', 'nome', 'numero_tessera', 'tipo_autorizzazione',
                       'data_richiesta', 'numero_protocollo', 'stato']
        
        df_display = df_auth[[col for col in cols_display if col in df_auth.columns]].copy()
        df_display.columns = ['Cognome', 'Nome', 'N. Tessera', 'Tipo',
                             'Data Richiesta', 'N. Protocollo', 'Stato']
        
        # Colora in base allo stato
        def highlight_stato(row):
            stato = row['Stato']
            if stato == 'IN_ATTESA':
                return ['background-color: #fff3cd'] * len(row)
            elif stato == 'IN_LAVORAZIONE':
                return ['background-color: #cce5ff'] * len(row)
            elif stato == 'APPROVATO':
                return ['background-color: #d4edda'] * len(row)
            elif stato == 'RIFIUTATO':
                return ['background-color: #f8d7da'] * len(row)
            else:
                return [''] * len(row)
        
        st.dataframe(
            df_display.style.apply(highlight_stato, axis=1),
            use_container_width=True,
            height=400
        )
        
        # Dettagli autorizzazione selezionata
        st.markdown("---")
        st.subheader("Dettagli Autorizzazione")
        
        autorizzazione_selezionata = st.selectbox(
            "Seleziona autorizzazione",
            options=[(a['id'], f"{a['cognome']} {a['nome']} - {a.get('tipo_autorizzazione', 'N/D')} - {a.get('data_richiesta', 'N/D')}") 
                    for a in autorizzazioni],
            format_func=lambda x: x[1]
        )
        
        if autorizzazione_selezionata:
            auth = next((a for a in autorizzazioni if a['id'] == autorizzazione_selezionata[0]), None)
            
            if auth:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Dati Cacciatore**")
                    st.text(f"Nome: {auth.get('cognome')} {auth.get('nome')}")
                    st.text(f"N. Tessera: {auth.get('numero_tessera')}")
                    
                    st.markdown("**Dati Autorizzazione**")
                    st.text(f"Tipo: {auth.get('tipo_autorizzazione', 'N/D')}")
                    st.text(f"Anno: {auth.get('anno')}")
                    st.text(f"Data Richiesta: {auth.get('data_richiesta', 'N/D')}")
                
                with col2:
                    st.markdown("**Stato Pratica**")
                    st.text(f"Stato: {auth.get('stato')}")
                    st.text(f"N. Protocollo: {auth.get('numero_protocollo', 'N/D')}")
                    st.text(f"Data Rilascio: {auth.get('data_rilascio', 'N/D')}")
                    st.text(f"Data Scadenza: {auth.get('data_scadenza', 'N/D')}")
                
                if auth.get('note'):
                    st.markdown("**Note**")
                    st.info(auth['note'])
                
                # Form per aggiornare stato
                st.markdown("---")
                st.markdown("**Aggiorna Stato Autorizzazione**")
                
                with st.form(f"form_update_auth_{auth['id']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        nuovo_stato = st.selectbox(
                            "Nuovo Stato",
                            options=['IN_ATTESA', 'IN_LAVORAZIONE', 'APPROVATO', 'RIFIUTATO'],
                            index=['IN_ATTESA', 'IN_LAVORAZIONE', 'APPROVATO', 'RIFIUTATO'].index(auth.get('stato', 'IN_ATTESA'))
                        )
                        
                        numero_protocollo = st.text_input(
                            "N. Protocollo",
                            value=auth.get('numero_protocollo', '')
                        )
                    
                    with col2:
                        data_rilascio = None
                        if auth.get('data_rilascio'):
                            try:
                                data_rilascio = dt.datetime.strptime(auth['data_rilascio'], '%Y-%m-%d').date()
                            except:
                                pass
                        
                        data_rilascio = st.date_input(
                            "Data Rilascio",
                            value=data_rilascio,
                            format="DD/MM/YYYY"
                        )
                        
                        data_scadenza = None
                        if auth.get('data_scadenza'):
                            try:
                                data_scadenza = dt.datetime.strptime(auth['data_scadenza'], '%Y-%m-%d').date()
                            except:
                                pass
                        
                        data_scadenza = st.date_input(
                            "Data Scadenza",
                            value=data_scadenza,
                            format="DD/MM/YYYY"
                        )
                    
                    note = st.text_area("Note", value=auth.get('note', ''))
                    
                    submitted = st.form_submit_button("💾 Aggiorna", 
                                                      type="primary", 
                                                      use_container_width=True)
                    
                    if submitted:
                        conn = None
                        try:
                            conn = st.session_state.db.get_connection()
                            cursor = conn.cursor()

                            cursor.execute("""
                                UPDATE autorizzazioni_ras SET
                                    stato = ?,
                                    numero_protocollo = ?,
                                    data_rilascio = ?,
                                    data_scadenza = ?,
                                    note = ?,
                                    data_modifica = CURRENT_TIMESTAMP
                                WHERE id = ?
                            """, (
                                nuovo_stato,
                                numero_protocollo if numero_protocollo else None,
                                data_rilascio.strftime('%Y-%m-%d') if data_rilascio else None,
                                data_scadenza.strftime('%Y-%m-%d') if data_scadenza else None,
                                note if note else None,
                                auth['id']
                            ))

                            conn.commit()

                            # Log attivita (non bloccante)
                            try:
                                st.session_state.db.log_attivita(
                                    'SISTEMA', 'UPDATE', 'autorizzazioni_ras',
                                    auth['id'], f"Stato: {nuovo_stato}")
                            except Exception:
                                pass

                            st.success("Autorizzazione aggiornata!")
                            st.rerun()

                        except Exception as e:
                            if conn:
                                conn.rollback()
                            st.error(f"Errore: {str(e)}")
                        finally:
                            if conn:
                                conn.close()
    
    else:
        st.warning(f"Nessuna autorizzazione presente per l'anno {anno_selezionato}")
        st.info("Utilizza la tab 'Nuova Richiesta' per aggiungere autorizzazioni")

def show_form_nuova_autorizzazione():
    """Form per nuova richiesta di autorizzazione"""
    st.subheader("Nuova Richiesta Autorizzazione RAS")
    
    st.info("Registra una nuova richiesta di autorizzazione alla RAS")
    
    # Recupera cacciatori
    cacciatori = st.session_state.db.get_tutti_cacciatori(solo_attivi=True)
    
    if not cacciatori:
        st.error("⚠️ Nessun cacciatore attivo nel database!")
        st.info("Aggiungi prima dei cacciatori nella sezione 'Anagrafe Cacciatori'")
        return
    
    with st.form("form_nuova_autorizzazione", clear_on_submit=True):
        st.markdown("**Dati Richiesta**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Selezione cacciatore
            cacciatore_selezionato = st.selectbox(
                "Cacciatore *",
                options=[(c['id'], f"{c['cognome']} {c['nome']} - {c['numero_tessera']}") 
                        for c in cacciatori],
                format_func=lambda x: x[1]
            )
            
            anno = st.number_input(
                "Anno *",
                min_value=2020,
                max_value=dt.datetime.now().year + 1,
                value=dt.datetime.now().year,
                step=1
            )
            
            tipo_autorizzazione = st.selectbox(
                "Tipo Autorizzazione *",
                options=[
                    'Licenza di Caccia',
                    'Autorizzazione Regionale',
                    'Permesso Speciale',
                    'Rinnovo Licenza',
                    'Altro'
                ]
            )
        
        with col2:
            data_richiesta = st.date_input(
                "Data Richiesta *",
                value=dt.datetime.now().date(),
                format="DD/MM/YYYY"
            )
            
            numero_protocollo = st.text_input(
                "N. Protocollo",
                placeholder="es. PROT-2025-001"
            )
            
            stato = st.selectbox(
                "Stato Iniziale",
                options=['IN_ATTESA', 'IN_LAVORAZIONE'],
                index=0
            )
        
        note = st.text_area("Note", placeholder="Note sulla richiesta...")
        
        st.markdown("---")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            submitted = st.form_submit_button("💾 Salva Richiesta", 
                                              type="primary", 
                                              use_container_width=True)
        
        if submitted:
            try:
                dati = {
                    'cacciatore_id': cacciatore_selezionato[0],
                    'anno': anno,
                    'tipo_autorizzazione': tipo_autorizzazione,
                    'numero_protocollo': numero_protocollo.strip() if numero_protocollo else None,
                    'data_richiesta': data_richiesta.strftime('%Y-%m-%d'),
                    'data_rilascio': None,
                    'data_scadenza': None,
                    'stato': stato,
                    'note': note.strip() if note else None,
                    'file_path': None
                }
                
                auth_id = st.session_state.db.aggiungi_autorizzazione(dati)
                
                st.success(f"✅ Richiesta autorizzazione registrata! ID: {auth_id}")
                st.balloons()
                
            except Exception as e:
                st.error(f"⚠️ Errore durante il salvataggio: {str(e)}")
