```python
import streamlit as st
import pandas as pd
import datetime as dt
import os

def show():
    """Mostra la pagina documenti"""
    st.markdown('<div class="main-header">📁 Documenti e Modulistica</div>', unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📄 Modulistica Standard", "📎 Upload Documenti", "📋 Archivio Documenti"])
    
    with tab1:
        show_modulistica_standard()
    
    with tab2:
        show_upload_documenti()
    
    with tab3:
        show_archivio_documenti()

def show_modulistica_standard():
    """Mostra e genera la modulistica standard"""
    st.subheader("Modulistica Standard")
    
    st.info("Moduli e documenti standard per la gestione della caccia")
    
    # Categorie di documenti
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Moduli per Cacciatori")
        
        moduli_cacciatori = [
            {
                'nome': 'Modulo Istanza Rilascio Autorizzazione',
                'descrizione': 'Richiesta autorizzazione regionale per esercizio caccia',
                'tipo': 'DOCX'
            },
            {
                'nome': 'Consegna Foglio Venatorio',
                'descrizione': 'Modulo per consegna foglio venatorio annuale',
                'tipo': 'DOCX'
            },
            {
                'nome': 'Richiesta Rinnovo Licenza',
                'descrizione': 'Modulo per rinnovo licenza di caccia',
                'tipo': 'DOCX'
            }
        ]
        
        for modulo in moduli_cacciatori:
            with st.expander(f"📄 {modulo['nome']}"):
                st.text(f"Tipo: {modulo['tipo']}")
                st.text(f"Descrizione: {modulo['descrizione']}")
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    if st.button(f"📥 Scarica Template", key=f"download_{modulo['nome']}"):
                        st.info("Funzione di download template in sviluppo")
                
                with col_b:
                    if st.button(f"✏️ Compila Modulo", key=f"compile_{modulo['nome']}"):
                        st.info("Funzione di compilazione modulo in sviluppo")
    
    with col2:
        st.markdown("### 📊 Documenti Amministrativi")
        
        moduli_admin = [
            {
                'nome': 'Registro Consegne Fogli',
                'descrizione': 'Registro delle consegne fogli da Ilbaa',
                'tipo': 'XLSX'
            },
            {
                'nome': 'Elenco Libretti Rilasciati',
                'descrizione': 'Elenco completo libretti regionali rilasciati',
                'tipo': 'XLSX'
            },
            {
                'nome': 'Trasmissione Database Anagrafe',
                'descrizione': 'Esportazione per trasmissione alla RAS',
                'tipo': 'XLSX'
            }
        ]
        
        for modulo in moduli_admin:
            with st.expander(f"📊 {modulo['nome']}"):
                st.text(f"Tipo: {modulo['tipo']}")
                st.text(f"Descrizione: {modulo['descrizione']}")
                
                if st.button(f"📥 Genera Documento", key=f"generate_{modulo['nome']}", 
                           use_container_width=True):
                    genera_documento_amministrativo(modulo['nome'])
    
    # Copertine e fac-simile
    st.markdown("---")
    st.markdown("### 📋 Fac-Simile e Copertine")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Genera Copertina Libretto", use_container_width=True):
            st.info("Generazione copertina libretto in sviluppo")
    
    with col2:
        if st.button("📄 Genera Foglio Caccia Vuoto", use_container_width=True):
            st.info("Generazione foglio caccia in sviluppo")

def genera_documento_amministrativo(tipo_documento: str):
    """Genera un documento amministrativo"""
    anno_corrente = dt.datetime.now().year
    
    if tipo_documento == "Registro Consegne Fogli":
        # Genera registro consegne
        fogli = st.session_state.db.get_fogli_anno(anno_corrente, 'CONSEGNATO')
        
        if fogli:
            df = pd.DataFrame(fogli)
            df_export = df[['numero_foglio', 'data_consegna', 'consegnato_da', 'note']].copy()
            df_export.columns = ['Numero Foglio', 'Data Consegna', 'Consegnato Da', 'Note']
            
            csv = df_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Scarica Registro Consegne CSV",
                data=csv,
                file_name=f"registro_consegne_{anno_corrente}.csv",
                mime="text/csv"
            )
        else:
            st.warning("Nessun foglio consegnato da esportare")
    
    elif tipo_documento == "Elenco Libretti Rilasciati":
        # Genera elenco libretti
        libretti = st.session_state.db.get_libretti_anno(anno_corrente)
        
        if libretti:
            df = pd.DataFrame(libretti)
            df_export = df[['numero_libretto', 'cognome', 'nome', 'numero_tessera', 
                          'data_rilascio', 'data_scadenza', 'stato']].copy()
            df_export.columns = ['N. Libretto', 'Cognome', 'Nome', 'N. Tessera',
                               'Data Rilascio', 'Data Scadenza', 'Stato']
            
            csv = df_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Scarica Elenco Libretti CSV",
                data=csv,
                file_name=f"elenco_libretti_{anno_corrente}.csv",
                mime="text/csv"
            )
        else:
            st.warning("Nessun libretto da esportare")
    
    elif tipo_documento == "Trasmissione Database Anagrafe":
        # Genera database anagrafe
        cacciatori = st.session_state.db.get_tutti_cacciatori(solo_attivi=True)
        
        if cacciatori:
            df = pd.DataFrame(cacciatori)
            df_export = df[['numero_tessera', 'cognome', 'nome', 'codice_fiscale',
                          'data_nascita', 'comune', 'provincia', 'cellulare']].copy()
            df_export.columns = ['N. Tessera', 'Cognome', 'Nome', 'Codice Fiscale',
                               'Data Nascita', 'Comune', 'Provincia', 'Cellulare']
            
            csv = df_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Scarica Anagrafe CSV",
                data=csv,
                file_name=f"anagrafe_cacciatori_{anno_corrente}.csv",
                mime="text/csv"
            )
        else:
            st.warning("Nessun cacciatore da esportare")

def show_upload_documenti():
    """Form per upload documenti"""
    st.subheader("Upload Documenti")
    
    st.info("Carica documenti relativi ai cacciatori (licenze, certificati, ecc.)")
    
    # Recupera cacciatori
    cacciatori = st.session_state.db.get_tutti_cacciatori(solo_attivi=True)
    
    if not cacciatori:
        st.error("⚠️ Nessun cacciatore attivo nel database!")
        return
    
    with st.form("form_upload_documento"):
        st.markdown("**Informazioni Documento**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Selezione cacciatore (opzionale)
            usa_cacciatore = st.checkbox("Associa a un cacciatore specifico")
            
            cacciatore_selezionato = None
            if usa_cacciatore:
                cacciatore_selezionato = st.selectbox(
                    "Cacciatore",
                    options=[(c['id'], f"{c['cognome']} {c['nome']} - {c['numero_tessera']}") 
                            for c in cacciatori],
                    format_func=lambda x: x[1]
                )
            
            tipo_documento = st.selectbox(
                "Tipo Documento *",
                options=[
                    'Licenza di Caccia',
                    'Libretto Regionale',
                    'Foglio Caccia',
                    'Autorizzazione RAS',
                    'Certificato Medico',
                    'Documento Identità',
                    'Ricevuta Pagamento',
                    'Altro'
                ]
            )
        
        with col2:
            anno = st.number_input(
                "Anno di Riferimento",
                min_value=2015,
                max_value=dt.datetime.now().year + 1,
                value=dt.datetime.now().year,
                step=1
            )
            
            data_documento = st.date_input(
                "Data Documento",
                value=dt.datetime.now().date(),
                format="DD/MM/YYYY"
            )
        
        descrizione = st.text_area(
            "Descrizione",
            placeholder="Descrizione del documento..."
        )
        
        # Upload file
        uploaded_file = st.file_uploader(
            "Seleziona File",
            type=['pdf', 'docx', 'xlsx', 'jpg', 'jpeg', 'png'],
            help="Formati supportati: PDF, Word, Excel, Immagini"
        )
        
        st.markdown("---")
        
        submitted = st.form_submit_button("💾 Salva Documento", 
                                          type="primary", 
                                          use_container_width=True)
        
        if submitted:
            if not uploaded_file:
                st.error("⚠️ Seleziona un file da caricare")
            else:
                try:
                    # Crea directory documenti se non esiste (relativa alla directory corrente)
                    docs_dir = os.path.join(os.getcwd(), "documenti")
                    os.makedirs(docs_dir, exist_ok=True)
                    
                    # Salva file
                    file_name = f"{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
                    file_path = os.path.join(docs_dir, file_name)
                    
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Salva nel database
                    dati = {
                        'cacciatore_id': cacciatore_selezionato[0] if usa_cacciatore and cacciatore_selezionato else None,
                        'tipo_documento': tipo_documento,
                        'nome_file': uploaded_file.name,
                        'file_path': file_path,
                        'descrizione': descrizione.strip() if descrizione else None,
                        'anno': anno,
                        'data_documento': data_documento.strftime('%Y-%m-%d')
                    }
                    
                    doc_id = st.session_state.db.aggiungi_documento(dati)
                    
                    st.success(f"✅ Documento salvato correttamente! ID: {doc_id}")
                    st.info(f"📁 File salvato in: {file_path}")
                    
                except Exception as e:
                    st.error(f"⚠️ Errore durante il salvataggio: {str(e)}")

def show_archivio_documenti():
    """Mostra l'archivio documenti"""
    st.subheader("Archivio Documenti")
    
    # Filtri
    col1, col2 = st.columns(2)
    
    with col1:
        filtro_tipo = st.selectbox(
            "Tipo Documento",
            options=['Tutti', 'Licenza di Caccia', 'Libretto Regionale', 'Foglio Caccia',
                    'Autorizzazione RAS', 'Certificato Medico', 'Documento Identità',
                    'Ricevuta Pagamento', 'Altro']
        )
    
    with col2:
        anno_corrente = dt.datetime.now().year
        anni_disponibili = ['Tutti'] + list(range(anno_corrente - 5, anno_corrente + 1))
        filtro_anno = st.selectbox("Anno", options=anni_disponibili)
    
    # Query documenti
    conn = st.session_state.db.get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT d.*, c.cognome, c.nome
        FROM documenti d
        LEFT JOIN cacciatori c ON d.cacciatore_id = c.id
        WHERE 1=1
    """
    params = []
    
    if filtro_tipo != 'Tutti':
        query += " AND d.tipo_documento = ?"
        params.append(filtro_tipo)
    
    if filtro_anno != 'Tutti':
        query += " AND d.anno = ?"
        params.append(filtro_anno)
    
    query += " ORDER BY d.data_inserimento DESC"
    
    cursor.execute(query, params)
    documenti = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    if documenti:
        st.success(f"📁 Trovati {len(documenti)} documenti")
        
        # Mostra documenti
        for doc in documenti:
            with st.expander(
                f"📄 {doc['nome_file']} - {doc['tipo_documento']} "
                f"({doc.get('data_documento', 'N/D')})"
            ):
                col1, col2 = st.columns(2)
                
                with col1:
                    if doc.get('cognome'):
                        st.text(f"Cacciatore: {doc['cognome']} {doc['nome']}")
                    else:
                        st.text("Cacciatore: Documento Generale")
                    
                    st.text(f"Tipo: {doc['tipo_documento']}")
                    st.text(f"Anno: {doc.get('anno', 'N/D')}")
                    st.text(f"Data: {doc.get('data_documento', 'N/D')}")
                
                with col2:
                    st.text(f"File: {doc['nome_file']}")
                    st.text(f"Caricato: {doc.get('data_inserimento', 'N/D')}")
                    
                    if doc.get('file_path') and os.path.exists(doc['file_path']):
                        st.text("✅ File disponibile")
                    else:
                        st.text("⚠️ File non trovato")
                
                if doc.get('descrizione'):
                    st.markdown("**Descrizione:**")
                    st.text(doc['descrizione'])
                
                # Azioni
                col_a, col_b = st.columns(2)
                
                with col_a:
                    if st.button(f"📥 Scarica", key=f"download_doc_{doc['id']}"):
                        if doc.get('file_path') and os.path.exists(doc['file_path']):
                            try:
                                with open(doc['file_path'], 'rb') as f:
                                    st.download_button(
                                        label="📥 Download File",
                                        data=f,
                                        file_name=doc['nome_file'],
                                        key=f"dl_btn_{doc['id']}"
                                    )
                            except Exception as e:
                                st.error(f"Errore: {str(e)}")
                        else:
                            st.error("File non trovato")
                
                with col_b:
                    if st.button(f"🗑️ Elimina", key=f"delete_doc_{doc['id']}"):
                        st.warning("Funzione di eliminazione in sviluppo")
    
    else:
        st.warning("Nessun documento presente nell'archivio")
        st.info("Utilizza la tab 'Upload Documenti' per caricare documenti")
