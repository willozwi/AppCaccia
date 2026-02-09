import streamlit as st
import pandas as pd
import datetime as dt
import os
import sys

def fmt_date_it(value) -> str:
    """
    Formatta una data in formato italiano dd/mm/yyyy per la visualizzazione.
    Accetta None, str (YYYY-MM-DD), datetime.date, o datetime.datetime
    """
    if value is None or value == '' or value == 'N/A':
        return ''
    
    try:
        # Se è già un oggetto date o datetime
        if hasattr(value, 'strftime'):
            return value.strftime('%d/%m/%Y')
        
        # Se è una stringa in formato ISO (YYYY-MM-DD o YYYY/MM/DD)
        if isinstance(value, str):
            # Prova a parsare il formato ISO
            try:
                date_obj = dt.datetime.strptime(value, '%Y-%m-%d').date()
                return date_obj.strftime('%d/%m/%Y')
            except:
                # Prova con separatore slash
                try:
                    date_obj = dt.datetime.strptime(value, '%Y/%m/%d').date()
                    return date_obj.strftime('%d/%m/%Y')
                except:
                    return value  # Se non riesce a parsare, ritorna la stringa originale
        
        return ''
    except:
        return ''


def show():
    """Mostra la pagina fogli caccia A3"""
    st.markdown('<div class="main-header">📄 Fogli Caccia A3 Annuali</div>', unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs([
        "📋 Gestione Fogli",
        "📥 Consegna Fogli",
        "🔄 Restituzione Fogli"
    ])
    
    with tab1:
        show_gestione_fogli()
    
    with tab2:
        show_consegna_fogli()
    
    with tab3:
        show_restituzione_fogli()

def _reset_filtri():
    """Callback per resettare tutti i filtri (eseguito prima del re-render)"""
    keys_to_reset = ['ricerca_fogli', 'filtro_solo_con_file', 'filtro_data_da', 'filtro_data_a']
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]

