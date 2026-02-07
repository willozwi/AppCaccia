# Report Tecnico Operativo - AppCaccia

**Data**: 2026-02-06
**Versione analizzata**: commit iniziale (ec1d166)
**Analista**: Claude Code (analisi automatizzata)

---

## A) Panoramica

AppCaccia è un gestionale per la Polizia Locale (Sardegna) dedicato alla gestione di cacciatori, fogli caccia A3, libretti regionali, autorizzazioni RAS e documenti correlati. Stack: **Python 3 + Streamlit 1.31 + SQLite** (WAL mode). L'app è monolitica, single-user, pensata per uso locale/intranet.

Il codebase conta ~5.500 righe Python distribuite su 12 file, con un database SQLite a 7 tabelle. L'architettura è semplice: `app.py` funge da router/dashboard, le pagine in `pages/` rendono UI con accesso diretto al DB via `database.py`. Non esiste autenticazione, API REST, né caching.

I problemi principali sono: **bug critici nel parser date** (crash a runtime), **incoerenza stato/checkbox** nei fogli caccia, **resource leak** nelle connessioni DB, e un **debito tecnico significativo** nel file `fogli_caccia.py` (1.500+ righe). La persistenza dati è generalmente funzionale ma con lacune nella gestione errori e nell'integrità referenziale.

---

## B) Mappa del progetto

```
AppCaccia/
├── app.py                      # Entrypoint, routing sidebar, dashboard (257 righe)
├── database.py                 # Wrapper SQLite: 7 tabelle, 50+ metodi (1.295 righe)
├── constants.py                # Enum stati, config (115 righe)
├── excel_parser.py             # Parser Excel + template RAS (399 righe)
├── requirements.txt            # streamlit, pandas, openpyxl, python-docx
│
├── pages/                      # Moduli UI Streamlit
│   ├── anagrafe_cacciatori.py  # CRUD cacciatori (386 righe)
│   ├── libretti_regionali.py   # Gestione libretti annuali (282 righe)
│   ├── fogli_caccia.py         # Gestione fogli A3 + restituzioni (1.512 righe) ⚠️
│   ├── import_fogli.py         # Import massivo da Excel (517 righe)
│   ├── autorizzazioni_ras.py   # Autorizzazioni RAS (344 righe)
│   ├── documenti.py            # Upload/archivio documenti (396 righe)
│   └── report_statistiche.py   # Dashboard e report (588 righe)
│
├── gestionale_caccia.db        # Database SQLite (~330KB)
├── import_debug.log            # Log operazioni import
├── migrate_stati.py            # Migrazione DB one-shot
├── avvia.bat / avvia.sh        # Script di avvio
└── *.md                        # Documentazione (in italiano)
```

**Tabelle DB**: `cacciatori`, `libretti_regionali`, `fogli_caccia`, `autorizzazioni_ras`, `documenti`, `log_attivita`, `restituzioni_allegati`

---

## C) Flussi critici

### 1. Ciclo di vita Foglio Caccia A3
**File**: `pages/fogli_caccia.py`, `database.py`
**Flusso**: DISPONIBILE → CONSEGNATO → RILASCIATO → RESTITUITO
**Operazioni**: Creazione batch → Consegna (checkbox+data) → Rilascio a cacciatore → Restituzione con scansione allegata
**Rischio**: Incoerenza tra campo `consegnato` (bool) e `stato` (enum) in `toggle_consegnato()` — **CORRETTO in questa patch**

### 2. Import massivo da Excel
**File**: `pages/import_fogli.py`, `excel_parser.py`
**Flusso**: Scansione cartella → Parse Excel (strutturato/RAS) → Match/creazione cacciatore → Inserimento foglio
**Rischio**: `_parse_date()` crashava a runtime per bug su variabile `dt` — **CORRETTO in questa patch**

### 3. Gestione Autorizzazioni RAS
**File**: `pages/autorizzazioni_ras.py`, `database.py`
**Flusso**: Nuova richiesta → Aggiornamento stato/protocollo → Approvazione/Rifiuto
**Rischio**: Connection leak su eccezione, nessun audit log su update — **CORRETTO in questa patch**

### 4. Anagrafe Cacciatori
**File**: `pages/anagrafe_cacciatori.py`, `database.py`
**Flusso**: Inserimento → Ricerca → Modifica → Disattivazione (soft delete)
**Rischio**: Basso. CRUD ben strutturato con validazione UI.

