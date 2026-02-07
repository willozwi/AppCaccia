import streamlit as st
import pandas as pd
import datetime as dt

def show():
    """Mostra la pagina libretti regionali"""
    st.markdown('<div class="main-header">📖 Libretti Regionali</div>', unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 Libretti per Anno", "➕ Nuovo Libretto", "📊 Statistiche"])
    
    with tab1:
        show_libretti_per_anno()
    
    with tab2:
        show_form_nuovo_libretto()
    
    with tab3:
        show_statistiche_libretti()

def show_libretti_per_anno():
    """Mostra i libretti filtrati per anno"""
    st.subheader("Libretti Regionali per Anno")
    
    # Selezione anno
    anno_corrente = dt.datetime.now().year
    anni_disponibili = list(range(anno_corrente - 5, anno_corrente + 2))
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        anno_selezionato = st.selectbox(
            "Seleziona Anno",
            options=anni_disponibili,
            index=anni_disponibili.index(anno_corrente) if anno_corrente in anni_disponibili else 0
        )
    
    with col2:
        if st.button("🔄 Aggiorna", use_container_width=True):
            st.rerun()
    
    # Recupera libretti dell'anno
    libretti = st.session_state.db.get_libretti_anno(anno_selezionato)
    
    if libretti:
        st.success(f"📖 Trovati {len(libretti)} libretti per l'anno {anno_selezionato}")
        
        # Crea DataFrame
        df_libretti = pd.DataFrame(libretti)
        
        # Seleziona colonne per visualizzazione
        cols_display = ['numero_libretto', 'cognome', 'nome', 'numero_tessera', 
                       'data_rilascio', 'data_scadenza', 'stato']
        
        df_display = df_libretti[cols_display].copy()
        df_display.columns = ['N. Libretto', 'Cognome', 'Nome', 'N. Tessera',
                             'Data Rilascio', 'Data Scadenza', 'Stato']
        
        # Colora in base allo stato
        def highlight_stato(row):
            if row['Stato'] == 'ATTIVO':
                return ['background-color: #d4edda'] * len(row)
            elif row['Stato'] == 'SCADUTO':
                return ['background-color: #f8d7da'] * len(row)
            elif row['Stato'] == 'SOSPESO':
                return ['background-color: #fff3cd'] * len(row)
            else:
                return [''] * len(row)
        
        st.dataframe(
            df_display.style.apply(highlight_stato, axis=1),
            use_container_width=True,
            height=400
        )
        
        # Statistiche rapide
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            attivi = len([l for l in libretti if l.get('stato') == 'ATTIVO'])
            st.metric("Libretti Attivi", attivi)
        
        with col2:
            scaduti = len([l for l in libretti if l.get('stato') == 'SCADUTO'])
            st.metric("Libretti Scaduti", scaduti)
        
        with col3:
            sospesi = len([l for l in libretti if l.get('stato') == 'SOSPESO'])
            st.metric("Libretti Sospesi", sospesi)
        
        # Esportazione
        st.markdown("---")
        st.subheader("Esporta Dati")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            csv = df_display.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Scarica CSV",
                data=csv,
                file_name=f"libretti_{anno_selezionato}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    else:
        st.warning(f"Nessun libretto registrato per l'anno {anno_selezionato}")
        st.info("Utilizza la tab 'Nuovo Libretto' per aggiungere libretti")

def show_form_nuovo_libretto():
    """Mostra il form per aggiungere un nuovo libretto"""
    st.subheader("Registrazione Nuovo Libretto Regionale")
    
    # Recupera cacciatori attivi
    cacciatori = st.session_state.db.get_tutti_cacciatori(solo_attivi=True)
    
    if not cacciatori:
        st.error("⚠️ Nessun cacciatore attivo nel database!")
        st.info("Aggiungi prima dei cacciatori nella sezione 'Anagrafe Cacciatori'")
        return
    
    with st.form("form_nuovo_libretto", clear_on_submit=True):
        st.markdown("**Dati Libretto**")
        
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
                min_value=2015,
                max_value=dt.datetime.now().year + 1,
                value=dt.datetime.now().year,
                step=1
            )
            
            numero_libretto = st.text_input(
                "Numero Libretto *",
                placeholder="es. 497424"
            )
        
        with col2:
            data_rilascio = st.date_input(
                "Data Rilascio *",
                value=dt.datetime.now().date(),
                format="DD/MM/YYYY"
            )
            
            # Calcola data scadenza (es. 31/12 dell'anno)
            data_scadenza_default = dt.datetime(anno, 12, 31).date()
            data_scadenza = st.date_input(
                "Data Scadenza",
                value=data_scadenza_default,
                format="DD/MM/YYYY"
            )
            
            stato = st.selectbox(
                "Stato",
                options=['ATTIVO', 'SCADUTO', 'SOSPESO', 'REVOCATO'],
                index=0
            )
        
        note = st.text_area("Note", placeholder="Note aggiuntive...")
        
        st.markdown("---")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            submitted = st.form_submit_button("💾 Salva Libretto", 
                                              type="primary", 
                                              use_container_width=True)
        
        if submitted:
            if not numero_libretto:
                st.error("⚠️ Il numero libretto è obbligatorio")
            else:
                try:
                    dati = {
                        'cacciatore_id': cacciatore_selezionato[0],
                        'anno': anno,
                        'numero_libretto': numero_libretto.strip(),
                        'data_rilascio': data_rilascio.strftime('%Y-%m-%d'),
                        'data_scadenza': data_scadenza.strftime('%Y-%m-%d'),
                        'stato': stato,
                        'note': note.strip() if note else None,
                        'file_path': None
                    }
                    
                    libretto_id = st.session_state.db.aggiungi_libretto(dati)
                    
                    st.success(f"✅ Libretto registrato correttamente! ID: {libretto_id}")
                    st.balloons()
                    
                except Exception as e:
                    if "UNIQUE constraint failed" in str(e):
                        st.error("⚠️ Numero libretto già esistente o cacciatore già ha un libretto per questo anno!")
                    else:
                        st.error(f"⚠️ Errore durante il salvataggio: {str(e)}")