def show_gestione_fogli():
    """Gestione completa dei fogli caccia"""
    st.subheader("Gestione Fogli Caccia A3")
    
    # Info debug opzionale
    if st.checkbox("🔍 Info Database", value=False, key="debug_fogli"):
        st.info(f"**Database:** {st.session_state.db.db_path}")
        
        # Conta fogli totali nel database
        conn = st.session_state.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM fogli_caccia")
        total = cursor.fetchone()[0]
        conn.close()
        
        st.metric("Fogli Totali nel Database", total)
    
    # Selezione anno
    anno_corrente = dt.datetime.now().year
    anni_disponibili = list(range(anno_corrente - 3, anno_corrente + 2))
    
    col1, col2, col3, col4 = st.columns([2, 2, 3, 1])
    
    with col1:
        anno_selezionato = st.selectbox(
            "Anno",
            options=anni_disponibili,
            index=anni_disponibili.index(anno_corrente) if anno_corrente in anni_disponibili else 0
        )
    
    with col2:
        # Stati effettivi dai file Excel
        filtro_stato = st.selectbox(
            "Filtra per Stato",
            options=['Tutti', 'Consegnato', 'Stampato', 'Da rinnovare']
        )
    
    with col3:
        # Campo ricerca
        ricerca = st.text_input(
            "🔍 Cerca (Nome, Cognome, N. Foglio)",
            placeholder="Es: Mario, Corona, 2025102752...",
            help="Cerca per Nome, Cognome, Numero Foglio o Nome nel campo Rilasciato A. La ricerca filtra in tempo reale.",
            key="ricerca_fogli"
        )
    
    with col4:
        if st.button("🔄 Aggiorna", use_container_width=True):
            st.rerun()
    
    # Riga filtri aggiuntivi (espandibile)
    with st.expander("🔧 Filtri Avanzati", expanded=False):
        col_a, col_b, col_c, col_d = st.columns([2, 2, 2, 1])
        
        with col_a:
            solo_con_file = st.checkbox(
                "📁 Solo con File Excel",
                value=False,
                help="Mostra solo fogli con file Excel associato",
                key="filtro_solo_con_file"
            )

        with col_b:
            data_da = st.date_input(
                "📅 Data Rilascio Da",
                value=None,
                format="DD/MM/YYYY",
                help="Filtra fogli rilasciati da questa data in poi",
                key="filtro_data_da"
            )

        with col_c:
            data_a = st.date_input(
                "📅 Data Rilascio A",
                value=None,
                format="DD/MM/YYYY",
                help="Filtra fogli rilasciati fino a questa data",
                key="filtro_data_a"
            )

        with col_d:
            st.button("🔄 Reset", help="Resetta tutti i filtri", use_container_width=True,
                       on_click=_reset_filtri)
    
    # Recupera fogli
    stato_filtro = None if filtro_stato == 'Tutti' else filtro_stato
    fogli = st.session_state.db.get_fogli_anno(anno_selezionato, stato_filtro)
    
    # Statistiche
    stats = st.session_state.db.get_statistiche_fogli(anno_selezionato)
    
    if stats and stats.get('totale', 0) > 0:
        # Calcola consegnati (checkbox) da campo consegnato
        consegnati_checkbox = sum(1 for f in fogli if f.get('consegnato', 0) == 1)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Totale", stats.get('totale', 0))
        with col2:
            st.metric("Consegnati (stato)", stats.get('consegnati', 0), 
                     help="Fogli con stato CONSEGNATO")
        with col3:
            st.metric("Consegnati (flag)", consegnati_checkbox,
                     help="Fogli con checkbox consegnato attivo")
        with col4:
            st.metric("Stampati", stats.get('rilasciati', 0),
                     help="Fogli gia stampati e rilasciati")
        with col5:
            st.metric("Da Rinnovare", stats.get('da_rinnovare', 0),
                     help="Fogli da rinnovare per nuovo anno")
    
    # ========== CANCELLA TUTTI I FOGLI ==========
    # Pulsante per cancellare tutti i fogli dell'anno selezionato
    if 'cancella_fogli_confirm' not in st.session_state:
        st.session_state.cancella_fogli_confirm = False

    with st.expander("⚠️ Operazioni Pericolose", expanded=False):
        st.warning("**Attenzione:** Le operazioni qui sotto sono irreversibili.")
        if st.button("🗑️ Cancella Tutti i Fogli dell'Anno", key="btn_cancella_tutti_fogli",
                     use_container_width=True):
            st.session_state.cancella_fogli_confirm = True
            st.rerun()

        if st.session_state.cancella_fogli_confirm:
            totale = stats.get('totale', 0) if stats else 0
            st.error(
                f"⚠️ **Stai per cancellare TUTTI i {totale} fogli dell'anno {anno_selezionato}** "
                f"e i relativi allegati. Questa operazione è **irreversibile**. "
                f"Potrai ricaricarli tramite **Import Fogli Massivo**."
            )
            conf_col1, conf_col2, conf_col3 = st.columns([2, 2, 6])
            with conf_col1:
                if st.button("✅ Conferma Cancellazione", type="primary",
                             key="confirm_cancella_tutti"):
                    try:
                        eliminati = st.session_state.db.cancella_tutti_fogli_anno(anno_selezionato)
                        st.session_state.cancella_fogli_confirm = False
                        st.success(f"✅ Cancellati {eliminati} fogli per l'anno {anno_selezionato}.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"⚠️ Errore durante la cancellazione: {str(e)}")
            with conf_col2:
                if st.button("❌ Annulla", key="cancel_cancella_tutti"):
                    st.session_state.cancella_fogli_confirm = False
                    st.rerun()

    st.markdown("---")

    # Elenco fogli
    if fogli:
        df_fogli = pd.DataFrame(fogli)
        
        # Applica filtro ricerca
        if ricerca:
            ricerca_lower = ricerca.lower().strip()
            
            # Crea maschera di filtro
            mask = pd.Series([False] * len(df_fogli))
            
            # Cerca in numero_foglio
            if 'numero_foglio' in df_fogli.columns:
                mask |= df_fogli['numero_foglio'].astype(str).str.lower().str.contains(ricerca_lower, na=False)
            
            # Cerca in cognome
            if 'cognome' in df_fogli.columns:
                mask |= df_fogli['cognome'].astype(str).str.lower().str.contains(ricerca_lower, na=False)
            
            # Cerca in nome
            if 'nome' in df_fogli.columns:
                mask |= df_fogli['nome'].astype(str).str.lower().str.contains(ricerca_lower, na=False)
            
            # Cerca in rilasciato_a
            if 'rilasciato_a' in df_fogli.columns:
                mask |= df_fogli['rilasciato_a'].astype(str).str.lower().str.contains(ricerca_lower, na=False)
            
            # Applica filtro
            df_fogli = df_fogli[mask]
            
            if len(df_fogli) == 0:
                st.warning(f"⚠️ Nessun foglio trovato per la ricerca: '{ricerca}'")
                return
            else:
                st.success(f"📄 Trovati {len(df_fogli)} fogli per '{ricerca}' nell'anno {anno_selezionato}")
        else:
            st.success(f"📄 Trovati {len(df_fogli)} fogli per l'anno {anno_selezionato}")
        
        # Applica filtri avanzati
        fogli_totali = len(df_fogli)
        
        # Filtro: solo con file
        if solo_con_file and 'file_path' in df_fogli.columns:
            df_fogli = df_fogli[df_fogli['file_path'].notna() & (df_fogli['file_path'] != '')]
            if len(df_fogli) == 0:
                st.warning("⚠️ Nessun foglio con file Excel trovato")
                return
        
        # Filtro: data rilascio da
        if data_da and 'data_rilascio' in df_fogli.columns:
            df_fogli = df_fogli[pd.to_datetime(df_fogli['data_rilascio'], errors='coerce') >= pd.to_datetime(data_da)]
        
        # Filtro: data rilascio a
        if data_a and 'data_rilascio' in df_fogli.columns:
            df_fogli = df_fogli[pd.to_datetime(df_fogli['data_rilascio'], errors='coerce') <= pd.to_datetime(data_a)]
        
        # Messaggio filtri applicati
        if solo_con_file or data_da or data_a:
            filtri_attivi = []
            if solo_con_file:
                filtri_attivi.append("con file")
            if data_da:
                filtri_attivi.append(f"da {data_da.strftime('%d/%m/%Y')}")
            if data_a:
                filtri_attivi.append(f"a {data_a.strftime('%d/%m/%Y')}")
            
            st.info(f"🔧 Filtri applicati: {', '.join(filtri_attivi)} → {len(df_fogli)}/{fogli_totali} fogli")
        
        if len(df_fogli) == 0:
            st.warning("⚠️ Nessun foglio trovato con i filtri selezionati")
            return
        
        # ========== ORDINAMENTO ALFABETICO A→Z ==========
        # Usa cognome e nome dal database
        if 'cognome' in df_fogli.columns and 'nome' in df_fogli.columns:
            # Riempi valori mancanti con stringa vuota per evitare errori
            df_fogli['cognome'] = df_fogli['cognome'].fillna('')
            df_fogli['nome'] = df_fogli['nome'].fillna('')
            
            # Ordina per cognome (primario) e nome (secondario) A→Z
            df_fogli = df_fogli.sort_values(
                by=['cognome', 'nome'], 
                ascending=[True, True], 
                kind='mergesort'  # Stabile
            ).reset_index(drop=True)
        elif 'rilasciato_a' in df_fogli.columns:
            # Fallback: se cognome/nome non ci sono, usa rilasciato_a
            # Parse: "Cognome Nome" split sull'ultimo spazio
            def parse_rilasciato_a(val):
                if pd.isna(val) or not val:
                    return ('', '')
                parts = str(val).strip().split()
                if len(parts) >= 2:
                    # Ultimo = nome, tutto il resto = cognome
                    return (' '.join(parts[:-1]), parts[-1])
                elif len(parts) == 1:
                    return (parts[0], '')
                else:
                    return ('', '')
            
            df_fogli['_cognome_sort'] = df_fogli['rilasciato_a'].apply(lambda x: parse_rilasciato_a(x)[0])
            df_fogli['_nome_sort'] = df_fogli['rilasciato_a'].apply(lambda x: parse_rilasciato_a(x)[1])
            
            df_fogli = df_fogli.sort_values(
                by=['_cognome_sort', '_nome_sort'], 
                ascending=[True, True], 
                kind='mergesort'
            ).reset_index(drop=True)
            
            # Rimuovi colonne temporanee
            df_fogli = df_fogli.drop(columns=['_cognome_sort', '_nome_sort'])
        
        
        # Prepara colonne per visualizzazione
        cols_base = ['numero_foglio', 'stato']
        
        # Aggiungi colonne condizionali in base ai dati presenti
        if 'cognome' in df_fogli.columns:
            cols_base.extend(['cognome', 'nome'])
        
        cols_base.extend(['data_consegna', 'consegnato_da', 
                         'data_rilascio', 'rilasciato_a',
                         'data_restituzione'])
        
        # Aggiungi file_path se presente
        if 'file_path' in df_fogli.columns:
            cols_base.append('file_path')
        
        # Filtra solo colonne esistenti
        cols_display = [col for col in cols_base if col in df_fogli.columns]
        
        df_display = df_fogli[cols_display].copy()
        
        # Rinomina colonne
        col_names = {
            'numero_foglio': 'N. Foglio',
            'stato': 'Stato',
            'cognome': 'Cognome',
            'nome': 'Nome',
            'data_consegna': 'Data Consegna',
            'consegnato_da': 'Consegnato Da',
            'data_rilascio': 'Data Rilascio',
            'rilasciato_a': 'Rilasciato A',
            'data_restituzione': 'Data Restituzione',
            'file_path': 'File'
        }
        
        df_display.columns = [col_names.get(col, col) for col in df_display.columns]
        
        # Semplifica percorso file per visualizzazione
        if 'File' in df_display.columns:
            df_display['File'] = df_display['File'].apply(
                lambda x: '📄 ' + x.split('\\')[-1] if x and isinstance(x, str) else 'Nessuno'
            )
        
        # Colora in base allo stato
        def highlight_stato(row):
            stato = row['Stato']
            if stato == 'Consegnato':
                return ['background-color: #cce5ff'] * len(row)  # Blu chiaro
            elif stato == 'Stampato':
                return ['background-color: #d4edda'] * len(row)  # Verde chiaro
            elif stato == 'Da rinnovare':
                return ['background-color: #fff3cd'] * len(row)  # Giallo chiaro
            elif stato == 'DISPONIBILE':
                return ['background-color: #e2e3e5'] * len(row)  # Grigio
            elif stato == 'RESTITUITO':
                return ['background-color: #f8f9fa'] * len(row)  # Grigio chiaro
            else:
                return [''] * len(row)
        
        
        # Nota informativa per utente
        st.info("""
        ℹ️ **Apertura File Excel**: Il pulsante "Apri (Excel)" apre il file direttamente dal suo percorso originale.
        Le modifiche salvate in Excel si rifletteranno nel file originale.
        
        ⚠️ **Nota**: Il file si apre sul PC dove è in esecuzione Streamlit. 
        Se l'app non gira sul tuo PC locale, usa Download/Upload manuale.
        """)
        
        # Visualizza tabella stile Excel con editing interattivo
        st.markdown("### 📋 Elenco Fogli")
        
        # Prepara DataFrame per editing
        df_edit = df_fogli.copy()
        
        # Crea DataFrame con colonne editabili
        edit_data = []
        id_map = {}  # Mappa indice -> id foglio
        cacciatore_map = {}  # Mappa indice -> cacciatore_id
        
        for idx, row in df_edit.iterrows():
            # Formatta date per visualizzazione
            data_restituzione_fmt = fmt_date_it(row.get('data_restituzione', '')) or ''

            # Costruisci Cognome Nome
            cognome = str(row.get('cognome', '') or '')
            nome = str(row.get('nome', '') or '')
            cognome_nome = f"{cognome} {nome}".strip()
            if not cognome_nome:
                cognome_nome = str(row.get('rilasciato_a', '') or '')

            # Contatto telefonico: preferisci cellulare, poi telefono
            cellulare = str(row.get('cellulare', '') or '')
            telefono = str(row.get('telefono', '') or '')
            contatto_tel = cellulare if cellulare else telefono

            edit_data.append({
                'Cognome Nome': cognome_nome,
                'N. Foglio': str(row.get('numero_foglio', 'N/A')),
                'Restituito in data': data_restituzione_fmt,
                'Stampato': bool(row.get('stampato', 0)),
                'Consegnato': bool(row.get('consegnato', 0)),
                'Contatto telefonico': contatto_tel
            })

            # Salva mapping indice -> id
            id_map[len(edit_data) - 1] = row.get('id')
            cacciatore_map[len(edit_data) - 1] = row.get('cacciatore_id')
        
        df_display = pd.DataFrame(edit_data)

        # Salva valori originali PRIMA di data_editor
        # (data_editor potrebbe modificare df_display in-place in alcune versioni di Streamlit)
        original_stampato = df_display['Stampato'].tolist()
        original_consegnato = df_display['Consegnato'].tolist()
        original_restituzione = df_display['Restituito in data'].tolist()
        original_contatto = df_display['Contatto telefonico'].tolist()

        # Usa data_editor per editing interattivo
        edited_df = st.data_editor(
            df_display,
            use_container_width=True,
            hide_index=True,
            height=min(600, 40 + len(df_display) * 35),
            column_config={
                "Cognome Nome": st.column_config.TextColumn(
                    "Cognome Nome",
                    width="medium",
                    disabled=True
                ),
                "N. Foglio": st.column_config.TextColumn(
                    "N. Foglio",
                    width="small",
                    disabled=True
                ),
                "Restituito in data": st.column_config.TextColumn(
                    "Restituito in data",
                    width="medium",
                    help="Inserire data in formato gg/mm/aaaa"
                ),
                "Stampato": st.column_config.CheckboxColumn(
                    "Stampato",
                    width="small",
                    help="Spunta se stampato"
                ),
                "Consegnato": st.column_config.CheckboxColumn(
                    "Consegnato",
                    width="small",
                    help="Spunta se consegnato"
                ),
                "Contatto telefonico": st.column_config.TextColumn(
                    "Contatto telefonico",
                    width="medium",
                    help="Numero di telefono del cacciatore"
                )
            },
            key="fogli_data_editor"
        )
        
        # Rileva modifiche tramite session state e salva automaticamente
        if "fogli_data_editor" in st.session_state:
            editor_changes = st.session_state["fogli_data_editor"]
            edited_rows = editor_changes.get("edited_rows", {})

            if edited_rows:
                changes_saved = False

                for row_idx_str, row_changes in edited_rows.items():
                    row_idx = int(row_idx_str)
                    foglio_id = id_map.get(row_idx)
                    if foglio_id is None:
                        continue

                    numero_foglio = df_display.iloc[row_idx]['N. Foglio']

                    if "Stampato" in row_changes:
                        old_val = original_stampato[row_idx]
                        new_val = bool(row_changes["Stampato"])
                        if old_val != new_val:
                            try:
                                st.session_state.db.set_stampato(foglio_id, new_val)
                                st.toast(f"Stampato aggiornato per {numero_foglio}", icon="✅")
                                changes_saved = True
                            except Exception as e:
                                st.error(f"Errore salvataggio Stampato: {e}")

                    if "Consegnato" in row_changes:
                        old_val = original_consegnato[row_idx]
                        new_val = bool(row_changes["Consegnato"])
                        if old_val != new_val:
                            try:
                                st.session_state.db.set_consegnato(foglio_id, new_val)
                                st.toast(f"Consegnato aggiornato per {numero_foglio}", icon="✅")
                                changes_saved = True
                            except Exception as e:
                                st.error(f"Errore salvataggio Consegnato: {e}")

                    if "Restituito in data" in row_changes:
                        old_val = original_restituzione[row_idx]
                        new_val = str(row_changes["Restituito in data"]).strip()
                        if old_val != new_val:
                            try:
                                # Converti da formato italiano gg/mm/aaaa a ISO yyyy-mm-dd
                                data_iso = None
                                if new_val:
                                    try:
                                        data_iso = dt.datetime.strptime(new_val, '%d/%m/%Y').strftime('%Y-%m-%d')
                                    except ValueError:
                                        # Prova anche formato ISO diretto
                                        try:
                                            dt.datetime.strptime(new_val, '%Y-%m-%d')
                                            data_iso = new_val
                                        except ValueError:
                                            st.error(f"Formato data non valido per {numero_foglio}. Usare gg/mm/aaaa")
                                            data_iso = None
                                st.session_state.db.set_data_restituzione(foglio_id, data_iso)
                                st.toast(f"Data restituzione aggiornata per {numero_foglio}", icon="✅")
                                changes_saved = True
                            except Exception as e:
                                st.error(f"Errore salvataggio data restituzione: {e}")

                    if "Contatto telefonico" in row_changes:
                        old_val = original_contatto[row_idx]
                        new_val = str(row_changes["Contatto telefonico"]).strip()
                        if old_val != new_val:
                            cacciatore_id = cacciatore_map.get(row_idx)
                            if cacciatore_id:
                                try:
                                    st.session_state.db.update_contatto_telefonico(cacciatore_id, new_val)
                                    st.toast(f"Contatto telefonico aggiornato per {numero_foglio}", icon="✅")
                                    changes_saved = True
                                except Exception as e:
                                    st.error(f"Errore salvataggio contatto telefonico: {e}")
                            else:
                                st.warning(f"Nessun cacciatore associato al foglio {numero_foglio}")

                if changes_saved:
                    st.rerun()
        
        # Sezione Azioni aggiuntive (modifica date e apertura file)
        st.markdown("---")
        st.markdown("**✏️ Azioni Aggiuntive sul Foglio**")
        
        col_select, col_info = st.columns([2, 1])
        
        with col_select:
            # Selectbox per scegliere il foglio
            foglio_options = [
                (row.get('id'), f"{row.get('numero_foglio', 'N/A')} - {row.get('rilasciato_a', 'N/A')}")
                for idx, row in df_fogli.iterrows()
            ]
            
            if foglio_options:
                selected_foglio_id = st.selectbox(
                    "Seleziona Foglio per modificare date o aprire file",
                    options=[opt[0] for opt in foglio_options],
                    format_func=lambda x: next(opt[1] for opt in foglio_options if opt[0] == x),
                    key="select_foglio_elenco"
                )
            else:
                selected_foglio_id = None
        
        with col_info:
            st.info(f"📊 Totale fogli: {len(df_fogli)}")
        
        # Se c'è un foglio selezionato, mostra form per date e file
        if selected_foglio_id:
            selected_row = df_fogli[df_fogli['id'] == selected_foglio_id].iloc[0]
            
            edit_col1, edit_col2, edit_col3 = st.columns(3)
            
            with edit_col1:
                # Data Rilascio
                data_ril_obj = selected_row.get('data_rilascio')
                if data_ril_obj and data_ril_obj != 'N/A':
                    try:
                        if isinstance(data_ril_obj, str):
                            data_ril_obj = pd.to_datetime(data_ril_obj).date()
                    except:
                        data_ril_obj = None
                else:
                    data_ril_obj = None
                
                # Checkbox per abilitare/disabilitare il campo data rilascio
                abilita_data_rilascio = st.checkbox(
                    "📅 Data Rilascio",
                    value=data_ril_obj is not None,
                    key=f"abilita_data_rilascio_{selected_foglio_id}",
                    help="Spunta per impostare una data, deseleziona per cancellare"
                )
                
                new_data_rilascio = None
                if abilita_data_rilascio:
                    new_data_rilascio = st.date_input(
                        "Seleziona data",
                        value=data_ril_obj if data_ril_obj else dt.datetime.now().date(),
                        key=f"edit_data_rilascio_{selected_foglio_id}",
                        format="DD/MM/YYYY",
                        label_visibility="collapsed"
                    )
                
                if st.button("💾 Salva Data Rilascio", key=f"save_ril_{selected_foglio_id}", use_container_width=True):
                    try:
                        st.session_state.db.set_data_rilascio(selected_foglio_id, str(new_data_rilascio) if new_data_rilascio else None)
                        st.success("✅ Data rilascio salvata!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Errore: {e}")
            
            with edit_col2:
                # Data Restituzione
                data_rest_obj = selected_row.get('data_restituzione')
                if data_rest_obj and data_rest_obj != 'N/A':
                    try:
                        if isinstance(data_rest_obj, str):
                            data_rest_obj = pd.to_datetime(data_rest_obj).date()
                    except:
                        data_rest_obj = None
                else:
                    data_rest_obj = None
                
                new_data_restituzione = st.date_input(
                    "📅 Data Restituzione",
                    value=data_rest_obj,
                    key=f"edit_data_restituzione_{selected_foglio_id}",
                    format="DD/MM/YYYY"
                )
                
                if st.button("💾 Salva Data Restituzione", key=f"save_rest_{selected_foglio_id}", use_container_width=True):
                    try:
                        st.session_state.db.set_data_restituzione(selected_foglio_id, new_data_restituzione)
                        st.success("✅ Data restituzione salvata!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Errore: {e}")
            
            with edit_col3:
                # Info file e bottone Apri Excel
                file_path = selected_row.get('file_path', None)
                if file_path and isinstance(file_path, str) and file_path.strip():
                    st.caption(f"📄 {os.path.basename(file_path)}")
                    
                    if st.button("📂 Apri Excel", key=f"apri_excel_{selected_foglio_id}", use_container_width=True):
                        if not os.path.exists(file_path):
                            st.error(f"❌ File non trovato")
                        else:
                            try:
                                if sys.platform.startswith('win'):
                                    os.startfile(file_path)
                                    st.success("✅ File aperto!")
                                elif sys.platform == 'darwin':
                                    import subprocess
                                    subprocess.call(['open', file_path])
                                    st.success("✅ File aperto!")
                                elif sys.platform.startswith('linux'):
                                    import subprocess
                                    subprocess.call(['xdg-open', file_path])
                                    st.success("✅ File aperto!")
                            except Exception as e:
                                st.error(f"Errore: {e}")
                else:
                    st.caption("Nessun file")
        
        
        # Form per aggiungere nuovi fogli in batch
        st.markdown("---")
        st.subheader("➕ Aggiungi Nuovi Fogli")
        
        with st.form("form_batch_fogli"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                anno_nuovo = st.number_input(
                    "Anno",
                    min_value=2015,
                    max_value=dt.datetime.now().year + 1,
                    value=anno_selezionato,
                    step=1
                )
            
            with col2:
                numero_iniziale = st.number_input(
                    "Numero Iniziale",
                    min_value=1,
                    value=497424,
                    step=1
                )
            
            with col3:
                quantita = st.number_input(
                    "Quantità",
                    min_value=1,
                    max_value=100,
                    value=20,
                    step=1
                )
            
            submitted = st.form_submit_button("💾 Crea Fogli", 
                                             type="primary", 
                                             use_container_width=True)
            
            if submitted:
                try:
                    fogli_creati = 0
                    fogli_saltati = 0
                    for i in range(quantita):
                        numero_foglio = str(numero_iniziale + i)
                        
                        dati = {
                            'numero_foglio': numero_foglio,
                            'anno': anno_nuovo,
                            'cacciatore_id': None,
                            'tipo': 'A3',
                            'data_consegna': None,
                            'consegnato_da': None,
                            'data_rilascio': None,
                            'rilasciato_a': None,
                            'data_restituzione': None,
                            'restituito_da': None,
                            'stato': 'DISPONIBILE',
                            'note': None,
                            'file_path': None
                        }
                        
                        try:
                            st.session_state.db.aggiungi_foglio_caccia(dati)
                            fogli_creati += 1
                        except:
                            fogli_saltati += 1  # Foglio già esistente
                    
                    if fogli_creati > 0:
                        st.success(f"✅ Creati {fogli_creati} nuovi fogli!")
                        if fogli_saltati > 0:
                            st.info(f"ℹ️ {fogli_saltati} fogli già esistenti (saltati)")
                        st.balloons()
                        
                        # Forza il refresh della pagina dopo 1 secondo
                        import time
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.warning("⚠️ Tutti i fogli esistono già!")
                    
                except Exception as e:
                    st.error(f"⚠️ Errore: {str(e)}")
    
    else:
        st.warning(f"Nessun foglio presente per l'anno {anno_selezionato}")
        
        # Form per aggiungere primi fogli
        st.info("👇 Crea i primi fogli per quest'anno")
        
        with st.form("form_primi_fogli"):
            col1, col2 = st.columns(2)
            
            with col1:
                numero_iniziale = st.number_input(
                    "Numero Iniziale",
                    min_value=1,
                    value=497424,
                    step=1
                )
            
            with col2:
                quantita = st.number_input(
                    "Quantità",
                    min_value=1,
                    max_value=100,
                    value=20,
                    step=1
                )
            
            submitted = st.form_submit_button("💾 Crea Fogli", 
                                             type="primary", 
                                             use_container_width=True)
            
            if submitted:
                try:
                    fogli_creati = 0
                    fogli_saltati = 0
                    
                    for i in range(quantita):
                        numero_foglio = str(numero_iniziale + i)
                        
                        dati = {
                            'numero_foglio': numero_foglio,
                            'anno': anno_selezionato,
                            'cacciatore_id': None,
                            'tipo': 'A3',
                            'stato': 'DISPONIBILE'
                        }
                        
                        try:
                            st.session_state.db.aggiungi_foglio_caccia(dati)
                            fogli_creati += 1
                        except:
                            fogli_saltati += 1
                    
                    if fogli_creati > 0:
                        st.success(f"✅ Creati {fogli_creati} fogli!")
                        if fogli_saltati > 0:
                            st.info(f"ℹ️ {fogli_saltati} fogli già esistenti")
                        st.balloons()
                        
                        # Forza il refresh
                        import time
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.warning("⚠️ Tutti i fogli esistono già!")
                    
                except Exception as e:
                    st.error(f"⚠️ Errore: {str(e)}")

def show_consegna_fogli():
    """Registrazione consegna fogli da fornitore"""
    st.subheader("📥 Consegna Fogli da Fornitore")
    
    st.info("Registra i fogli consegnati dal fornitore (es. Ilbaa)")
    
    anno_corrente = dt.datetime.now().year
    
    # Recupera fogli disponibili - ordinati alfabeticamente
    fogli_disponibili = st.session_state.db.get_fogli_anno_ordinati_per_cacciatore(anno_corrente, 'DISPONIBILE')
    
    if not fogli_disponibili:
        st.warning("⚠️ Nessun foglio disponibile da consegnare")
        st.info("Crea prima i fogli nella tab 'Gestione Fogli'")
        return
    
    with st.form("form_consegna_fogli"):
        st.markdown("**Informazioni Consegna**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            data_consegna = st.date_input(
                "Data Consegna *",
                value=dt.datetime.now().date(),
                format="DD/MM/YYYY"
            )
            
            consegnato_da = st.text_input(
                "Consegnato Da *",
                placeholder="es. Ilbaa",
                value="Ilbaa"
            )
        
        with col2:
            # Selezione fogli multipli
            fogli_selezionati = st.multiselect(
                "Fogli Consegnati *",
                options=[f['numero_foglio'] for f in fogli_disponibili],
                help="Seleziona uno o più fogli consegnati"
            )
        
        note = st.text_area("Note", placeholder="Note sulla consegna...")
        
        st.markdown("---")
        
        submitted = st.form_submit_button("💾 Registra Consegna", 
                                          type="primary", 
                                          use_container_width=True)
        
        if submitted:
            if not fogli_selezionati or not consegnato_da:
                st.error("⚠️ Seleziona almeno un foglio e indica chi l'ha consegnato")
            else:
                try:
                    count = 0
                    for numero_foglio in fogli_selezionati:
                        # Trova l'ID del foglio
                        foglio = next((f for f in fogli_disponibili 
                                     if f['numero_foglio'] == numero_foglio), None)
                        
                        if foglio:
                            dati = {
                                'cacciatore_id': None,
                                'data_consegna': data_consegna.strftime('%Y-%m-%d'),
                                'consegnato_da': consegnato_da.strip(),
                                'data_rilascio': None,
                                'rilasciato_a': None,
                                'data_restituzione': None,
                                'restituito_da': None,
                                'stato': 'CONSEGNATO',
                                'note': note.strip() if note else None
                            }
                            
                            st.session_state.db.modifica_foglio_caccia(foglio['id'], dati)
                            count += 1
                    
                    st.success(f"✅ Registrati {count} fogli consegnati!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"⚠️ Errore: {str(e)}")



def show_restituzione_fogli():
    """Restituzione fogli da cacciatori"""
    st.subheader("🔄 Restituzione Fogli da Cacciatori")
    
    # CSS per UI compatta stile Excel (solo per questa sezione)
    st.markdown("""
    <style>
    /* ============================================
       CSS COMPATTO STILE EXCEL - Restituzione Fogli
       Variabili modificabili in cima
       ============================================ */
    :root {
        --row-height: 30px;
        --font-size: 12px;
        --cell-padding-y: 4px;
        --cell-padding-x: 8px;
        --header-bg: #f0f2f6;
        --border-color: #dfe1e6;
        --zebra-bg: #f8f9fa;
    }
    
    /* Form restituzione - riduzione spacing */
    div[data-testid="stForm"] {
        padding: 12px 16px !important;
        margin-bottom: 16px !important;
    }
    
    div[data-testid="stForm"] label {
        font-size: 13px !important;
        margin-bottom: 4px !important;
    }
    
    div[data-testid="stForm"] input,
    div[data-testid="stForm"] textarea,
    div[data-testid="stForm"] select {
        font-size: 13px !important;
        padding: 6px 10px !important;
        min-height: 32px !important;
    }
    
    div[data-testid="stForm"] textarea {
        min-height: 60px !important;
    }
    
    div[data-testid="stForm"] button[kind="primary"] {
        padding: 8px 16px !important;
        font-size: 13px !important;
        height: auto !important;
        min-height: 36px !important;
    }
    
    /* Tabella Fogli Restituiti - stile Excel compatto */
    /* Target: sezione dopo il separatore della tabella */
    div[data-testid="stVerticalBlock"]:has(> div > div > p:first-child strong:contains("N. Foglio")) {
        font-size: var(--font-size) !important;
    }
    
    /* Header tabella */
    div[data-testid="column"] > div > p > strong {
        font-size: 13px !important;
        font-weight: 600 !important;
        color: #262730 !important;
    }
    
    /* Righe tabella - padding ridotto */
    div[data-testid="column"] > div > p:not(:has(strong)) {
        font-size: var(--font-size) !important;
        padding: var(--cell-padding-y) var(--cell-padding-x) !important;
        margin: 0 !important;
        line-height: 1.4 !important;
    }
    
    /* Contenitori riga */
    div[data-testid="column"] {
        padding: 2px 4px !important;
    }
    
    /* Bottoni azioni - compatti */
    div[data-testid="column"] button {
        font-size: 11px !important;
        padding: 4px 8px !important;
        height: auto !important;
        min-height: 26px !important;
        margin: 2px !important;
        border-radius: 4px !important;
    }
    
    /* Bottoni modifica e elimina - icone più piccole */
    div[data-testid="column"] button:contains("Modifica"),
    div[data-testid="column"] button:contains("Elimina") {
        font-size: 10px !important;
        padding: 3px 6px !important;
        min-height: 24px !important;
    }
    
    /* Bottoni Salva/Annulla in edit mode */
    div[data-testid="column"] button:contains("Salva"),
    div[data-testid="column"] button:contains("Annulla") {
        font-size: 11px !important;
        padding: 5px 10px !important;
        min-height: 28px !important;
    }
    
    /* Campi edit mode - compatti */
    div[data-testid="column"] input[type="date"],
    div[data-testid="column"] input[type="text"],
    div[data-testid="column"] textarea {
        font-size: 12px !important;
        padding: 4px 8px !important;
        min-height: 28px !important;
    }
    
    div[data-testid="column"] textarea {
        min-height: 60px !important;
    }
    
    div[data-testid="column"] label {
        font-size: 11px !important;
        margin-bottom: 2px !important;
    }
    
    /* Separatori riga - border sottile */
    hr[style*="opacity: 0.3"] {
        margin: 2px 0 !important;
        border-color: var(--border-color) !important;
        opacity: 0.5 !important;
    }
    
    /* Zebra striping - alternanza righe (simulato con nth-child) */
    /* Nota: Streamlit non supporta direttamente nth-child sulle righe,
       ma possiamo applicare un background leggero alle colonne pari */
    
    /* Riduzione spaziatura verticale generale nella sezione tabella */
    div[data-testid="stVerticalBlock"] > div {
        gap: 4px !important;
    }
    
    /* Info badge totale fogli */
    div[data-testid="stAlert"] p {
        font-size: 12px !important;
        padding: 6px 12px !important;
        margin: 0 !important;
    }
    
    /* Warning/error banners - compatti */
    div[data-testid="stAlert"] {
        padding: 8px 12px !important;
        margin-bottom: 12px !important;
    }
    
    div[data-testid="stAlert"] p strong {
        font-size: 13px !important;
    }
    
    /* Success messages - compatti */
    div[data-testid="stSuccess"],
    div[data-testid="stWarning"],
    div[data-testid="stError"] {
        padding: 6px 10px !important;
        font-size: 12px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.info("Registra la restituzione di fogli compilati")
    
    anno_corrente = dt.datetime.now().year
    
    # Recupera fogli rilasciati - ordinati alfabeticamente
    fogli_rilasciati = st.session_state.db.get_fogli_anno_ordinati_per_cacciatore(anno_corrente, 'RILASCIATO')
    
    if not fogli_rilasciati:
        st.warning("⚠️ Nessun foglio rilasciato da restituire")
        st.info("Rilascia prima i fogli ai cacciatori nella tab 'Rilascio Fogli'")
        return
    
    with st.form("form_restituzione_fogli"):
        st.markdown("**Informazioni Restituzione**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Selezione foglio
            foglio_selezionato = st.selectbox(
                "Foglio da Restituire *",
                options=[(f['numero_foglio'], 
                         f"{f['numero_foglio']} - {f.get('cognome', '')} {f.get('nome', '')}") 
                        for f in fogli_rilasciati],
                format_func=lambda x: x[1]
            )
            
            data_restituzione = st.date_input(
                "Data Restituzione *",
                value=dt.datetime.now().date(),
                format="DD/MM/YYYY"
            )
        
        with col2:
            restituito_da = st.text_input(
                "Restituito Da",
                placeholder="Nome persona"
            )
        
        note = st.text_area("Note", placeholder="Note sulla restituzione...")
        
        st.markdown("---")
        
        submitted = st.form_submit_button("💾 Registra Restituzione", 
                                          type="primary", 
                                          use_container_width=True)
        
        if submitted:
            try:
                # Trova il foglio
                numero_foglio = foglio_selezionato[0]
                foglio = next((f for f in fogli_rilasciati 
                             if f['numero_foglio'] == numero_foglio), None)
                
                if foglio:
                    dati = {
                        'cacciatore_id': foglio.get('cacciatore_id'),
                        'data_consegna': foglio.get('data_consegna'),
                        'consegnato_da': foglio.get('consegnato_da'),
                        'data_rilascio': foglio.get('data_rilascio'),
                        'rilasciato_a': foglio.get('rilasciato_a'),
                        'data_restituzione': data_restituzione.strftime('%Y-%m-%d'),
                        'restituito_da': restituito_da.strip() if restituito_da else None,
                        'stato': 'RESTITUITO',
                        'note': note.strip() if note else None
                    }
                    
                    st.session_state.db.modifica_foglio_caccia(foglio['id'], dati)
                    
                    st.success(f"✅ Foglio {numero_foglio} restituito correttamente!")
                    st.rerun()
                
            except Exception as e:
                st.error(f"⚠️ Errore: {str(e)}")
    
    
    # Mostra fogli restituiti
    st.markdown("---")
    st.subheader("📋 Fogli Restituiti")
    
    # Initialize session state for edit/delete
    if 'resti_selected_id' not in st.session_state:
        st.session_state.resti_selected_id = None
    if 'resti_edit_mode' not in st.session_state:
        st.session_state.resti_edit_mode = False
    if 'resti_delete_confirm' not in st.session_state:
        st.session_state.resti_delete_confirm = False
    
    # Recupera fogli restituiti - ordinati alfabeticamente
    fogli_restituiti = st.session_state.db.get_fogli_anno_ordinati_per_cacciatore(anno_corrente, 'RESTITUITO')
    
    if fogli_restituiti:
        # Mostra totale
        st.info(f"📄 Totale fogli restituiti: {len(fogli_restituiti)}")
        
        # Batch query per conteggio allegati (efficiente)
        num_fogli_list = [f.get('numero_foglio') for f in fogli_restituiti]
        allegati_counts = st.session_state.db.count_allegati_per_foglio(num_fogli_list)
        
        # Batch query per recuperare tutti gli allegati (per evitare query ripetute nel loop)
        allegati_map = {}  # Mappa numero_foglio -> lista allegati
        for numero_foglio in num_fogli_list:
            allegati_map[numero_foglio] = st.session_state.db.get_restituzione_allegati(numero_foglio)
        
        # Tabella con bottoni per aprire fogli
        # Intestazione
        header_cols = st.columns([1.5, 1.5, 1.5, 1.3, 1.3, 1.2])
        headers = ['N. Foglio', 'Cognome', 'Nome', 'Data Rilascio', 'Data Restituzione', 'Apri foglio']
        for col, header in zip(header_cols, headers):
            col.markdown(f"**{header}**")
        
        st.markdown("---")
        
        # Mappa numero_foglio -> record completo per azioni
        id_map = {}
        
        # Righe con bottoni
        for idx, f in enumerate(fogli_restituiti):
            row_cols = st.columns([1.5, 1.5, 1.5, 1.3, 1.3, 1.2])
            
            numero_foglio = f.get('numero_foglio', 'N/A')
            cognome = f.get('cognome', '') or 'N/A'
            nome = f.get('nome', '') or 'N/A'
            data_rilascio_fmt = fmt_date_it(f.get('data_rilascio', '')) or 'N/A'
            data_restituzione_fmt = fmt_date_it(f.get('data_restituzione', '')) or 'N/A'
            
            # Conteggio allegati
            allegati_count = allegati_counts.get(numero_foglio, 0)
            
            # Colonne dati
            row_cols[0].text(numero_foglio)
            row_cols[1].text(cognome)
            row_cols[2].text(nome)
            row_cols[3].text(data_rilascio_fmt)
            row_cols[4].text(data_restituzione_fmt)
            
            # Colonna Apri foglio con bottone per aprire SCANSIONE
            if allegati_count > 0:
                # Recupera allegati dalla mappa (già caricati)
                allegati = allegati_map.get(numero_foglio, [])
                
                if allegati and len(allegati) > 0:
                    # Prendi il primo allegato
                    primo_allegato = allegati[0]
                    scan_path = primo_allegato.get('file_path', None)
                    
                    allegati_badge = f" ({allegati_count})" if allegati_count > 1 else ""
                    button_label = f"📂 Foglio{allegati_badge}"
                    button_key = f"apri_scan_{numero_foglio}_{idx}"
                    
                    if row_cols[5].button(button_label, key=button_key, help=f"Apri: {os.path.basename(scan_path) if scan_path else 'N/A'}"):
                        if scan_path and os.path.exists(scan_path):
                            try:
                                if sys.platform.startswith('win'):
                                    os.startfile(scan_path)
                                    st.success(f"✅ Scansione aperta: {os.path.basename(scan_path)}")
                                elif sys.platform == 'darwin':
                                    import subprocess
                                    subprocess.call(['open', scan_path])
                                    st.success(f"✅ Scansione aperta")
                                elif sys.platform.startswith('linux'):
                                    import subprocess
                                    subprocess.call(['xdg-open', scan_path])
                                    st.success(f"✅ Scansione aperta")
                            except Exception as e:
                                st.error(f"Errore: {e}")
                        else:
                            st.error(f"❌ File scansione non trovato")
                else:
                    row_cols[5].text("—")
            else:
                # Nessun allegato - mostra solo icona
                row_cols[5].text("—")
            
            # Separatore tra righe
            if idx < len(fogli_restituiti) - 1:
                st.markdown("<hr style='margin: 3px 0; opacity: 0.1;'>", unsafe_allow_html=True)
            
            # Salva record completo per id
            id_map[numero_foglio] = f
        
        st.markdown("---")
        
        # Selezione record e azioni
        st.markdown("**Azioni sul Record Selezionato**")
        
        col_select, col_actions = st.columns([3, 2])
        
        with col_select:
            # Selectbox per scegliere il record
            foglio_options = [(f['numero_foglio'], 
                              f"{f['numero_foglio']} - {f.get('cognome', '')} {f.get('nome', '')}".strip()) 
                             for f in fogli_restituiti]
            
            selected_foglio = st.selectbox(
                "Seleziona Foglio",
                options=[opt[0] for opt in foglio_options],
                format_func=lambda x: next(opt[1] for opt in foglio_options if opt[0] == x),
                key="select_foglio_resti"
            )
            
            if selected_foglio:
                st.session_state.resti_selected_id = id_map[selected_foglio]['id']
        
        with col_actions:
            st.write("")  # Spacing
            act_col1, act_col2 = st.columns(2)
            
            with act_col1:
                if st.button("✏️ Modifica", key="btn_modifica_resti", use_container_width=True):
                    st.session_state.resti_edit_mode = True
                    st.session_state.resti_delete_confirm = False
                    st.rerun()
            
            with act_col2:
                if st.button("🗑️ Elimina", key="btn_elimina_resti", use_container_width=True):
                    st.session_state.resti_delete_confirm = True
                    st.session_state.resti_edit_mode = False
                    st.rerun()
        
        # Delete confirmation banner
        if st.session_state.resti_delete_confirm and st.session_state.resti_selected_id:
            selected_record = next((f for f in fogli_restituiti 
                                   if f['id'] == st.session_state.resti_selected_id), None)
            
            if selected_record:
                cognome = selected_record.get('cognome', '')
                nome = selected_record.get('nome', '')
                numero_foglio = selected_record.get('numero_foglio', '')
                nome_completo = f"{cognome} {nome}" if cognome and nome else selected_record.get('rilasciato_a', 'N/A')
                
                st.error(f"⚠️ **Confermi eliminazione restituzione per foglio {numero_foglio} – {nome_completo}?**")
                
                conf_col1, conf_col2, conf_col3 = st.columns([2, 2, 6])
                
                with conf_col1:
                    if st.button("✅ Conferma eliminazione", type="primary", key="confirm_del_resti"):
                        try:
                            st.session_state.db.annulla_restituzione_foglio(st.session_state.resti_selected_id)
                            st.session_state.resti_delete_confirm = False
                            st.session_state.resti_selected_id = None
                            st.success(f"✅ Restituzione foglio {numero_foglio} annullata!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"⚠️ Errore: {str(e)}")
                
                with conf_col2:
                    if st.button("❌ Annulla", key="cancel_del_resti"):
                        st.session_state.resti_delete_confirm = False
                        st.rerun()
        
        # Edit mode panel
        if st.session_state.resti_edit_mode and st.session_state.resti_selected_id:
            selected_record = next((f for f in fogli_restituiti 
                                   if f['id'] == st.session_state.resti_selected_id), None)
            
            if selected_record:
                st.markdown("---")
                st.markdown(f"**✏️ Modifica Foglio {selected_record['numero_foglio']} - {selected_record.get('cognome', '')} {selected_record.get('nome', '')}**")
                
                edit_col1, edit_col2 = st.columns(2)
                
                with edit_col1:
                    # Parse current date
                    data_rest_current = selected_record.get('data_restituzione', '')
                    if data_rest_current:
                        try:
                            if isinstance(data_rest_current, str):
                                data_rest_obj = dt.datetime.strptime(data_rest_current, '%Y-%m-%d').date()
                            else:
                                data_rest_obj = data_rest_current
                        except:
                            data_rest_obj = dt.datetime.now().date()
                    else:
                        data_rest_obj = dt.datetime.now().date()
                    
                    new_data_rest = st.date_input(
                        "Data Restituzione *",
                        value=data_rest_obj,
                        key="edit_data_resti",
                        format="DD/MM/YYYY"
                    )
                    
                    new_restituito_da = st.text_input(
                        "Restituito Da",
                        value=selected_record.get('restituito_da', '') or "",
                        key="edit_restituito_resti"
                    )
                
                with edit_col2:
                    new_note = st.text_area(
                        "Note",
                        value=selected_record.get('note', '') or "",
                        key="edit_note_resti",
                        height=100
                    )
                
                btn_col1, btn_col2 = st.columns(2)
                
                with btn_col1:
                    if st.button("💾 Salva Modifiche", key="save_edit_resti", type="primary", use_container_width=True):
                        try:
                            if not new_data_rest:
                                st.error("⚠️ La data restituzione è obbligatoria")
                            else:
                                st.session_state.db.aggiorna_restituzione_foglio(
                                    st.session_state.resti_selected_id,
                                    new_data_rest,
                                    new_restituito_da.strip() if new_restituito_da else None,
                                    new_note.strip() if new_note else None
                                )
                                st.session_state.resti_edit_mode = False
                                st.success(f"✅ Foglio {selected_record['numero_foglio']} aggiornato!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"⚠️ Errore: {str(e)}")
                
                with btn_col2:
                    if st.button("❌ Annulla Modifica", key="cancel_edit_resti", use_container_width=True):
                        st.session_state.resti_edit_mode = False
                        st.rerun()
        
        # ========== GESTIONE ALLEGATI (SCANSIONI) ==========
        if st.session_state.resti_selected_id:
            selected_record = next((f for f in fogli_restituiti 
                                   if f['id'] == st.session_state.resti_selected_id), None)
            
            if selected_record:
                st.markdown("---")
                numero_foglio = selected_record['numero_foglio']
                
                # Base path UNC per scansioni
                BASE_RESTI = r"\\serrenti.local\Gestione\Dati\Condivisa\Vigilanza\CACCIA\FOGLI CACCIA A3 Annuali\FOGLI CACCIA RESTITUITI\2026"
                
                # Sanitize numero foglio per nome cartella
                def sanitize_filename(name):
                    # Rimuovi caratteri non validi per Windows
                    invalid_chars = '<>:"/\\|?*'
                    for char in invalid_chars:
                        name = name.replace(char, '_')
                    return name.strip()
                
                folder_name = sanitize_filename(numero_foglio)
                folder_path = os.path.join(BASE_RESTI, folder_name)
                
                # Recupera allegati esistenti
                allegati = st.session_state.db.get_restituzione_allegati(numero_foglio)
                allegati_count = len(allegati)
                
                with st.expander(f"📎 Fogli Scansionati ({allegati_count})", expanded=False):
                    # Lista allegati esistenti
                    if allegati:
                        st.markdown("**File caricati:**")
                        
                        # Init session state for delete confirmation
                        if 'delete_allegato_id' not in st.session_state:
                            st.session_state.delete_allegato_id = None
                        
                        for allegato in allegati:
                            allegato_id = allegato['id']
                            file_name = allegato['file_name']
                            file_path = allegato['file_path']
                            uploaded_at = allegato['uploaded_at']
                            
                            # Check if delete confirmation for this file
                            if st.session_state.delete_allegato_id == allegato_id:
                                st.warning(f"⚠️ Confermi eliminazione di **{file_name}**?")
                                del_col1, del_col2 = st.columns(2)
                                with del_col1:
                                    if st.button("✅ Conferma", key=f"conf_del_{allegato_id}"):
                                        try:
                                            # Delete from DB and get file info
                                            file_info = st.session_state.db.delete_restituzione_allegato(allegato_id)
                                            
                                            # Delete physical file
                                            if file_info and os.path.exists(file_info['file_path']):
                                                try:
                                                    os.remove(file_info['file_path'])
                                                except Exception as file_err:
                                                    st.warning(f"File eliminato dal DB ma non dal disco: {str(file_err)}")
                                            
                                            st.session_state.delete_allegato_id = None
                                            st.success(f"✅ File {file_name} eliminato!")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"⚠️ Errore: {str(e)}")
                                
                                with del_col2:
                                    if st.button("❌ Annulla", key=f"canc_del_{allegato_id}"):
                                        st.session_state.delete_allegato_id = None
                                        st.rerun()
                            else:
                                # Normal display
                                col_file, col_date, col_down, col_del = st.columns([3, 2, 1, 1])
                                
                                col_file.text(file_name)
                                col_date.text(uploaded_at[:16] if uploaded_at else '')  # YYYY-MM-DD HH:MM
                                
                                # Download button
                                if os.path.exists(file_path):
                                    try:
                                        with open(file_path, 'rb') as f:
                                            file_bytes = f.read()
                                        col_down.download_button(
                                            "📥", 
                                            file_bytes, 
                                            file_name=file_name,
                                            key=f"down_{allegato_id}"
                                        )
                                    except Exception as e:
                                        col_down.text("❌")
                                else:
                                    col_down.text("❌")
                                
                                # Delete button
                                if col_del.button("🗑️", key=f"del_{allegato_id}"):
                                    st.session_state.delete_allegato_id = allegato_id
                                    st.rerun()
                                
                                # Image preview
                                if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                                    if os.path.exists(file_path):
                                        try:
                                            st.image(file_path, width=400, caption=file_name)
                                        except:
                                            pass
                        
                        st.markdown("---")
                    
                    # Upload section
                    st.markdown("**Carica nuove scansioni:**")
                    
                    uploaded_files = st.file_uploader(
                        "Sfoglia file...",
                        type=['pdf', 'jpg', 'jpeg', 'png'],
                        accept_multiple_files=True,
                        key=f"upload_resti_{numero_foglio}"
                    )
                    
                    if uploaded_files:
                        st.info(f"📄 {len(uploaded_files)} file selezionati")
                        
                        if st.button("💾 Salva Scansioni", key=f"btn_save_scan_{numero_foglio}", type="primary"):
                            try:
                                # Verifica/crea cartella
                                try:
                                    os.makedirs(folder_path, exist_ok=True)
                                except Exception as mkdir_err:
                                    st.error(f"⚠️ Errore creazione cartella UNC: {str(mkdir_err)}")
                                    st.info(f"Percorso: {folder_path}")
                                    st.stop()
                                
                                saved_count = 0
                                errors = []
                                
                                for uploaded_file in uploaded_files:
                                    try:
                                        # Get current timestamp for naming
                                        timestamp = dt.datetime.now().strftime('%Y-%m-%d')
                                        
                                        # Get file extension
                                        file_ext = os.path.splitext(uploaded_file.name)[1]
                                        
                                        # Find next available number
                                        base_name = f"scan_{timestamp}"
                                        counter = 1
                                        final_name = f"{base_name}_001{file_ext}"
                                        final_path = os.path.join(folder_path, final_name)
                                        
                                        while os.path.exists(final_path):
                                            counter += 1
                                            final_name = f"{base_name}_{counter:03d}{file_ext}"
                                            final_path = os.path.join(folder_path, final_name)
                                        
                                        # Save file
                                        with open(final_path, 'wb') as f:
                                            f.write(uploaded_file.getbuffer())
                                        
                                        # Add to database
                                        st.session_state.db.add_restituzione_allegato(
                                            numero_foglio,
                                            final_name,
                                            final_path,
                                            uploaded_by='SISTEMA'
                                        )
                                        
                                        saved_count += 1
                                        
                                    except Exception as file_err:
                                        errors.append(f"{uploaded_file.name}: {str(file_err)}")
                                
                                if saved_count > 0:
                                    st.success(f"✅ {saved_count} file salvati con successo!")
                                
                                if errors:
                                    st.error("⚠️ Errori durante il salvataggio:")
                                    for err in errors:
                                        st.text(err)
                                
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"⚠️ Errore generale: {str(e)}")
                    
                    # Optional: Open folder button (Windows only)
                    if os.name == 'nt':  # Windows
                        if st.button("📂 Apri Cartella", key=f"open_folder_{numero_foglio}"):
                            try:
                                if os.path.exists(folder_path):
                                    os.startfile(folder_path)
                                else:
                                    st.warning("Cartella non ancora creata")
                            except Exception as e:
                                st.error(f"⚠️ Errore apertura cartella: {str(e)}")
    
    
    else:
        st.info("Nessun foglio ancora restituito")