### 5. Upload Documenti
**File**: `pages/documenti.py`, `database.py`
**Flusso**: Upload file → Salvataggio su `./documenti/` → Record in DB
**Rischio**: Path basato su `os.getcwd()` (non deterministico), connection leak.

### 6. Report e Statistiche
**File**: `pages/report_statistiche.py`, `database.py`
**Flusso**: Query aggregate → Rendering metriche/grafici → Export CSV
**Rischio**: Basso. Operazioni di sola lettura.

### 7. Gestione Libretti Regionali
**File**: `pages/libretti_regionali.py`, `database.py`
**Flusso**: Creazione libretto annuale → Gestione stato → Scadenza
**Rischio**: Basso. Ben integrato con constants.py.

---

## D) Problemi

### BLOCCANTI

| # | Problema | File | Linee | Impatto | Fix |
|---|----------|------|-------|---------|-----|
| B1 | **`_parse_date()` crash a runtime**: `dt.strftime()` chiamato sul modulo invece che sull'oggetto; `datetime()` usato senza import; variabile `dt` sovrascrive il modulo | `excel_parser.py` | 366-376 | Import Excel completamente non funzionante per date in formato stringa o numerico Excel | **CORRETTO**: usato `dt_obj` come variabile locale |
| B2 | **`toggle_consegnato()` non aggiorna `stato`**: il campo bool `consegnato` cambia ma `stato` resta invariato, creando dati incoerenti | `database.py` | 654-694 | Fogli marcati come consegnati nel checkbox ma con stato DISPONIBILE nei filtri/report | **CORRETTO**: allineato logica con `set_consegnato()` |

### ALTI

| # | Problema | File | Linee | Impatto | Fix |
|---|----------|------|-------|---------|-----|
| A1 | **Connection leak** su eccezione in query dirette (no try/finally) | `autorizzazioni_ras.py` | 44-64, 210-240 | Connessioni SQLite non chiuse → DB locked dopo molte operazioni | **CORRETTO**: aggiunto try/finally + rollback |
| A2 | **Nessun audit log** su UPDATE autorizzazioni (SQL diretto, bypassa `database.py`) | `autorizzazioni_ras.py` | 210-240 | Modifiche non tracciate nel log attività | **CORRETTO**: aggiunto `log_attivita()` |
| A3 | **Bare except** in creazione batch fogli: tutti gli errori contati come "duplicati" | `fogli_caccia.py` | 655-659 | Errori gravi (disco pieno, corruzione) mascherati come duplicati | Distinguere `IntegrityError` da altre eccezioni |
| A4 | **Foreign key non enforce** (`PRAGMA foreign_keys=ON` mancante) | `database.py` | 20-29 | Record orfani possibili (libretti/fogli senza cacciatore) | Aggiungere pragma in `get_connection()` |
| A5 | **Path UNC hardcoded** con anno 2026 fisso | `fogli_caccia.py` | 1326 | Rottura automatica nel 2027; non funziona su Linux | Estrarre in configurazione con anno dinamico |
| A6 | **Connection leak** in pagina documenti (query dirette senza finally) | `documenti.py` | 311-334 | Stessi rischi di A1 | Wrappare in try/finally |

### MEDI

| # | Problema | File | Linee | Impatto | Fix |
|---|----------|------|-------|---------|-----|
| M1 | `fogli_caccia.py` è 1.512 righe con metodi da 680+ righe | `fogli_caccia.py` | intero | Difficile manutenzione, alto rischio di regressioni | Splitare in sotto-moduli |
| M2 | Bare except diffusi (~15 occorrenze tra `database.py` e pagine) | Multipli | Multipli | Errori silenziosamente ignorati, debug impossibile | Specificare tipo eccezione |
| M3 | CSS duplicato: 150+ righe inline in `fogli_caccia.py`, 50+ in `app.py` | `fogli_caccia.py`, `app.py` | Vari | Stile incoerente, manutenzione doppia | Centralizzare in file CSS condiviso |
| M4 | Nessun `@st.cache_data`: query DB rieseguite a ogni rerun Streamlit | Tutte le pagine | - | Performance degradata su dataset grandi | Aggiungere caching su query frequenti |
| M5 | `documenti.py` usa `os.getcwd()` per path upload | `documenti.py` | 261 | Directory documenti dipende da dove si avvia Streamlit | Usare `os.path.dirname(__file__)` |
| M6 | Operazione file upload + DB insert non atomica | `fogli_caccia.py` | 1449-1480 | File orfani su disco se insert DB fallisce | Invertire ordine o usare transazione |

