# GUIDA: Risolvere "Database is Locked"

## 🔴 Problema: "Errore durante l'import: database is locked"

Questo errore si verifica quando il database SQLite è ancora occupato da un'operazione precedente.

## ✅ SOLUZIONE RAPIDA (3 passaggi)

### STEP 1: Chiudi l'Applicazione
```
Nel terminale dove gira Streamlit:
CTRL + C
```

Aspetta che il processo si chiuda completamente (vedi "Server stopped").

### STEP 2: Sblocca il Database
Hai **2 opzioni**:

#### Opzione A: Sblocca SENZA perdere dati (CONSIGLIATA)
```
Doppio click su: sblocca_e_avvia.bat
```
Questo:
- ✅ Elimina solo i file di lock (.db-shm, .db-wal)
- ✅ Mantiene tutti i dati
- ✅ Riavvia automaticamente l'app

#### Opzione B: Reset completo (solo se Opzione A non funziona)
```
Doppio click su: reset_e_avvia.bat
```
Questo:
- ⚠️ Elimina il database
- ⚠️ Perdi tutti i dati
- ✅ Riparte da zero

### STEP 3: Riprova l'Import
Dopo il riavvio:
```
Menu → Import Fogli Massivo → Import da Cartella
```

## 🎯 PREVENZIONE

### 1. Chiudi sempre correttamente l'app
Non chiudere brutalmente la finestra del terminale!

**Modo corretto**:
```
Nel terminale: CTRL + C
Aspetta "Server stopped"
```

### 2. Non aprire il database in altri programmi
Non aprire `gestionale_caccia.db` in:
- DB Browser for SQLite
- Excel
- Altri programmi database

mentre l'applicazione è in esecuzione.

### 3. Import Massivo: Fai batch piccoli
Se devi importare molti file (>50):
- Dividi in cartelle più piccole
- Importa 20-30 file alla volta

## 📋 Checklist Troubleshooting

Se l'errore persiste dopo lo sblocco:

- [ ] Ho chiuso completamente l'applicazione? (CTRL+C nel terminale)
- [ ] Ho aspettato "Server stopped"?
- [ ] Ho eseguito `sblocca_e_avvia.bat`?
- [ ] Il database non è aperto in altri programmi?
- [ ] Ho provato a riavviare il PC? (ultima risorsa)

## 🔧 Perché Succede?

Il database SQLite può essere "locked" quando:
1. **Operazione precedente non completata**: L'import precedente non ha finito correttamente
2. **Crash dell'applicazione**: L'app si è chiusa male
3. **File WAL non eliminati**: I file temporanei (.db-shm, .db-wal) sono rimasti

## ✨ Novità: WAL Mode Abilitato

Dalla versione corrente, il database usa **WAL mode** (Write-Ahead Logging):
- ✅ Permette letture durante scritture
- ✅ Riduce drasticamente i lock
- ✅ Migliora le performance
- ⚠️ Crea file temporanei: .db-shm e .db-wal (normale!)

**NON eliminare manualmente** questi file mentre l'app è in esecuzione!

## 🆘 Supporto Avanzato

Se il problema persiste:

### Verifica file database
```
Dir nella cartella dell'app, dovresti vedere:
  gestionale_caccia.db       <- Database principale
  gestionale_caccia.db-shm   <- File WAL (temporaneo)
  gestionale_caccia.db-wal   <- File WAL (temporaneo)
```

### Controlla processi in background
```
Task Manager (CTRL+SHIFT+ESC)
Cerca: python.exe o streamlit
Chiudi tutti i processi se presenti
```

### Backup prima del reset
Se devi fare reset completo:
```
1. Chiudi l'app
2. Copia gestionale_caccia.db in altra cartella
3. Esegui reset_e_avvia.bat
4. Reimporta i dati se necessario
```

## 📞 Domande Frequenti

**Q: L'errore appare solo durante l'import?**
A: Sì, è normale. L'import scrive molti dati rapidamente. Usa `sblocca_e_avvia.bat` e riprova.

**Q: Posso continuare a usare l'app se vedo file .db-wal?**
A: Sì! I file .db-wal sono normali con WAL mode abilitato. NON eliminarli manualmente.

**Q: Devo sempre usare sblocca_e_avvia.bat per avviare?**
A: No, solo se hai l'errore "database is locked". Normalmente usa `avvia.bat`.

**Q: I miei dati sono al sicuro?**
A: Sì. Lo sblocco elimina solo i file temporanei, non i dati. Il reset invece elimina tutto.

---

**Ultima modifica**: 30/01/2026
**Versione app**: 1.1 (WAL Mode)
