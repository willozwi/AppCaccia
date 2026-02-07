#!/usr/bin/env python3
"""
Verifica Datetime Shadowing

Scansiona tutti i file Python nel progetto per identificare potenziali
shadowing del modulo datetime (assegnazioni a variabili locali chiamate 'datetime').

Esegui questo script per verificare che non ci siano variabili locali
che ombreggiano l'import datetime.
"""

import os
import re
import sys

def check_datetime_shadowing(project_dir="."):
    """Scansiona i file Python per datetime shadowing"""
    
    # Pattern da cercare (solo assegnazioni che ombreggiano davvero)
    patterns = [
        (r'^\s*datetime\s*=', 'Assegnazione a variabile datetime'),
        (r'for\s+datetime\s+in\s+', 'Loop variabile datetime'),
    ]
    
    issues_found = []
    files_scanned = 0
    
    # Scansiona tutti i file .py
    for root, dirs, files in os.walk(project_dir):
        # Ignora directory comuni
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv', 'venv', 'node_modules']]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                files_scanned += 1
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    for line_num, line in enumerate(lines, 1):
                        for pattern, description in patterns:
                            if re.search(pattern, line):
                                issues_found.append({
                                    'file': filepath,
                                    'line': line_num,
                                    'content': line.strip(),
                                    'issue': description
                                })
                
                except Exception as e:
                    print(f"⚠️  Errore lettura {filepath}: {e}")
    
   # Report
    print("=" * 70)
    print("VERIFICA DATETIME SHADOWING")
    print("=" * 70)
    print(f"File scansionati: {files_scanned}")
    print()
    
    if issues_found:
        print(f"[X] TROVATI {len(issues_found)} POTENZIALI PROBLEMI:\n")
        
        for issue in issues_found:
            print(f"File: {issue['file']}")
            print(f"   Riga {issue['line']}: {issue['issue']}")
            print(f"   Codice: {issue['content']}")
            print()
        
        print("=" * 70)
        print("AZIONE RICHIESTA: Rinomina le variabili evidenziate")
        print("=" * 70)
        return 1  # Exit code 1 per errori
    
    else:
        print("[OK] NESSUN PROBLEMA RILEVATO")
        print()
        print("Tutti i file sono puliti: nessuna variabile locale chiamata 'datetime'")
        print("=" * 70)
        return 0  # Exit code 0 per successo


if __name__ == "__main__":
    project_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    exit_code = check_datetime_shadowing(project_dir)
    sys.exit(exit_code)