### BASSI

| # | Problema | File | Linee | Impatto | Fix |
|---|----------|------|-------|---------|-----|
| L1 | Variabile `_tessera_counter` definita mai usata | `import_fogli.py` | 26 | Dead code | Rimuovere |
| L2 | Costanti di stato hardcoded in pagine (bypassano `constants.py`) | `fogli_caccia.py` | 93, 336 | Rischio disallineamento valori | Usare sempre `StatoFoglio.*` |
| L3 | Nessuna autenticazione | `app.py` | - | Accesso libero a chiunque sulla rete | Accettabile per intranet, documentare |
| L4 | `sanitize_filename()` definita inline dentro una funzione | `fogli_caccia.py` | 1329 | Ridefinita a ogni chiamata | Estrarre come utility |
| L5 | Debug print in produzione (`print(f"[DEBUG] Database path: ...")`) | `database.py` | 16 | Output spurio in console | Usare logging.debug |
| L6 | Nessuna validazione campi obbligatori nel layer DB | `database.py` | 226-261 | Errori SQLite poco informativi | Aggiungere validazione pre-insert |

---

## E) Quick Wins (10 interventi ordinati per ROI)

| # | Intervento | File | Effort | Impatto |
|---|-----------|------|--------|---------|
| 1 | ~~Fix `_parse_date()` — bug variabile `dt`~~ | `excel_parser.py` | 5 min | **CRITICO** — ✅ FATTO |
| 2 | ~~Fix `toggle_consegnato()` — sync stato~~ | `database.py` | 10 min | **CRITICO** — ✅ FATTO |
| 3 | ~~Fix connection leak autorizzazioni~~ | `autorizzazioni_ras.py` | 10 min | **ALTO** — ✅ FATTO |
| 4 | Aggiungere `PRAGMA foreign_keys=ON` | `database.py:27` | 1 riga | **ALTO** — previene record orfani |
| 5 | Sostituire `except:` con `except Exception as e:` | Multipli | 30 min | **MEDIO** — debug possibile |
| 6 | Rendere anno dinamico nel path UNC | `fogli_caccia.py:1326` | 5 min | **ALTO** — evita rottura nel 2027 |
| 7 | Wrappare query documenti in try/finally | `documenti.py` | 10 min | **MEDIO** — previene leak |
| 8 | Sostituire `print("[DEBUG]...")` con `logging.debug()` | `database.py:16` | 2 min | **BASSO** — output pulito |
| 9 | Rimuovere dead code `_tessera_counter` | `import_fogli.py:26` | 1 min | **BASSO** — pulizia |
| 10 | Aggiungere `@st.cache_data` su `get_tutti_cacciatori()` | pagine | 15 min | **MEDIO** — performance |

---

## F) Piano di Refactor

### Milestone 1 — Stabilizzazione (priorità immediata)
- [x] Fix `_parse_date()` in `excel_parser.py`
- [x] Fix `toggle_consegnato()` in `database.py`
- [x] Fix connection leak in `autorizzazioni_ras.py`
- [ ] Aggiungere `PRAGMA foreign_keys=ON` in `database.py`
- [ ] Sostituire tutti i `except:` con `except Exception as e:` (15 occorrenze)
- [ ] Fix path UNC hardcoded (anno dinamico + config)
- [ ] Fix connection leak in `documenti.py`
- [ ] Validazione campi obbligatori in `aggiungi_cacciatore()` e `aggiungi_foglio_caccia()`

### Milestone 2 — Refactoring strutturale
- [ ] Splitare `fogli_caccia.py` in sotto-moduli (`gestione/`, `consegna/`, `restituzione/`, `allegati/`)
- [ ] Estrarre query dirette dalle pagine → metodi in `database.py`
- [ ] Centralizzare CSS in file condiviso
- [ ] Estrarre `sanitize_filename()`, `fmt_date_it()`, `highlight_stato()` in `utils.py`
- [ ] Aggiungere `@st.cache_data` sulle query di sola lettura
- [ ] Sostituire magic numbers/strings con costanti in `constants.py`

