# FIX IMPORT TEMPLATE RAS - DOCUMENTAZIONE TECNICA

## 🎯 Problema Risolto

**BUG**: File Excel "Foglio Venatorio RAS" importati con Cognome/Nome = "None"

**CAUSA**: Il parser cercava colonne strutturate (intestazioni) che non esistono nei template RAS. 
I dati RAS sono in celle testuali libere tipo: "BANDINO GIUSEPPE in possesso del porto d'arma..."

## ✅ Soluzione Implementata

### 1. **Riconoscimento Automatico Template RAS**

Il parser ora rileva automaticamente il template:
- Cerca keyword: "Regione Autonoma della Sardegna", "Foglio Venatorio", "R.A.S", "assessorato"
- Scan nelle prime 20 righe, prime 5 colonne
- Non si basa sul nome file

### 2. **Parsing Template RAS**

Estrae Cognome/Nome dal contenuto cella con pattern regex:
```python
r"([A-Za-zÀ-ÿ''\-]+)\s+([A-Za-zÀ-ÿ''\-]+)\s+in\s+possesso\s+del\s+porto"
```

Strategia di ricerca:
1. Cerca in A2 (posizione tipica)
2. Fallback su A3, A4, A1
3. Scan esteso A1:B60 se necessario

### 3. **Fallback su Filename**

Se parsing contenuto fallisce, estrae dal filename:
- `Bandino Giuseppe(Stampato).xlsx` → Cognome=BANDINO, Nome=Giuseppe, Stato=STAMPATO
- `Caboni Stefano (CONSEGNATO).xlsx` → Cognome=CABONI, Nome=Stefano, Stato=CONSEGNATO
- `Corona_Mario_Stampato.xlsx` → Cognome=CORONA, Nome=Mario, Stato=STAMPATO
- `Ortu Mario.xlsx` → Cognome=ORTU, Nome=Mario, Stato=RILASCIATO

### 4. **Gestione Anagrafica Senza CF**

Template RAS spesso non hanno CF. Modifiche:
- Cerca cacciatore per CF se disponibile
- Fallback su ricerca per Cognome+Nome
- Crea cacciatore anche senza CF

### 5. **Logging Diagnostico Completo**

Ogni import logga:
```
[IMPORT] file=Bandino Giuseppe(Stampato).xlsx | name_source=filename | cognome=BANDINO | nome=Giuseppe
```

Valori `name_source`:
- `cell_A2` - Estratto da cella A2
- `cell_A3` - Estratto da cella A3
- `filename` - Estratto da nome file
- `structured` - Tabella con intestazioni
- `none` - Fallito

---

## 📝 File Modificati

### 1. `excel_parser.py` - Parser Excel Avanzato

**Modifiche**:
- Aggiunto `_detect_template_type()` - Rileva RAS vs STANDARD
- Aggiunto `_parse_ras_template()` - Parsing specifico RAS
- Aggiunto `_parse_from_filename()` - Fallback filename
- Modificato `parse_excel_file()` - Integra logiche
- Modificato `_validate_data()` - CF opzionale

**Righe modificate**: ~200 righe aggiunte/modificate

### 2. `pages/import_fogli.py` - Import Fogli Massivo

**Modifiche**:
- Riga 125: Passa `file_name` al parser per fallback
- Riga 136-142: Gestione `name_source` nel log
- Riga 144-153: Validazione minima cognome+nome
- Riga 154-169: Gestione cacciatori senza CF
- Riga 199-232: Creazione cacciatori con CF opzionale

**Righe modificate**: ~50 righe modificate

### 3. `test_parser.py` - Script Test Nuovo

**File nuovo**: Script di test completo per verificare parsing

---

## 🧪 Test Eseguiti

### Test 1: Filename Patterns

