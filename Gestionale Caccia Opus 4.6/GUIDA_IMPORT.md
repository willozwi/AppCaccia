# GUIDA IMPORT FOGLI CACCIA

## 📥 Import Massivo Fogli Caccia Esistenti

Il gestionale può importare automaticamente i fogli caccia esistenti dai file Excel.

## 🎯 Preparazione

### 1. Organizza i File
I tuoi file possono avere uno di questi formati:
```
Cognome Nome(Stato).xlsx
Cognome Nome (Stato).xlsx
Cognome_Nome_Stato.xlsx
Cognome Nome.xlsx
```

Esempi validi:
- `Bandino Giuseppe(Stampato).xlsx` ✅
- `Bandino Giuseppe (Stampato).xlsx` ✅
- `Bandino_Giuseppe_Stampato_.xlsx` ✅
- `Corona Mario (CONSEGNATO).xlsx` ✅
- `Piras Antonio(da rinnovare).xlsx` ✅
- `Sanna Luigi.xlsx` ✅ (stato automatico: RILASCIATO)

### 2. Stati Riconosciuti
Il sistema riconosce automaticamente questi stati dal nome file e li mappa correttamente:

**Stati Mappati**:
- `CONSEGNATO` / `Consegnato` → **CONSEGNATO** (fogli consegnati dal fornitore, pronti per rilascio)
- `Stampato` / `STAMPATO` → **RILASCIATO** (fogli già stampati e rilasciati ai cacciatori)
- `da rinnovare` / `DA_RINNOVARE` → **RILASCIATO** (fogli da rinnovare, aggiunge nota speciale)
- (vuoto) → **RILASCIATO** per default

**Differenza Stati**:
- **CONSEGNATO**: Fogli consegnati dal fornitore (es. Ilbaa) ma NON ancora rilasciati ai cacciatori
- **RILASCIATO**: Fogli già rilasciati ai cacciatori (stampati o da rinnovare)

## 🚀 Procedura Import

### STEP 1: Aggiungi Prima i Cacciatori

Prima di importare i fogli, **devi avere i cacciatori nel database**!

```
Menu → Anagrafe Cacciatori → Nuovo Cacciatore
```

Inserisci tutti i cacciatori che hanno fogli da importare.

### STEP 2: Import Massivo

```
Menu → Import Fogli Massivo → Import da Cartella
```

1. **Inserisci il percorso della cartella**
   ```
   C:\CACCIA\FOGLI CACCIA A3 Annuali\FOGLI RILASCIATI\2025-26
   ```

2. **Seleziona l'anno**
   - Esempio: 2025

3. **Click su "🔍 Scansiona Cartella"**

Il sistema:
- ✅ Trova tutti i file Excel (.xlsx)
- ✅ Estrae cognome, nome e stato dal nome file
- ✅ Cerca il cacciatore nel database
- ✅ Crea il record del foglio caccia
- ✅ Associa il file al record

### STEP 3: Verifica Import

```
Menu → Import Fogli Massivo → Fogli Importati
```

Controlla che tutti i fogli siano stati importati correttamente.

## 📊 Risultati Import

Al termine vedrai un riepilogo:
- **File Trovati**: Totale file nella cartella
- **✅ Importati**: Fogli aggiunti con successo
- **⚠️ Già Esistenti**: Fogli già presenti (saltati)
- **❌ Errori**: File con problemi

## ⚠️ Gestione Errori

### Cacciatore Non Trovato
Se un cacciatore non è nel database:
- Il foglio viene comunque importato
- Nome viene salvato in `rilasciato_a`
- Associazione cacciatore = NULL
- Appare negli avvisi

**Soluzione:**
1. Aggiungi il cacciatore in "Anagrafe Cacciatori"
2. Vai in "Fogli Caccia A3"
3. Modifica il foglio e associa il cacciatore

### Nome File Non Valido
Se il nome file non rispetta uno dei formati supportati:
- Appare negli errori
- Non viene importato

**Formati accettati:**
- `Cognome Nome(Stato).xlsx`
- `Cognome Nome (Stato).xlsx` 
- `Cognome_Nome_Stato.xlsx`
- `Cognome Nome.xlsx`

**Soluzione:**
Verifica che il nome file contenga almeno cognome e nome separati da spazio o underscore.

## 📄 Import Singolo File

Se hai solo un file da importare:

```
Menu → Import Fogli Massivo → Import Singolo File
```

1. Carica il file Excel
2. Il sistema compila automaticamente i campi
3. Verifica/modifica i dati
4. Seleziona cacciatore (opzionale)
5. Click "💾 Importa Foglio"

## 🔍 Verifica Dopo Import

Dopo l'import, controlla:

### 1. Dashboard
```
Menu → Dashboard
```
Verifica che il numero "Fogli Anno 2025" sia aumentato

### 2. Fogli Caccia A3
```
Menu → Fogli Caccia A3 → Gestione Fogli
```
- Filtra per anno 2025
- Filtra per stato RILASCIATO
- Controlla che tutti i fogli siano presenti

### 3. Statistiche
```
Menu → Report e Statistiche
```
Genera report per verificare completezza dati

## 💡 Tips e Best Practices

### ✅ DA FARE
- Importa i cacciatori PRIMA dei fogli
- Usa nomi file uniformi e corretti
- Controlla sempre il riepilogo import
- Verifica gli avvisi per cacciatori non trovati
- Fai backup del database prima di import massivi

### ❌ EVITA
- Importare senza aver creato i cacciatori
- Modificare i nomi file dopo l'import
- Ignorare gli avvisi di import
- Fare import multipli della stessa cartella (crea duplicati)

## 🔄 Re-Import

Se devi re-importare la stessa cartella:
- I fogli già esistenti vengono saltati (no duplicati)
- Vengono importati solo i nuovi fogli
- Controlla il contatore "Già Esistenti"

## 📁 Dove Vengono Salvati i File

I file Excel originali vengono:
1. **Import da Cartella**: Viene salvato solo il percorso originale
2. **Import Singolo**: Viene copiato in `documenti/fogli_caccia/`

## 🆘 Risoluzione Problemi

### Problema: "Cartella non trovata"
**Causa**: Percorso errato
**Soluzione**: 
- Copia/incolla il percorso da Esplora File
- Usa backslash `\` su Windows
- Verifica che la cartella esista

### Problema: "Nessun file Excel trovato"
**Causa**: Cartella vuota o file non .xlsx
**Soluzione**:
- Verifica che ci siano file .xlsx nella cartella
- Controlla estensioni file (non .xls vecchio)

### Problema: "Molti cacciatori non trovati"
**Causa**: Cacciatori non nel database
**Soluzione**:
1. Esporta lista nomi dai file Excel
2. Importa tutti i cacciatori in "Anagrafe Cacciatori"
3. Ri-importa i fogli

### Problema: "Errore durante l'import"
**Causa**: Varie (permessi, file corrotto, ecc.)
**Soluzione**:
- Controlla dettaglio errori nell'expander
- Verifica permessi file/cartelle
- Prova import singolo per debug

## 📋 Checklist Import Completo

Prima dell'import:
- [ ] Database pulito o backup fatto
- [ ] Tutti i cacciatori nel database
- [ ] Percorso cartella verificato
- [ ] Nomi file uniformi

Durante import:
- [ ] Anno corretto selezionato
- [ ] Scansione completata
- [ ] Nessun errore critico

Dopo import:
- [ ] Riepilogo controllato
- [ ] Avvisi verificati e risolti
- [ ] Dashboard aggiornata
- [ ] Report generato per verifica

---

**Buon import! 📥**
