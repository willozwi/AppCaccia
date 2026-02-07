#!/bin/bash

echo "========================================="
echo " GESTIONALE CACCIA - POLIZIA LOCALE"
echo "========================================="
echo ""
echo "Avvio applicazione..."
echo ""

# Attiva ambiente virtuale se esiste
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Ambiente virtuale attivato"
else
    echo "Nessun ambiente virtuale trovato"
fi

echo ""
echo "Avvio Streamlit..."
echo "L'applicazione si aprirà nel browser all'indirizzo:"
echo "http://localhost:8501"
echo ""
echo "Premi CTRL+C per terminare l'applicazione"
echo ""

streamlit run app.py
