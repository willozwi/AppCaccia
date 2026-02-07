# GUIDA RISOLUZIONE PROBLEMI - Dati che non Persistono

## 🔍 Verifica che i Dati Siano Salvati

### STEP 1: Controlla il Database

Nella Dashboard (home page), attiva "Mostra Info Debug":

```
☑️ Mostra Info Debug
```

Vedrai:
- **Percorso database**: Es. `C:\...\gestionale_caccia.db`
- **Database esiste**: True/False

### STEP 2: Verifica Creazione Fogli

Quando crei i fogli:

```
Menu → Fogli Caccia A3 → Gestione Fogli
```

1. Attiva "🔍 Info Database"
2. Vedi "Fogli Totali nel Database" prima di creare
3. Crea i fogli (es. 20 fogli dal numero 497424)
4. Vedi "✅ Creati X nuovi fogli!"
5. La pagina si aggiorna automaticamente
6. Controlla che "Fogli Totali nel Database" sia aumentato

### STEP 3: Verifica Persistenza

1. Vai alla Dashboard
2. Torna a "Fogli Caccia A3"
3. I fogli devono essere ancora lì
4. Controlla "Fogli Totali nel Database"

## ⚠️ Problemi Comuni

### Problema: "Fogli scompaiono quando cambio pagina"

**Causa**: Database in posizione diversa ogni volta

**Soluzione**:
1. Chiudi completamente l'applicazione
2. Verifica che ci sia UN SOLO file `gestionale_caccia.db` nella cartella
3. Se ci sono più file `.db`, elimina tutti
4. Riavvia l'applicazione
5. Ricrea i fogli

### Problema: "Non vedo i fogli appena creati"

**Causa**: Anno non corretto

**Soluzione**:
1. Verifica che l'anno selezionato sia quello giusto (es. 2025)
2. Click su "🔄 Aggiorna"
3. Verifica il filtro "Filtra per Stato" → seleziona "Tutti"

### Problema: "Dice 'Nessun foglio presente' ma li ho creati"

**Causa**: Database multipli o errore nella query

**Soluzione**:
1. Attiva "🔍 Info Database"
2. Verifica "Fogli Totali nel Database"
3. Se il numero è corretto ma non vedi fogli:
   - Controlla l'anno selezionato
   - Prova a selezionare "Anno: 2025" (o l'anno corretto)
   - Click "🔄 Aggiorna"

### Problema: "Messaggio 'Creati 0 nuovi fogli'"

**Causa**: Fogli già esistenti

**Soluzione**:
- I fogli con quei numeri esistono già
- Prova con un numero iniziale diverso
- O elimina i fogli esistenti prima (non implementato nel gestionale base)

## 🔧 Reset Completo Database

Se i problemi persistono:

1. **Chiudi l'applicazione** (CTRL+C nel terminale)

2. **Trova il database**:
   - Windows: Cerca `gestionale_caccia.db` nella cartella dell'app
   - Dovrebbe essere nella stessa cartella di `app.py`

3. **Elimina il database**:
   ```
   DEL gestionale_caccia.db
   ```

4. **Riavvia l'applicazione**:
   ```
   streamlit run app.py
   ```

5. **Il database verrà ricreato vuoto**

6. **Ricomincia da zero**:
   - Aggiungi cacciatori
   - Crea fogli
   - Verifica persistenza

## ✅ Test di Verifica

Esegui questo test per verificare che tutto funzioni:

1. **Avvia l'app**
2. **Dashboard** → Attiva "Mostra Info Debug" → Annota percorso DB
3. **Anagrafe Cacciatori** → Aggiungi 1 cacciatore di test
4. **Dashboard** → Verifica "Cacciatori Attivi" = 1
5. **Fogli Caccia A3** → Crea 5 fogli
6. **Fogli Caccia A3** → Attiva "Info Database" → Verifica "Fogli Totali" = 5
7. **Dashboard** → Verifica "Fogli 2025" = 5
8. **Chiudi browser** (non l'app)
9. **Riapri browser** su `localhost:8501`
10. **Dashboard** → Verifica che i dati siano ancora lì

✅ Se il test passa → Tutto funziona correttamente!
❌ Se fallisce → Segui le soluzioni sopra

## 📁 Verifica File Database

Il database deve essere sempre nella **stessa cartella** di `app.py`:

```
gestionale_caccia/
├── app.py
├── database.py
├── gestionale_caccia.db  ← DEVE ESSERE QUI
└── pages/
    └── ...
```

**Non deve essere**:
- In una sottocartella temporanea
- In `C:\Users\...` diversa ogni volta
- Multipli database con nomi diversi

## 🆘 Supporto

Se i problemi persistono:
1. Attiva "Mostra Info Debug" nella Dashboard
2. Attiva "🔍 Info Database" in Fogli Caccia
3. Fai screenshot delle informazioni
4. Verifica che il percorso DB sia sempre lo stesso

---

**La persistenza dei dati dipende dall'uso dello stesso file database!**
