# Guida Import Strutturato File Excel

## Sistema di Import Automatico con Parsing Excel

Il gestionale legge automaticamente i dati anagrafici DENTRO i file Excel, non solo dal nome file.

---

## 🎯 Funzionalità

### 1. **Parsing File Excel**
- Apertura automatica di ogni file `.xlsx`
- Lettura intestazioni colonne (non posizioni fisse)
- Estrazione dati strutturati
- Gestione date native Excel

### 2. **Dati Estratti**
Il sistema cerca e legge questi dati:

| Campo | Intestazioni Riconosciute | Obbligatorio |
|-------|---------------------------|--------------|
| **Cognome** | "Cognome", "Surname" | ✅ Sì |
| **Nome** | "Nome", "Name", "First Name" | ✅ Sì |
| **Codice Fiscale** | "Codice Fiscale", "CF", "Cod. Fiscale" | ✅ Sì |
| **Data Nascita** | "Data Nascita", "Nascita", "Birth Date" | ❌ No |
| **Comune Residenza** | "Comune", "Residenza", "Città" | ❌ No |
| **Numero Licenza** | "Numero Licenza", "Licenza", "Tesserino" | ❌ No |
| **Anno** | "Anno", "Year", "Stagione" | ❌ No |

**Note**:
- Le intestazioni sono **case-insensitive** (maiuscole/minuscole uguali)
- Le intestazioni possono essere in qualsiasi colonna
- Il sistema cerca nelle prime 20 righe del file

### 3. **Popolazione Anagrafica**

```
┌─────────────────────────────────────────────────┐
│  File Excel → Parser → Dati Strutturati         │
└──────────────────┬──────────────────────────────┘
                   │
                   ↓
         ┌─────────────────────┐
         │ Cerca per CF        │ → Cacciatore esiste?
         └──────┬──────┬───────┘
                │      │
         SÌ ←───┘      └───→ NO
         │                    │
         ↓                    ↓
  Aggiorna dati         Crea nuovo
  se necessario         cacciatore
         │                    │
         └─────────┬──────────┘
                   │
                   ↓
           Crea foglio caccia
           collegato al cacciatore
```

**Logica**:
1. Cerca cacciatore per **Codice Fiscale** (chiave univoca)
2. **Se esiste** → Aggiorna solo dati nuovi (data nascita, residenza, licenza)
3. **Se NON esiste** → Crea nuova anagrafica completa
4. Collega il foglio al cacciatore via `cacciatore_id`

### 4. **Validazione Dati**

Il sistema valida automaticamente:

| Controllo | Azione | Messaggio Errore |
|-----------|--------|------------------|
| Cognome mancante | ❌ Blocca import file | "Cognome mancante" |
| Nome mancante | ❌ Blocca import file | "Nome mancante" |
| CF mancante | ❌ Blocca import file | "Codice Fiscale mancante" |
| CF formato invalido | ❌ Blocca import file | "Codice Fiscale invalido: XXX" |
| Anno < 1900 | ❌ Blocca import file | "Anno incoerente: 1850" |
| Anno > corrente+5 | ❌ Blocca import file | "Anno incoerente: 2050" |
| Data non riconosciuta | ⚠️ Warning | "Data non riconosciuta: XYZ" |

**Formato Codice Fiscale**:
- Lunghezza: 16 caratteri
- Pattern: `ABCDEF12G34H567I`
- 6 lettere + 2 cifre + 1 lettera + 2 cifre + 1 lettera + 3 cifre + 1 lettera

### 5. **Gestione Date**

Il sistema riconosce automaticamente:

- **Date Excel native** (datetime)
- **Stringhe**: `DD/MM/YYYY`, `DD-MM-YYYY`, `YYYY-MM-DD`
- **Numeri seriali Excel** (es: 44927 = 01/01/2023)

Tutte convertite in formato standard: `YYYY-MM-DD`

### 6. **Tracciabilità**

Ogni record importato conserva:

```
Note: "Importato da: Caboni Stefano (CONSEGNATO).xlsx | 
       Data: 2026-02-02 08:30:15 | 
       Operatore: admin"
```

---

## 📋 Formato File Excel Richiesto

### Esempio Foglio Excel:

| Cognome | Nome | Codice Fiscale | Data Nascita | Comune | Numero Licenza | Anno |
|---------|------|----------------|--------------|--------|----------------|------|
| CABONI | Stefano | CBNSFN80A01B354X | 01/01/1980 | Cagliari | 102752 | 2025 |
| ORTU | Mario | ORTMRA75B15L219Y | 15/02/1975 | Sassari | 109631 | 2025 |

**Requisiti**:
- Prima riga contiene intestazioni
- Intestazioni in qualsiasi ordine
- Cognome, Nome, CF obbligatori
- Altri campi opzionali

---

## 🚀 Come Usare

### STEP 1: Preparazione File

