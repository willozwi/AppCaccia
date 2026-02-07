@echo off
echo ========================================
echo RESET DATABASE - Gestionale Caccia
echo ========================================
echo.
echo ATTENZIONE: Questo script eliminera' il database esistente!
echo Tutti i dati (cacciatori, fogli, libretti, ecc.) verranno persi.
echo.
echo Se vuoi fare un backup, premi CTRL+C ora e copia il file:
echo   gestionale_caccia.db
echo.
pause

echo.
echo Eliminazione database in corso...

if exist gestionale_caccia.db (
    del gestionale_caccia.db
    echo Database eliminato.
) else (
    echo Database non trovato (gia' eliminato o non ancora creato).
)

if exist gestionale_caccia.db-shm (
    del gestionale_caccia.db-shm
    echo File WAL-shm eliminato.
)

if exist gestionale_caccia.db-wal (
    del gestionale_caccia.db-wal
    echo File WAL eliminato.
)

echo.
echo ========================================
echo RESET COMPLETATO!
echo ========================================
echo.
echo Il database sara' ricreato automaticamente al prossimo avvio.
echo.
echo Avvio applicazione...
timeout /t 2 >nul

streamlit run app.py
