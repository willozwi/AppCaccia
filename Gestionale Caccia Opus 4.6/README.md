# Gestionale Caccia - Polizia Locale

Software completo per la gestione delle autorizzazioni e libretti di caccia per la Polizia Locale.

## 🎯 Funzionalità Principali

### 👥 Anagrafe Cacciatori
- Gestione completa anagrafica cacciatori
- Dati personali, recapiti e documenti
- Ricerca rapida e filtri avanzati
- Storico completo per ogni cacciatore

### 📖 Libretti Regionali
- Registrazione libretti per anno
- Tracciamento rilasci e scadenze
- Alert per libretti in scadenza
- Gestione stati (Attivo, Scaduto, Sospeso, Revocato)

### 📄 Fogli Caccia A3
- Gestione completa del ciclo di vita dei fogli
- Tracciamento consegne da fornitore (es. Ilbaa)
- Registrazione rilascio ai cacciatori
- Monitoraggio restituzioni
- Statistiche in tempo reale

### 🔐 Autorizzazioni RAS
- Gestione richieste autorizzazioni
- Tracciamento stato pratiche
- Numerazione protocollo
- Timeline complete

### 📁 Documenti e Modulistica
- Upload e archiviazione documenti
- Modulistica standard
- Generazione automatica report
- Export per trasmissione dati

### 📊 Report e Statistiche
- Dashboard interattiva
- Analisi per anno
- Trend temporali pluriennali
- Report personalizzati
- Export CSV/Excel

## 🚀 Installazione

### Requisiti
- Python 3.8 o superiore
- pip (package installer)

### Setup

1. **Installa le dipendenze:**
```bash
pip install -r requirements.txt
```

2. **Avvia l'applicazione:**
```bash
streamlit run app.py
```

3. **Accedi all'interfaccia:**
L'applicazione si aprirà automaticamente nel browser all'indirizzo:
```
http://localhost:8501
```

## 📂 Struttura del Progetto

```
gestionale_caccia/
│
├── app.py                      # Applicazione principale
├── database.py                 # Gestione database SQLite
├── requirements.txt            # Dipendenze Python
│
├── pages/                      # Moduli interfaccia
│   ├── __init__.py
│   ├── anagrafe_cacciatori.py
│   ├── libretti_regionali.py
│   ├── fogli_caccia.py
│   ├── autorizzazioni_ras.py
│   ├── documenti.py
│   └── report_statistiche.py
│
├── documenti/                  # Documenti caricati
└── gestionale_caccia.db       # Database SQLite
```

## 💾 Database

Il sistema utilizza SQLite per la persistenza dei dati. Il database viene creato automaticamente al primo avvio.

### Tabelle Principali:
- **cacciatori**: Anagrafe completa cacciatori
- **libretti_regionali**: Libretti per anno
- **fogli_caccia**: Fogli caccia A3 con tracciamento completo
- **autorizzazioni_ras**: Autorizzazioni e pratiche RAS
- **documenti**: Archivio documenti
- **log_attivita**: Log di tutte le operazioni

## 🔧 Configurazione

### Prima Configurazione

1. **Aggiungi Cacciatori:**
   - Vai su "Anagrafe Cacciatori"
   - Usa "Nuovo Cacciatore" per inserire i primi dati

2. **Crea Fogli Caccia:**
   - Vai su "Fogli Caccia A3"
   - Usa "Gestione Fogli" per creare i fogli per l'anno corrente
   - Specifica numero iniziale e quantità (es. da 497424, 20 fogli)

3. **Registra Consegne:**
   - Vai su "Consegna Fogli"
   - Registra i fogli ricevuti dal fornitore

4. **Rilascia ai Cacciatori:**
   - Vai su "Rilascio Fogli"
   - Assegna i fogli ai singoli cacciatori

## 📊 Workflow Tipo

### Gestione Annuale Fogli Caccia

1. **Inizio Anno:**
   - Crea i fogli per l'anno corrente
   - Stato: DISPONIBILE

2. **Consegna da Fornitore:**
   - Registra consegna da Ilbaa
   - Stato: CONSEGNATO

3. **Rilascio ai Cacciatori:**
   - Assegna foglio al cacciatore
   - Stato: RILASCIATO

4. **Restituzione:**
   - Registra restituzione foglio compilato
   - Stato: RESTITUITO

5. **Fine Anno:**
   - Verifica fogli restituiti
   - Genera report annuale

## 📈 Report e Export

Il sistema genera automaticamente:
- Report anagrafico cacciatori
- Elenco libretti per anno
- Registro consegne/rilasci fogli
- Database per trasmissione RAS
- Statistiche e trend pluriennali

Tutti i report sono esportabili in formato CSV.

## 🔒 Sicurezza e Privacy

- Database locale SQLite
- Nessuna connessione esterna richiesta
- Log completo di tutte le operazioni
- Backup consigliato del file .db

## 🆘 Supporto

Per problemi o domande:
- Verifica che tutte le dipendenze siano installate
- Controlla i log di Streamlit in console
- Il database è in `gestionale_caccia.db`

## 📝 Note Importanti

- **Backup Regolari**: Effettua backup periodici del database
- **Documentazione**: Mantieni documentati i processi
- **Formazione**: Forma gli operatori all'uso del sistema
- **Manutenzione**: Aggiorna regolarmente le dipendenze

## 🎨 Personalizzazione

Il sistema può essere personalizzato modificando:
- Colori e stili CSS in `app.py`
- Campi del database in `database.py`
- Layout pagine nei file in `pages/`

## 📞 Contatti

Polizia Locale - Serrenti
Gestionale Caccia v1.0

---

**Developed with ❤️ for Polizia Locale**