1. I file Excel devono contenere i dati in formato tabellare
2. Prima riga con intestazioni colonne
3. Una riga per ogni cacciatore
4. Nome file: `Cognome Nome (Stato).xlsx`

### STEP 2: Import

```
Menu → Import Fogli Massivo
Tab: Import da Cartella

1. Percorso: \\SERVER2\...\2025-26
2. Anno: 2025
3. Click: 🔍 Scansiona Cartella
```

### STEP 3: Processo Automatico

Il sistema per ogni file:
1. 📖 Apre il file Excel
2. 🔍 Cerca le intestazioni
3. 📊 Estrae i dati
4. ✅ Valida (CF, date, campi obbligatori)
5. 👤 Cerca/Crea cacciatore
6. 📄 Crea foglio collegato
7. 💾 Salva nel database

### STEP 4: Riepilogo

Al termine vedrai:

```
📊 Riepilogo Import

📁 File Trovati: 99
✅ Fogli Importati: 95
⚠️ Già Esistenti: 3
❌ Errori: 1

👤 Cacciatori Creati: 35
🔄 Cacciatori Aggiornati: 60
```

### STEP 5: Dettagli

Espandi "📋 Dettaglio Fogli Importati" per vedere:

| File | Cacciatore | CF | Numero Foglio | Stato | Nuovo Cacciatore |
|------|------------|----|--------------:|-------|:----------------:|
| Caboni Stefano... | CABONI Stefano | CBNSFN... | 2025102752 | Consegnato | ✅ |
| Ortu Mario... | ORTU Mario | ORTMRA... | 2025109631 | Stampato | ❌ |

---

## ⚠️ Gestione Errori

### Errori Bloccanti

Se un file ha errori critici:
- ❌ Il file viene saltato
- ✅ Gli altri file continuano
- 📋 Errore loggato nel dettaglio

**Esempio dettaglio errori**:

| File | Motivo |
|------|--------|
| Rossi Mario.xlsx | Parsing: Codice Fiscale mancante |
| Bianchi Luigi.xlsx | Parsing: Anno incoerente: 1850 |

### Warning Non Bloccanti

- ⚠️ Data non riconosciuta → Continua, campo vuoto
- ⚠️ Numero licenza mancante → Continua, genera automatico
- ⚠️ Anno mancante → Usa anno import

---

## 🔄 Aggiornamento Dati

### Comportamento

Se un cacciatore esiste già (stesso CF):

**Aggiorna SOLO se**:
- Nuovo dato disponibile nel file Excel
- Dato diverso da quello in database
- Campo non vuoto

**Campi aggiornabili**:
- Data nascita
- Comune residenza
- Numero licenza
- Telefono, cellulare, email
- Indirizzo, CAP

**Campi MAI sovrascritti**:
- Cognome
- Nome
- Codice Fiscale
- Note personali

### Esempio

**Database esistente**:
- CF: CBNSFN80A01B354X
- Data Nascita: (vuoto)
- Comune: Cagliari

**File Excel**:
- CF: CBNSFN80A01B354X
- Data Nascita: 01/01/1980
- Comune: Sassari

**Risultato**:
- CF: CBNSFN80A01B354X
- Data Nascita: 01/01/1980 ← Aggiunto
- Comune: Sassari ← Aggiornato

---

## 🎯 Vantaggi

### vs Vecchio Sistema

| Aspetto | Vecchio | Nuovo |
|---------|---------|-------|
| **Fonte dati** | Solo nome file | ✅ Contenuto Excel |
| **Anagrafica** | Manuale | ✅ Automatica |
| **Validazione** | Nessuna | ✅ CF, date, obbligatori |
| **Collegamento** | Nome stringa | ✅ FK cacciatore_id |
| **Date** | Stringhe | ✅ Date native |
| **Tracciabilità** | Limitata | ✅ Completa |
| **Aggiornamenti** | No | ✅ Automatici |

### Risultati

✅ **Import zero-touch**: Nessun intervento manuale
✅ **Anagrafica popolata**: Dati completi e validati
✅ **Fogli collegati**: Relazione cacciatore-foglio
✅ **Modificabile**: Dati editabili dopo import
✅ **Tracciato**: Origine dati sempre nota

---

## 🔍 Troubleshooting

### "Intestazioni non trovate"

**Causa**: File Excel non ha intestazioni riconosciute

**Soluzione**:
1. Apri il file Excel manualmente
2. Verifica che la prima riga contenga: "Cognome", "Nome", "Codice Fiscale"
3. Se le intestazioni sono in un'altra riga, spostale alla riga 1

### "Codice Fiscale invalido"

**Causa**: CF non rispetta il formato italiano

**Soluzione**:
1. Verifica lunghezza (deve essere 16 caratteri)
2. Verifica formato: `ABCDEF12G34H567I`
3. Controlla non ci siano spazi

### "Anno incoerente"

**Causa**: Anno < 1900 o > anno corrente + 5

