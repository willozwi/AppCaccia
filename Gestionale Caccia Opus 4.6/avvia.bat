@echo off
echo =========================================
echo  GESTIONALE CACCIA - POLIZIA LOCALE
echo =========================================
echo.
echo Avvio applicazione...
echo.

REM Attiva ambiente virtuale se esiste
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Ambiente virtuale attivato
) else (
    echo Nessun ambiente virtuale trovato
)

echo.
echo Avvio Streamlit...
echo L'applicazione si aprira' nel browser all'indirizzo:
echo http://localhost:8501
echo.
echo Premi CTRL+C per terminare l'applicazione
echo.

streamlit run app.py

pause