### Milestone 3 — Hardening e qualità
- [ ] Implementare autenticazione base (opzionale per intranet)
- [ ] Aggiungere type hints completi su tutte le funzioni
- [ ] Implementare test unitari per `database.py` e `excel_parser.py`
- [ ] Creare `config.py` per path configurabili (UNC, documenti, DB)
- [ ] Documentare in `.env.example` le variabili di configurazione
- [ ] Atomic file upload (DB record + file write in transazione)
- [ ] Monitoraggio: logging strutturato su file con rotazione

---

## G) Patch applicate

### Fix 1: Crash `_parse_date()` in `excel_parser.py`
**Causa**: Linea 367 chiamava `dt.strftime()` sul modulo `datetime` aliasato come `dt` invece che sull'oggetto `dt_obj`. Linea 373 usava `datetime(...)` non importato e sovrascriveva la variabile `dt` col risultato, rendendo impossibili chiamate successive a `dt.timedelta()`.

**File**: `excel_parser.py:366-376`

**Fix**: Usato `dt_obj` come variabile locale per il risultato del parsing, evitando shadowing del modulo.

**Verifica manuale**:
```python
# Creare un file Excel con date in formato "15/01/2026" (stringa)
# e con date in formato numerico Excel (es. 46042)
# Importare tramite "Import Fogli Massivo"
# Verificare che le date vengano correttamente parsate
# Pre-fix: crash con AttributeError
# Post-fix: date convertite in YYYY-MM-DD
```

### Fix 2: Incoerenza stato in `toggle_consegnato()` (`database.py`)
**Causa**: Il metodo aggiornava solo il campo bool `consegnato` senza toccare il campo `stato`, creando divergenza. Es: checkbox ON ma stato resta DISPONIBILE.

**File**: `database.py:654-694`

**Fix**: Replicata la stessa logica di `set_consegnato()` — quando `consegnato=1` → `stato='CONSEGNATO'`, quando `consegnato=0` e stato era CONSEGNATO → `stato='DISPONIBILE'`, altrimenti stato preservato.

**Verifica manuale**:
```
1. Aprire "Fogli Caccia A3" → tab "Gestione Fogli"
2. Trovare un foglio con stato DISPONIBILE
3. Cliccare il toggle/checkbox "Consegnato"
4. Verificare che lo stato passi a CONSEGNATO
5. Togliere il checkbox
6. Verificare che lo stato torni a DISPONIBILE
7. Su un foglio RILASCIATO: togliere consegnato → stato deve restare RILASCIATO
```

### Fix 3: Connection leak e audit trail in `autorizzazioni_ras.py`
**Causa**: Query dirette al DB senza `try/finally` — se un'eccezione occorreva tra `get_connection()` e `conn.close()`, la connessione restava aperta. Inoltre l'UPDATE delle autorizzazioni non veniva registrato nel log attività.

**File**: `autorizzazioni_ras.py:44-64, 210-240`

**Fix**: Wrappate entrambe le sezioni in `try/except/finally` con `conn.close()` garantito. Aggiunto `rollback()` su errore nell'update. Aggiunto `log_attivita()` dopo commit riuscito.

**Verifica manuale**:
```
1. Aprire "Autorizzazioni RAS" → "Elenco Autorizzazioni"
2. Verificare che la lista si carichi senza errori
3. Modificare stato di un'autorizzazione esistente
4. Verificare che il salvataggio funzioni
5. Controllare nella Dashboard che l'attività recente mostri l'update
6. Simulare errore: chiudere DB file (chmod 000) → verificare che
   l'errore sia mostrato e la connessione venga comunque chiusa
```

---

## Note e assunzioni

1. L'app è pensata per uso locale/intranet — l'assenza di autenticazione è accettabile ma va documentata.
2. SQLite è adeguato per il volume di dati attuale (~300KB DB) ma potrebbe diventare un collo di bottiglia con accesso concorrente multi-postazione.
3. Il path UNC `\\serrenti.local\...` indica deployment su rete Windows con condivisione file — non testabile in ambiente Linux.
4. Non sono stati introdotti nuovi pacchetti/dipendenze.
5. Le patch mantengono piena compatibilità con la struttura e il DB esistenti.