**Soluzione**:
1. Verifica la colonna "Anno" nel file Excel
2. Correggi il valore (es: 2025)
3. Se manca, il sistema usa l'anno di import

### File saltato ma non capisco perché

**Soluzione**:
1. Espandi "⚠️ Dettaglio Avvisi/Errori"
2. Cerca il nome file
3. Leggi il motivo dell'errore
4. Correggi il file Excel
5. Riprova import

---

## 💡 Best Practices

### Preparazione File

1. **Standardizza intestazioni**: Usa sempre "Cognome", "Nome", "Codice Fiscale"
2. **Una riga = Un cacciatore**: Non duplicare righe
3. **CF univoco**: Un file = Un cacciatore
4. **Date in formato Excel**: Usa celle tipo "Data", non testo
5. **Nomi file significativi**: Include stato tra parentesi

### Durante Import

1. **Importa una volta**: Evita reimport multipli
2. **Controlla riepilogo**: Verifica contatori
3. **Leggi dettaglio errori**: Correggi file problematici
4. **Verifica anagrafica**: Controlla cacciatori creati

### Dopo Import

1. **Controlla collegamenti**: Vai a Anagrafe → Verifica cacciatori
2. **Verifica fogli**: Menu Fogli Caccia → Controlla numero fogli
3. **Testa ricerca**: Cerca per nome/cognome
4. **Valida dati**: Apri alcuni record per controllo

---

## 📊 Workflow Completo

```
1. Prepara file Excel con dati strutturati
   ↓
2. Carica file in cartella di rete
   ↓
3. Menu → Import Fogli Massivo
   ↓
4. Inserisci percorso cartella
   ↓
5. Click "Scansiona Cartella"
   ↓
6. Sistema processa automaticamente:
   - Apre file
   - Legge dati
   - Valida
   - Crea/aggiorna cacciatori
   - Crea fogli
   ↓
7. Controlla riepilogo import
   ↓
8. Verifica eventuali errori
   ↓
9. Correggi file problematici
   ↓
10. Riprova import solo file corretti
```

---

## 🎓 Esempio Completo

### File: `Caboni Stefano (CONSEGNATO).xlsx`

**Contenuto**:
```
| Cognome | Nome    | Codice Fiscale    | Data Nascita | Comune    | Numero Licenza |
|---------|---------|-------------------|--------------|-----------|----------------|
| CABONI  | Stefano | CBNSFN80A01B354X  | 01/01/1980   | Cagliari  | 102752         |
```

### Processo:

1. **Parsing**: Sistema apre file ed estrae dati
2. **Validazione**: CF valido ✅, tutti campi OK ✅
3. **Ricerca**: Cerca cacciatore con CF = CBNSFN80A01B354X
4. **Risultato**: Non trovato → Crea nuovo
5. **Anagrafica Creata**:
   ```
   ID: 1
   Cognome: CABONI
   Nome: Stefano
   CF: CBNSFN80A01B354X
   Data Nascita: 1980-01-01
   Comune: Cagliari
   Numero Tessera: 102752
   ```
6. **Foglio Creato**:
   ```
   Numero: 2025102752
   Anno: 2025
   Cacciatore ID: 1 ← Collegato!
   Stato: Consegnato
   Note: "Importato da: Caboni Stefano (CONSEGNATO).xlsx | ..."
   File Path: \\SERVER2\...\Caboni Stefano (CONSEGNATO).xlsx
   ```

### Visualizzazione:

**Menu → Anagrafe Cacciatori**:
```
┌─────┬─────────┬─────────┬──────────────────┬────────────┐
│ ID  │ Cognome │ Nome    │ CF               │ Comune     │
├─────┼─────────┼─────────┼──────────────────┼────────────┤
│ 1   │ CABONI  │ Stefano │ CBNSFN80A01B354X │ Cagliari   │
└─────┴─────────┴─────────┴──────────────────┴────────────┘
```

**Menu → Fogli Caccia A3**:
```
┌──────────────┬──────┬───────────────┬───────┬────────────┐
│ N. Foglio    │ Anno │ Cacciatore    │ Stato │ File       │
├──────────────┼──────┼───────────────┼───────┼────────────┤
│ 2025102752   │ 2025 │ CABONI Stefano│ Cons. │ Caboni...  │
└──────────────┴──────┴───────────────┴───────┴────────────┘
```

---

## ✅ Checklist Verifica

Dopo l'import, verifica:

- [ ] Numero fogli importati = File Excel validi
- [ ] Cacciatori creati in anagrafica
- [ ] Fogli collegati ai cacciatori corretti
- [ ] Stati corretti (Consegnato, Stampato, Da rinnovare)
- [ ] CF presenti e validi per tutti
- [ ] Date nascita nel formato corretto
- [ ] File path salvati per ogni foglio
- [ ] Note import con tracciabilità

---

**Sistema sviluppato per Polizia Locale - Import automatico fogli caccia**
