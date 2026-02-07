# GUIDA: Reimport Fogli con Stati Corretti

## 🎯 Problema

I fogli importati hanno tutti stato **RILASCIATO** invece di distinguere tra:
- **CONSEGNATO** (dal fornitore, non ancora ai cacciatori)
- **RILASCIATO** (già ai cacciatori - Stampato)
- **RILASCIATO** con nota "DA RINNOVARE" (da rinnovare)

## ✅ SOLUZIONE: Reimport Corretto

### STEP 1: Elimina Import Precedente

**Opzione A: Reset Completo** (se non hai altri dati importanti)
```
1. Chiudi app (CTRL+C)
2. Doppio click: reset_e_avvia.bat
3. L'app si riavvia con database pulito
```

**Opzione B: Elimina Solo Fogli Anno 2025** (mantieni cacciatori)
```
Purtroppo non c'è funzione automatica
Soluzione: usa Opzione A e reimporta tutto
```

### STEP 2: Riavvia App (se non già fatto)
```
Doppio click: avvia.bat
```

### STEP 3: Aggiungi Cacciatori (se necessario)
```
Menu → Anagrafe Cacciatori
Aggiungi tutti i cacciatori presenti nei file
```

### STEP 4: Reimport con Nuova Versione
```
Menu → Import Fogli Massivo
Tab: Import da Cartella

Percorso: \\SERVER2\...\2025-26
Anno: 2025

Click: Scansiona Cartella
```

### STEP 5: Verifica Stati
```
Menu → Fogli Caccia A3
Anno: 2025

Verifica nella colonna "Stato":
✅ Fogli con "(CONSEGNATO)" → Stato: CONSEGNATO
✅ Fogli con "(Stampato)" → Stato: RILASCIATO  
✅ Fogli con "(da rinnovare)" → Stato: RILASCIATO + nota [DA RINNOVARE]
```

## 📊 Nuova Mappatura Stati

### File: "Bandino Giuseppe(CONSEGNATO).xlsx"
```
Stato: CONSEGNATO
Significato: Consegnato dal fornitore (Ilbaa)
           Non ancora rilasciato al cacciatore
Prossimo step: Rilascio al cacciatore
```

### File: "Corona Mario(Stampato).xlsx"
```
Stato: RILASCIATO
Significato: Già stampato e rilasciato al cacciatore
Prossimo step: Attendi restituzione
```

### File: "Piras Luigi(da rinnovare).xlsx"
```
Stato: RILASCIATO
Note: [DA RINNOVARE]
Significato: Foglio dell'anno scorso da rinnovare
Prossimo step: Rinnovo per nuovo anno
```

## 🎯 Workflow Completo 2025-26

### 1. CONSEGNATO (dal fornitore)
```
Stato: CONSEGNATO
Tab: "Consegna Fogli"
Azione: Registra data consegna da Ilbaa
```

### 2. RILASCIATO (al cacciatore)
```
Stato: RILASCIATO
Tab: "Rilascio Fogli"
Azione: Associa cacciatore, registra rilascio
```

### 3. RESTITUITO
```
Stato: RESTITUITO
Tab: "Restituzione Fogli"
Azione: Registra data restituzione
```

## 📋 Statistiche Attese

Dopo reimport corretto, dovresti vedere:

```
Menu → Fogli Caccia A3 → Anno 2025

Totale: 99
Disponibili: 0
Consegnati: X  ← Fogli con (CONSEGNATO)
Rilasciati: Y  ← Fogli con (Stampato) + (da rinnovare)
Restituiti: 0
```

## 💡 Filtri per Stato

Usa il filtro "Filtra per Stato":

```
Tutti → Vedi tutti i 99 fogli
CONSEGNATO → Solo fogli consegnati dal fornitore
RILASCIATO → Solo fogli rilasciati ai cacciatori
```

## 🔍 Come Distinguere "da rinnovare"

Fogli "da rinnovare" hanno:
```
Stato: RILASCIATO
Note: "Importato da file: Nome(da rinnovare).xlsx [DA RINNOVARE]"
```

Per trovarli velocemente:
```
1. Filtra per Stato: RILASCIATO
2. Guarda colonna "Note"
3. Cerca "[DA RINNOVARE]"
```

## ⚠️ IMPORTANTE

**Prima di Reimport**:
- [ ] Ho fatto backup del database? (copia gestionale_caccia.db)
- [ ] Ho la lista dei cacciatori? (per reinserirli se necessario)
- [ ] So dove sono i file Excel? (percorso cartella)
- [ ] Ho chiuso completamente l'app? (CTRL+C)

**Dopo Reimport**:
- [ ] Verifico totale fogli = 99
- [ ] Verifico stati diversi (CONSEGNATO + RILASCIATO)
- [ ] Verifico colonna "File" popolata
- [ ] Verifico posso aprire file Excel

## 🎯 Risultato Finale

```
Anno 2025 - Totale 99 fogli

CONSEGNATI: 30 fogli
├─ Bandino Giuseppe (CONSEGNATO)
├─ Boi Gerardo (CONSEGNATO)
└─ ... altri consegnati dal fornitore

RILASCIATI: 69 fogli  
├─ Stampati: 50 fogli
│  ├─ Piras Antonio (Stampato)
│  ├─ Sanna Luigi (Stampato)
│  └─ ... altri stampati
│
└─ Da Rinnovare: 19 fogli
   ├─ Corona Mario (da rinnovare) [DA RINNOVARE]
   ├─ Murru Enrico (da rinnovare) [DA RINNOVARE]
   └─ ... altri da rinnovare
```

## 📞 FAQ

**Q: Perso dati reimportando?**
A: Se fai reset completo, sì. Fai backup prima!

**Q: Devo reimportare i cacciatori?**
A: Dipende. Se fai reset completo, sì. Se no, sono già nel database.

**Q: Gli stati cambieranno automaticamente sui file vecchi?**
A: No. Devi reimportare i fogli per applicare la nuova mappatura.

**Q: Posso correggere manualmente gli stati?**
A: Sì, ma su 99 fogli è impraticabile. Meglio reimport.

---

**Data:** 31/01/2026
**Versione:** 1.2 (Stati Distinti)