```
✅ Bandino Giuseppe(Stampato).xlsx
   Cognome: BANDINO | Nome: Giuseppe | Stato: STAMPATO

✅ Caboni Stefano (CONSEGNATO).xlsx
   Cognome: CABONI | Nome: Stefano | Stato: CONSEGNATO

✅ Corona Mario (da rinnovare).xlsx
   Cognome: CORONA | Nome: Mario | Stato: DA_RINNOVARE

✅ Todeschini Gianni Carlo (CONSEGNATO).xlsx
   Cognome: TODESCHINI | Nome: Gianni Carlo | Stato: CONSEGNATO

✅ Ortu Mario.xlsx
   Cognome: ORTU | Nome: Mario | Stato: RILASCIATO

✅ Furcas_Luigi_Stampato.xlsx
   Cognome: FURCAS | Nome: Luigi | Stato: STAMPATO
```

**Tutti i pattern riconosciuti correttamente! ✅**

---

## 📊 Flusso Completo Import

```
File Excel
    ↓
[STEP 1] Apri file con openpyxl
    ↓
[STEP 2] Rileva template (RAS o STANDARD)
    ↓
┌──────────────┴──────────────┐
│                             │
│ Template RAS               │ Template STANDARD
│ • Cerca in celle A2-A4     │ • Cerca intestazioni
│ • Pattern regex COGNOME    │ • Mappa colonne
│   NOME "in possesso..."    │ • Estrai da riga dati
│ • Fallback scan A1:B60     │
│                             │
└──────────────┬──────────────┘
               ↓
[STEP 3] Parsing fallito?
    ↓ SÌ
[STEP 4] Fallback filename
    • Pattern1: Nome(Stato).xlsx
    • Pattern2: Nome_Stato.xlsx
    • Pattern3: Nome.xlsx
    ↓
[STEP 5] Validazione (Cognome+Nome obbligatori)
    ↓
[STEP 6] Cerca/Crea Cacciatore
    • Cerca per CF se disponibile
    • Fallback ricerca Cognome+Nome
    • Crea anche senza CF
    ↓
[STEP 7] Crea Foglio collegato
    ↓
[STEP 8] Salva con tracciabilità
```

---

## 🔍 Esempi Log Attesi

### Caso 1: Template RAS - Parsing OK da Contenuto

```
INFO:excel_parser:[PARSE] Inizio parsing file: Bandino Giuseppe(Stampato).xlsx
INFO:excel_parser:Template RAS riconosciuto: 'foglio venatorio' in 1,1
INFO:excel_parser:RAS: Estratto da cella A2: BANDINO Giuseppe
INFO:excel_parser:Parse OK | Source: ras_template | BANDINO Giuseppe
INFO:import_fogli:[IMPORT] file=Bandino Giuseppe(Stampato).xlsx | name_source=cell_A2 | cognome=BANDINO | nome=Giuseppe
```

### Caso 2: Template RAS - Parsing Fallito, Fallback Filename

```
INFO:excel_parser:[PARSE] Inizio parsing file: Ortu Mario(Consegnato).xlsx
INFO:excel_parser:Template RAS riconosciuto: 'regione autonoma' in 2,1
WARNING:excel_parser:RAS: Estratto da cella B12: ORTU Mario
WARNING:excel_parser:Template RAS: Cognome/Nome non trovati nel contenuto
INFO:excel_parser:[PARSE] Filename pattern1: cognome=ORTU, nome=Mario, stato=CONSEGNATO
INFO:excel_parser:Parse OK | Source: filename | ORTU Mario
INFO:import_fogli:[IMPORT] file=Ortu Mario(Consegnato).xlsx | name_source=filename | cognome=ORTU | nome=Mario
```

### Caso 3: Template Strutturato - Normale

```
INFO:excel_parser:[PARSE] Inizio parsing file: Anagrafica.xlsx
INFO:excel_parser:Template STANDARD
INFO:excel_parser:Parse OK | Source: structured | CABONI Stefano
INFO:import_fogli:[IMPORT] file=Anagrafica.xlsx | name_source=structured | cognome=CABONI | nome=Stefano
```

### Caso 4: Parsing FALLITO

```
INFO:excel_parser:[PARSE] Inizio parsing file: File_Corrotto.xlsx
ERROR:excel_parser:Parse FAILED | Errors: ['Cognome mancante', 'Nome mancante']
ERROR:import_fogli:[IMPORT] file=File_Corrotto.xlsx | Cognome/Nome mancanti | source=none
```