def show_statistiche_libretti():
    """Mostra statistiche sui libretti"""
    st.subheader("Statistiche Libretti Regionali")
    
    anno_corrente = dt.datetime.now().year
    anni_disponibili = list(range(anno_corrente - 5, anno_corrente + 1))
    
    # Statistiche per anno
    st.markdown("### 📊 Distribuzione per Anno")
    
    stats_anni = []
    for anno in reversed(anni_disponibili):
        libretti_anno = st.session_state.db.get_libretti_anno(anno)
        if libretti_anno:
            attivi = len([l for l in libretti_anno if l.get('stato') == 'ATTIVO'])
            scaduti = len([l for l in libretti_anno if l.get('stato') == 'SCADUTO'])
            sospesi = len([l for l in libretti_anno if l.get('stato') == 'SOSPESO'])
            
            stats_anni.append({
                'Anno': anno,
                'Totale': len(libretti_anno),
                'Attivi': attivi,
                'Scaduti': scaduti,
                'Sospesi': sospesi
            })
    
    if stats_anni:
        df_stats = pd.DataFrame(stats_anni)
        
        # Visualizza tabella
        st.dataframe(df_stats, use_container_width=True, hide_index=True)
        
        # Grafico
        st.bar_chart(df_stats.set_index('Anno')[['Attivi', 'Scaduti', 'Sospesi']])
    else:
        st.warning("Nessun dato disponibile per generare statistiche")
    
    # Libretti in scadenza
    st.markdown("---")
    st.markdown("### ⚠️ Libretti in Scadenza")
    
    giorni_preavviso = st.slider(
        "Giorni di preavviso",
        min_value=7,
        max_value=90,
        value=30,
        step=7
    )
    
    # Recupera libretti anno corrente
    libretti_correnti = st.session_state.db.get_libretti_anno(anno_corrente)
    
    data_limite = (dt.datetime.now() + dt.timedelta(days=giorni_preavviso)).date()
    
    libretti_in_scadenza = [
        l for l in libretti_correnti 
        if l.get('data_scadenza') and 
           dt.datetime.strptime(l['data_scadenza'], '%Y-%m-%d').date() <= data_limite and
           l.get('stato') == 'ATTIVO'
    ]
    
    if libretti_in_scadenza:
        st.warning(f"⚠️ {len(libretti_in_scadenza)} libretti in scadenza nei prossimi {giorni_preavviso} giorni")
        
        df_scadenza = pd.DataFrame(libretti_in_scadenza)
        cols_display = ['numero_libretto', 'cognome', 'nome', 'data_scadenza']
        df_display = df_scadenza[cols_display].copy()
        df_display.columns = ['N. Libretto', 'Cognome', 'Nome', 'Data Scadenza']
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.success(f"✅ Nessun libretto in scadenza nei prossimi {giorni_preavviso} giorni")
