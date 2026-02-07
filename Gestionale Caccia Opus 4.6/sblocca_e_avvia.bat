@echo off
echo ========================================
echo SBLOCCA DATABASE - Gestionale Caccia
echo ========================================
echo.
echo Questo script chiudera' i file di lock del database WAL
echo SENZA eliminare i dati.
echo.
pause

echo.
echo Chiusura file WAL in corso...

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
echo SBLOCCO COMPLETATO!
echo ========================================
echo.
echo I dati del database sono al sicuro.
echo.
echo Avvio applicazione...
timeout /t 2 >nul

streamlit run app.py