---

## 🚀 Come Testare

### 1. Installa Nuova Versione

```
1. Chiudi app (CTRL+C)
2. Elimina cartella vecchia "gestionale_caccia"
3. Estrai gestionale_caccia_RAS_FIX_FINAL.zip
4. Doppio click: avvia.bat
```

### 2. Test Manuale con Script

```bash
cd gestionale_caccia
python test_parser.py
```

Output atteso: Tutti i test ✅

### 3. Test Import Reale

```
1. Menu → Import Fogli Massivo
2. Percorso: \\SERVER2\...\2025-26
3. Anno: 2025
4. Click: 🔍 Scansiona Cartella
```

### 4. Verifica Risultati

```
Menu → Fogli Caccia A3
→ Colonne Cognome/Nome NON devono essere "None"
→ Controlla log in console per vedere `name_source`
```

---

## 📋 Checklist Verifica

Dopo l'import, verifica:

- [ ] Cognome/Nome popolati correttamente (NON "None")
- [ ] Stati corretti (Consegnato, Stampato, Da rinnovare)
- [ ] Cacciatori creati in anagrafica
- [ ] Fogli collegati ai cacciatori
- [ ] Log mostrano `name_source` corretto
- [ ] File con CF popolano campo CF
- [ ] File senza CF creano cacciatore ugualmente

---

## 🐛 Troubleshooting

### "Cognome/Nome ancora None"

**Causa**: Database vecchio con import precedenti

**Soluzione**:
```
1. Chiudi app
2. Doppio click: reset_e_avvia.bat
3. Reimporta tutti i file
```

### "Template RAS non riconosciuto"

**Causa**: Keywords RAS non trovate

**Soluzione**:
- Apri file Excel manualmente
- Verifica presenza testo "Regione Autonoma della Sardegna" o "Foglio Venatorio"
- Se assente, usa fallback filename (rinomina file con pattern corretto)

### "Parsing fallisce anche su filename"

**Causa**: Nome file non segue pattern supportati

**Soluzione**:
- Rinomina file: `Cognome Nome(Stato).xlsx`
- Esempio: `Bandino Giuseppe(Stampato).xlsx`

---

## 💡 Best Practices

### Nomi File

Per massima compatibilità:
```
✅ CORRETTO:
   Bandino Giuseppe(Stampato).xlsx
   Caboni Stefano (CONSEGNATO).xlsx
   Ortu Mario.xlsx

❌ EVITARE:
   BandinoGiuseppe.xlsx          (no spazio)
   Giuseppe Bandino(Stampato).xlsx (ordine invertito)
   File123.xlsx                   (non riconoscibile)
```

### File Excel Template RAS

Assicurati che contengano:
- Testo "Regione Autonoma della Sardegna" o "Foglio Venatorio"
- Frase con pattern: "COGNOME NOME in possesso del porto d'arma"
- Cella A2 o A3 preferibilmente

---

## 🎯 Riassunto Modifiche

| Componente | Prima | Dopo |
|------------|-------|------|
| **Template RAS** | ❌ Non riconosciuto → Cognome/Nome = None | ✅ Riconosciuto e parsato |
| **Parsing contenuto** | ❌ Solo tabelle con intestazioni | ✅ Anche celle testuali con regex |
| **Fallback filename** | ❌ Non implementato | ✅ Pattern multipli supportati |
| **CF obbligatorio** | ❌ Sì, bloccava import RAS | ✅ Opzionale |
| **Logging** | ⚠️ Minimo | ✅ Completo con name_source |
| **Test** | ❌ Nessuno | ✅ Script test_parser.py |

---

## 📞 Support

Se continui ad avere problemi:

1. Esegui `python test_parser.py` e condividi output
2. Controlla log in console durante import
3. Verifica formato nome file
4. Controlla contenuto celle A2-A4 del file Excel

---

**Versione**: 1.0 - Fix Template RAS  
**Data**: 2026-02-02  
**Autore**: Sistema Import Gestionale Caccia
