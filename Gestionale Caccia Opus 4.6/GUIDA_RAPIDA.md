# GUIDA RAPIDA - Gestionale Caccia

## 🚀 AVVIO VELOCE

### Windows:
1. Doppio click su `avvia.bat`
2. L'applicazione si apre nel browser

### Linux/Mac:
1. Apri terminale nella cartella
2. Esegui: `./avvia.sh`
3. L'applicazione si apre nel browser

## 📋 PRIMI PASSI

### 1. Aggiungi Cacciatori
```
Menu → Anagrafe Cacciatori → Nuovo Cacciatore
```
Compila i dati obbligatori (contrassegnati con *)

### 2. Crea Fogli Caccia
```
Menu → Fogli Caccia A3 → Gestione Fogli
```
- Seleziona anno
- Inserisci numero iniziale (es. 497424)
- Indica quantità (es. 20)
- Click "Crea Fogli"

### 3. Registra Consegna
```
Menu → Fogli Caccia A3 → Consegna Fogli
```
- Seleziona data consegna
- Inserisci "Consegnato da" (es. Ilbaa)
- Seleziona fogli consegnati
- Click "Registra Consegna"

### 4. Rilascia Foglio a Cacciatore
```
Menu → Fogli Caccia A3 → Rilascio Fogli
```
- Seleziona cacciatore
- Seleziona foglio da rilasciare
- Inserisci data rilascio
- Click "Registra Rilascio"

### 5. Registra Restituzione
```
Menu → Fogli Caccia A3 → Restituzione Fogli
```
- Seleziona foglio da restituire
- Inserisci data restituzione
- Click "Registra Restituzione"

## 📊 STATISTICHE E REPORT

### Dashboard
```
Menu → Dashboard
```
Panoramica completa dello stato attuale

### Report Personalizzati
```
Menu → Report e Statistiche → Report Personalizzati
```
- Scegli tipo report
- Seleziona anno
- Click "Genera Report"
- Scarica CSV

## 🔍 RICERCA

### Cerca Cacciatore
```
Menu → Anagrafe Cacciatori → Ricerca
```
Cerca per:
- Nome / Cognome
- Numero tessera
- Codice fiscale

### Filtra Fogli
```
Menu → Fogli Caccia A3 → Gestione Fogli
```
Filtra per:
- Anno
- Stato (Disponibile, Consegnato, Rilasciato, Restituito)

## 💡 SUGGERIMENTI

### ✅ Best Practices
- Fai backup regolari del database (gestionale_caccia.db)
- Registra sempre le operazioni appena effettuate
- Verifica i dati prima di confermare
- Usa la ricerca per trovare rapidamente i cacciatori

### ⚠️ Attenzione
- Non chiudere la finestra del terminale mentre usi l'app
- Non modificare manualmente il database
- Mantieni i numeri tessera univoci
- Verifica le date inserite

## 📁 FILE IMPORTANTI

- **gestionale_caccia.db** - Database principale (FAI BACKUP!)
- **documenti/** - Cartella documenti caricati
- **app.py** - Applicazione principale

## 🆘 PROBLEMI COMUNI

### L'applicazione non si avvia
1. Verifica che Python sia installato
2. Installa dipendenze: `pip install -r requirements.txt`
3. Riavvia il terminale

### Errore "Numero tessera già esistente"
- Controlla che il numero tessera sia univoco
- Verifica nell'anagrafe se è già presente

### I fogli non vengono visualizzati
- Verifica di aver creato i fogli per l'anno corretto
- Controlla il filtro anno selezionato

## 📞 SUPPORTO

In caso di problemi:
1. Controlla i messaggi di errore
2. Verifica i dati inseriti
3. Riavvia l'applicazione
4. Consulta il README.md completo

## 🎯 WORKFLOW COMPLETO ANNO

```
INIZIO ANNO
↓
CREA FOGLI (Disponibili)
↓
RICEVI CONSEGNA DA FORNITORE (Consegnati)
↓
RILASCIA AI CACCIATORI (Rilasciati)
↓
RACCOGLI RESTITUZIONI (Restituiti)
↓
GENERA REPORT FINE ANNO
↓
FINE ANNO
```

## 📊 REPORT DISPONIBILI

1. **Report Anagrafico Completo**
   - Tutti i cacciatori con dati completi

2. **Report Libretti per Anno**
   - Elenco libretti rilasciati

3. **Report Fogli Caccia Dettagliato**
   - Tracciamento completo fogli

4. **Report Autorizzazioni RAS**
   - Stato pratiche autorizzazioni

5. **Report Attività Sistema**
   - Log operazioni effettuate

---

**Buon lavoro! 🦌**
