```python
import streamlit as st
import pandas as pd
import datetime as dt

# Import opzionale di plotly
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

def show():
    """Mostra la pagina report e statistiche"""
    st.markdown('<div class="main-header">📊 Report e Statistiche</div>', unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Dashboard Generale",
        "📊 Analisi per Anno",
        "📉 Trend Temporali",
        "📋 Report Personalizzati"
    ])
    
    with tab1:
        show_dashboard_generale()
    
    with tab2:
        show_analisi_per_anno()
    
    with tab3:
        show_trend_temporali()
    
    with tab4:
        show_report_personalizzati()

def show_dashboard_generale():
    """Dashboard con panoramica generale"""
    st.subheader("Dashboard Generale")
    
    anno_corrente = dt.datetime.now().year
    
    # Statistiche generali
    stats = st.session_state.db.get_statistiche_generali()
    
    st.markdown("### 📊 Panoramica Generale")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "👥 Cacciatori Attivi",
            stats.get('cacciatori_attivi', 0)
        )
    
    with col2:
        st.metric(
            f"📖 Libretti {anno_corrente}",
            stats.get('libretti_anno_corrente', 0)
        )
    
    with col3:
        st.metric(
            f"📄 Fogli {anno_corrente}",
            stats.get('fogli_anno_corrente', 0)
        )
    
    with col4:
        st.metric(
            "⏳ Autorizzazioni in Attesa",
            stats.get('autorizzazioni_in_attesa', 0)
        )
    
    st.markdown("---")
    
    # Statistiche fogli caccia dettagliate
    st.markdown(f"### 📄 Stato Fogli Caccia {anno_corrente}")
    
    stats_fogli = st.session_state.db.get_statistiche_fogli(anno_corrente)
    
    if stats_fogli and stats_fogli.get('totale', 0) > 0:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if PLOTLY_AVAILABLE:
                # Grafico a torta
                labels = ['Disponibili', 'Consegnati', 'Rilasciati', 'Restituiti']
                values = [
                    stats_fogli.get('disponibili', 0),
                    stats_fogli.get('consegnati', 0),
                    stats_fogli.get('rilasciati', 0),
                    stats_fogli.get('restituiti', 0)
                ]
                
                fig = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values,
                    hole=.3,
                    marker_colors=['#d4edda', '#cce5ff', '#fff3cd', '#f8f9fa']
                )])
                
                fig.update_layout(
                    title="Distribuzione Fogli per Stato",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Alternativa senza plotly: usa st.bar_chart
                df_stats = pd.DataFrame({
                    'Stato': ['Disponibili', 'Consegnati', 'Rilasciati', 'Restituiti'],
                    'Numero': [
                        stats_fogli.get('disponibili', 0),
                        stats_fogli.get('consegnati', 0),
                        stats_fogli.get('rilasciati', 0),
                        stats_fogli.get('restituiti', 0)
                    ]
                })
                st.bar_chart(df_stats.set_index('Stato'))
        
        with col2:
            st.markdown("**Riepilogo Numerico**")
            
            st.metric("Totale", stats_fogli.get('totale', 0))
            st.metric("Disponibili", stats_fogli.get('disponibili', 0), 
                     delta_color="off")
            st.metric("Consegnati", stats_fogli.get('consegnati', 0))
            st.metric("Rilasciati", stats_fogli.get('rilasciati', 0))
            st.metric("Restituiti", stats_fogli.get('restituiti', 0))
            
            # Percentuale completamento
            totale = stats_fogli.get('totale', 0)
            if totale > 0:
                restituiti = stats_fogli.get('restituiti', 0)
                perc_completamento = (restituiti / totale) * 100
                
                st.markdown("---")
                st.metric(
                    "% Completamento",
                    f"{perc_completamento:.1f}%"
                )
    
    else:
        st.info(f"Nessun dato sui fogli caccia per l'anno {anno_corrente}")
    
    st.markdown("---")
    
    # Distribuzione geografica cacciatori
    st.markdown("### 🗺️ Distribuzione Geografica Cacciatori")
    
    cacciatori = st.session_state.db.get_tutti_cacciatori(solo_attivi=True)
    
    if cacciatori:
        df_cacciatori = pd.DataFrame(cacciatori)
        
        if 'comune' in df_cacciatori.columns:
            # Conta per comune
            comuni_count = df_cacciatori['comune'].value_counts().reset_index()
            comuni_count.columns = ['Comune', 'Numero Cacciatori']
            
            if PLOTLY_AVAILABLE:
                fig = px.bar(
                    comuni_count.head(10),
                    x='Comune',
                    y='Numero Cacciatori',
                    title='Top 10 Comuni per Numero di Cacciatori',
                    color='Numero Cacciatori',
                    color_continuous_scale='Blues'
                )
                
                fig.update_layout(height=400)
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Alternativa senza plotly
                st.subheader("Top 10 Comuni per Numero di Cacciatori")
                st.bar_chart(comuni_count.head(10).set_index('Comune'))
        else:
            st.info("Dati geografici non disponibili")
    else:
        st.info("Nessun cacciatore registrato")

def show_analisi_per_anno():
    """Analisi dettagliata per anno"""
    st.subheader("Analisi per Anno")
    
    anno_corrente = dt.datetime.now().year
    anni_disponibili = list(range(anno_corrente - 5, anno_corrente + 1))
    
    anno_selezionato = st.selectbox(
        "Seleziona Anno",
        options=anni_disponibili,
        index=anni_disponibili.index(anno_corrente)
    )
    
    st.markdown(f"### 📊 Statistiche Anno {anno_selezionato}")
    
    # Recupera dati anno
    libretti_anno = st.session_state.db.get_libretti_anno(anno_selezionato)
    fogli_anno = st.session_state.db.get_fogli_anno(anno_selezionato)
    stats_fogli = st.session_state.db.get_statistiche_fogli(anno_selezionato)
    
    # Metriche anno
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📖 Libretti Rilasciati", len(libretti_anno))
    
    with col2:
        st.metric("📄 Fogli Totali", stats_fogli.get('totale', 0))
    
    with col3:
        st.metric("✅ Fogli Restituiti", stats_fogli.get('restituiti', 0))
    
    st.markdown("---")
    
    # Grafici libretti
    if libretti_anno:
        st.markdown("#### 📖 Libretti Regionali")
        
        df_libretti = pd.DataFrame(libretti_anno)
        
        # Distribuzione per stato
        if 'stato' in df_libretti.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                stato_count = df_libretti['stato'].value_counts()
                
                if PLOTLY_AVAILABLE:
                    fig = go.Figure(data=[go.Pie(
                        labels=stato_count.index,
                        values=stato_count.values,
                        hole=.3
                    )])
                    
                    fig.update_layout(
                        title="Distribuzione Libretti per Stato",
                        height=350
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.subheader("Distribuzione Libretti per Stato")
                    st.bar_chart(stato_count)
            
            with col2:
                # Tabella riepilogo
                st.markdown("**Riepilogo Stati**")
                for stato, count in stato_count.items():
                    st.metric(stato, count)
        
        # Timeline rilasci
        if 'data_rilascio' in df_libretti.columns:
            st.markdown("#### 📅 Timeline Rilasci Libretti")
            
            # Converti date e conta per mese
            df_libretti_timeline = df_libretti[df_libretti['data_rilascio'].notna()].copy()
            
            if not df_libretti_timeline.empty:
                df_libretti_timeline['data_rilascio'] = pd.to_datetime(
                    df_libretti_timeline['data_rilascio']
                )
                df_libretti_timeline['mese'] = df_libretti_timeline['data_rilascio'].dt.to_period('M')
                
                timeline_count = df_libretti_timeline.groupby('mese').size().reset_index()
                timeline_count.columns = ['Mese', 'Numero Libretti']
                timeline_count['Mese'] = timeline_count['Mese'].astype(str)
                
                if PLOTLY_AVAILABLE:
                    fig = px.line(
                        timeline_count,
                        x='Mese',
                        y='Numero Libretti',
                        markers=True,
                        title=f'Rilasci Libretti nel {anno_selezionato}'
                    )
                    
                    fig.update_layout(height=350)
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.subheader(f'Rilasci Libretti nel {anno_selezionato}')
                    st.line_chart(timeline_count.set_index('Mese'))
    
    else:
        st.info(f"Nessun libretto registrato per l'anno {anno_selezionato}")
    
    st.markdown("---")
    
    # Grafici fogli caccia
    if fogli_anno:
        st.markdown("#### 📄 Fogli Caccia")
        
        df_fogli = pd.DataFrame(fogli_anno)
        
        # Stato fogli
        if 'stato' in df_fogli.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                stato_count = df_fogli['stato'].value_counts()
                
                if PLOTLY_AVAILABLE:
                    fig = px.bar(
                        x=stato_count.index,
                        y=stato_count.values,
                        labels={'x': 'Stato', 'y': 'Numero Fogli'},
                        title='Distribuzione Fogli per Stato',
                        color=stato_count.values,
                        color_continuous_scale='Viridis'
                    )
                    
                    fig.update_layout(height=350)
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.subheader("Distribuzione Fogli per Stato")
                    st.bar_chart(stato_count)
            
            with col2:
                st.markdown("**Riepilogo Stati**")
                for stato, count in stato_count.items():
                    st.metric(stato, count)
    
    else:
        st.info(f"Nessun foglio caccia registrato per l'anno {anno_selezionato}")

def show_trend_temporali():
    """Mostra trend nel tempo"""
    st.subheader("Trend Temporali")
    
    st.markdown("### 📈 Andamento Pluriennale")
    
    anno_corrente = dt.datetime.now().year
    anni_analisi = list(range(anno_corrente - 5, anno_corrente + 1))
    
    # Raccolta dati per tutti gli anni
    dati_anni = []
    
    for anno in anni_analisi:
        libretti = st.session_state.db.get_libretti_anno(anno)
        stats_fogli = st.session_state.db.get_statistiche_fogli(anno)
        
        dati_anni.append({
            'Anno': anno,
            'Libretti': len(libretti),
            'Fogli Totali': stats_fogli.get('totale', 0),
            'Fogli Consegnati': stats_fogli.get('consegnati', 0),
            'Fogli Rilasciati': stats_fogli.get('rilasciati', 0),
            'Fogli Restituiti': stats_fogli.get('restituiti', 0)
        })
    
    if dati_anni:
        df_trend = pd.DataFrame(dati_anni)
        
        # Grafico libretti nel tempo
        st.markdown("#### 📖 Trend Libretti Regionali")
        
        if PLOTLY_AVAILABLE:
            fig = px.line(
                df_trend,
                x='Anno',
                y='Libretti',
                markers=True,
                title='Numero Libretti Rilasciati per Anno'
            )
            
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.subheader('Numero Libretti Rilasciati per Anno')
            st.line_chart(df_trend.set_index('Anno')['Libretti'])
        
        # Grafico fogli nel tempo
        st.markdown("#### 📄 Trend Fogli Caccia")
        
        if PLOTLY_AVAILABLE:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df_trend['Anno'],
                y=df_trend['Fogli Totali'],
                mode='lines+markers',
                name='Totali',
                line=dict(color='blue', width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=df_trend['Anno'],
                y=df_trend['Fogli Consegnati'],
                mode='lines+markers',
                name='Consegnati',
                line=dict(color='green', width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=df_trend['Anno'],
                y=df_trend['Fogli Rilasciati'],
                mode='lines+markers',
                name='Rilasciati',
                line=dict(color='orange', width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=df_trend['Anno'],
                y=df_trend['Fogli Restituiti'],
                mode='lines+markers',
                name='Restituiti',
                line=dict(color='red', width=2)
            ))
            
            fig.update_layout(
                title='Andamento Fogli Caccia nel Tempo',
                xaxis_title='Anno',
                yaxis_title='Numero Fogli',
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.subheader('Andamento Fogli Caccia nel Tempo')
            st.line_chart(df_trend.set_index('Anno')[['Fogli Totali', 'Fogli Consegnati', 
                                                       'Fogli Rilasciati', 'Fogli Restituiti']])
        
        # Tabella riepilogo
        st.markdown("#### 📊 Tabella Riepilogo Pluriennale")
        
        st.dataframe(df_trend, use_container_width=True, hide_index=True)
        
        # Export dati
        csv = df_trend.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Scarica Dati Trend CSV",
            data=csv,
            file_name=f"trend_pluriennale_{dt.datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    else:
        st.warning("Dati insufficienti per generare trend temporali")

def show_report_personalizzati():
    """Genera report personalizzati"""
    st.subheader("Report Personalizzati")
    
    st.info("Genera report personalizzati in base ai tuoi criteri")
    
    # Selezione tipo report
    tipo_report = st.selectbox(
        "Tipo di Report",
        options=[
            "Report Anagrafico Completo",
            "Report Libretti per Anno",
            "Report Fogli Caccia Dettagliato",
            "Report Autorizzazioni RAS",
            "Report Attività Sistema"
        ]
    )
    
    # Parametri comuni
    col1, col2 = st.columns(2)
    
    with col1:
        anno_corrente = dt.datetime.now().year
        anno_report = st.number_input(
            "Anno di Riferimento",
            min_value=2015,
            max_value=anno_corrente + 1,
            value=anno_corrente,
            step=1
        )
    
    with col2:
        formato_export = st.selectbox(
            "Formato Export",
            options=["CSV", "Excel (futuro)"]
        )
    
    if st.button("📊 Genera Report", type="primary", use_container_width=True):
        genera_report_personalizzato(tipo_report, anno_report, formato_export)

def genera_report_personalizzato(tipo_report: str, anno: int, formato: str):
    """Genera un report personalizzato"""
    
    if tipo_report == "Report Anagrafico Completo":
        cacciatori = st.session_state.db.get_tutti_cacciatori(solo_attivi=True)
        
        if cacciatori:
            df = pd.DataFrame(cacciatori)
            
            # Seleziona colonne per export
            cols_export = ['numero_tessera', 'cognome', 'nome', 'codice_fiscale',
                          'data_nascita', 'luogo_nascita', 'indirizzo', 'comune',
                          'provincia', 'cap', 'telefono', 'cellulare', 'email']
            
            df_export = df[[col for col in cols_export if col in df.columns]].copy()
            
            st.success(f"✅ Report generato con {len(cacciatori)} cacciatori")
            
            st.dataframe(df_export, use_container_width=True, hide_index=True)
            
            if formato == "CSV":
                csv = df_export.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Scarica Report CSV",
                    data=csv,
                    file_name=f"report_anagrafico_{dt.datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        else:
            st.warning("Nessun cacciatore da esportare")
    
    elif tipo_report == "Report Libretti per Anno":
        libretti = st.session_state.db.get_libretti_anno(anno)
        
        if libretti:
            df = pd.DataFrame(libretti)
            
            cols_export = ['numero_libretto', 'cognome', 'nome', 'numero_tessera',
                          'anno', 'data_rilascio', 'data_scadenza', 'stato']
            
            df_export = df[[col for col in cols_export if col in df.columns]].copy()
            
            st.success(f"✅ Report generato con {len(libretti)} libretti")
            
            st.dataframe(df_export, use_container_width=True, hide_index=True)
            
            if formato == "CSV":
                csv = df_export.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Scarica Report CSV",
                    data=csv,
                    file_name=f"report_libretti_{anno}_{dt.datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        else:
            st.warning(f"Nessun libretto per l'anno {anno}")
    
    elif tipo_report == "Report Fogli Caccia Dettagliato":
        fogli = st.session_state.db.get_fogli_anno(anno)
        
        if fogli:
            df = pd.DataFrame(fogli)
            
            cols_export = ['numero_foglio', 'anno', 'cognome', 'nome',
                          'data_consegna', 'consegnato_da', 'data_rilascio',
                          'rilasciato_a', 'data_restituzione', 'stato']
            
            df_export = df[[col for col in cols_export if col in df.columns]].copy()
            
            st.success(f"✅ Report generato con {len(fogli)} fogli")
            
            st.dataframe(df_export, use_container_width=True, hide_index=True)
            
            if formato == "CSV":
                csv = df_export.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Scarica Report CSV",
                    data=csv,
                    file_name=f"report_fogli_{anno}_{dt.datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        else:
            st.warning(f"Nessun foglio per l'anno {anno}")
    
    elif tipo_report == "Report Attività Sistema":
        log = st.session_state.db.get_log_attivita(500)
        
        if log:
            df = pd.DataFrame(log)
            
            st.success(f"✅ Report generato con {len(log)} attività")
            
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            if formato == "CSV":
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Scarica Report CSV",
                    data=csv,
                    file_name=f"report_attivita_{dt.datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        else:
            st.warning("Nessuna attività registrata")
