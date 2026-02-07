"""
Script di migrazione degli stati per Gestionale Caccia
Normalizza tutti gli stati legacy ai nuovi valori standard

ATTENZIONE: Eseguire SOLO UNA VOLTA
Crea automaticamente un backup prima di procedere

Uso: python migrate_stati.py
"""

import sqlite3
import os
import shutil
import datetime as dt

# Import constants (se presente)
try:
    from constants import StatoFoglio
    STATI_MAPPING = StatoFoglio.LEGACY_MAPPING
    STATI_VALIDI = StatoFoglio.all()
except ImportError:
    print("⚠️ constants.py non trovato, uso mapping hardcoded")
    STATI_MAPPING = {
        'Consegnato': 'CONSEGNATO',
        'Stampato': 'RILASCIATO',
        'Da rinnovare': 'DISPONIBILE',
    }
    STATI_VALIDI = ['DISPONIBILE', 'CONSEGNATO', 'RILASCIATO', 'RESTITUITO']


def backup_database(db_path):
    """Crea backup del database"""
    timestamp = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = db_path.replace('.db', f'_backup_{timestamp}.db')
    
    print(f"💾 Creazione backup: {os.path.basename(backup_path)}")
    shutil.copy2(db_path, backup_path)
    print(f"✅ Backup creato: {backup_path}")
    
    return backup_path


def get_current_states(conn):
    """Verifica stati attuali"""
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT stato FROM fogli_caccia ORDER BY stato")
    return [row[0] for row in cursor.fetchall() if row[0]]


def migrate_states(db_path, dry_run=False):
    """Migra gli stati al nuovo formato"""
    
    if not os.path.exists(db_path):
        print(f"❌ Database non trovato: {db_path}")
        return False
    
    print(f"\n📂 Database: {db_path}")
    
    # Backup
    if not dry_run:
        backup_path = backup_database(db_path)
    
    # Connessione
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Stati attuali
    print("\n📊 Stati attuali nel database:")
    stati_attuali = get_current_states(conn)
    for stato in stati_attuali:
        print(f"  - {stato}")
    
    # Migrazione
    print(f"\n{'🔍 [DRY RUN]' if dry_run else '🔄'} Migrazione stati...")
    
    total_changes = 0
    
    for old_stato, new_stato in STATI_MAPPING.items():
        if not dry_run:
            cursor.execute("""
                UPDATE fogli_caccia 
                SET stato = ? 
                WHERE stato = ?
            """, (new_stato, old_stato))
            changed = cursor.rowcount
        else:
            cursor.execute("""
                SELECT COUNT(*) FROM fogli_caccia WHERE stato = ?
            """, (old_stato,))
            changed = cursor.fetchone()[0]
        
        if changed > 0:
            icon = "  🔍" if dry_run else "  ✅"
            print(f"{icon} {old_stato:20} → {new_stato:20}: {changed:4} record")
            total_changes += changed
    
    # Normalizza stati già in maiuscolo ma con maiuscolo/minuscolo misto
    for stato_valido in STATI_VALIDI:
        # Cerca varianti case-insensitive
        if not dry_run:
            cursor.execute("""
                UPDATE fogli_caccia 
                SET stato = ? 
                WHERE UPPER(stato) = ? AND stato != ?
            """, (stato_valido, stato_valido, stato_valido))
            changed = cursor.rowcount
        else:
            cursor.execute("""
                SELECT COUNT(*) FROM fogli_caccia 
                WHERE UPPER(stato) = ? AND stato != ?
            """, (stato_valido, stato_valido))
            changed = cursor.fetchone()[0]
        
        if changed > 0:
            icon = "  🔍" if dry_run else "  ✅"
            print(f"{icon} {stato_valido} (case-fix):      {changed:4} record")
            total_changes += changed
    
    # Commit
    if not dry_run:
        conn.commit()
        print(f"\n✅ Migrazione completata: {total_changes} record aggiornati")
    else:
        print(f"\n🔍 [DRY RUN] Verrebbero aggiornati: {total_changes} record")
    
    # Stati finali
    print("\n📊 Stati finali nel database:")
    stati_finali = get_current_states(conn)
    for stato in stati_finali:
        if stato in STATI_VALIDI:
            print(f"  ✅ {stato}")
        else:
            print(f"  ⚠️ {stato} (NON STANDARD)")
    
    # Verifica
    stati_non_standard = [s for s in stati_finali if s not in STATI_VALIDI]
    if stati_non_standard:
        print(f"\n⚠️ ATTENZIONE: {len(stati_non_standard)} stati non standard rilevati:")
        for stato in stati_non_standard:
            cursor.execute("SELECT COUNT(*) FROM fogli_caccia WHERE stato = ?", (stato,))
            count = cursor.fetchone()[0]
            print(f"   - '{stato}': {count} record")
    else:
        print("\n✅ Tutti gli stati sono normalizzati correttamente!")
    
    conn.close()
    return True


def main():
    """Main entry point"""
    print("="*70)
    print("MIGRAZIONE STATI DATABASE - GESTIONALE CACCIA")
    print("="*70)
    
    # Trova database
    db_path = os.path.join(os.path.dirname(__file__), 'gestionale_caccia.db')
    
    if not os.path.exists(db_path):
        print(f"\n❌ Database non trovato: {db_path}")
        print("Verifica di essere nella directory del progetto.")
        return
    
    print(f"\nDatabase trovato: {db_path}")
    print(f"Dimensione: {os.path.getsize(db_path) / 1024:.1f} KB")
    
    # DRY RUN prima
    print("\n" + "="*70)
    print("FASE 1: DRY RUN (Simulazione)")
    print("="*70)
    migrate_states(db_path, dry_run=True)
    
    # Conferma
    print("\n" + "="*70)
    print("FASE 2: ESECUZIONE EFFETTIVA")
    print("="*70)
    print("\n⚠️  ATTENZIONE: Questa operazione modificherà il database!")
    print("    Un backup verrà creato automaticamente.")
    
    risposta = input("\nProcedere con la migrazione? (s/n): ")
    
    if risposta.lower() in ['s', 'si', 'sì', 'y', 'yes']:
        print("\n🚀 Avvio migrazione...")
        success = migrate_states(db_path, dry_run=False)
        
        if success:
            print("\n" + "="*70)
            print("✅ MIGRAZIONE COMPLETATA CON SUCCESSO!")
            print("="*70)
            print("\n📋 Prossimi passi:")
            print("  1. Verifica che l'applicazione funzioni correttamente")
            print("  2. Se OK, puoi eliminare i file di backup")
            print("  3. Usa i file corretti per usare constants.py nel codice")
        else:
            print("\n❌ Migrazione fallita")
    else:
        print("\n❌ Operazione annullata dall'utente")


if __name__ == "__main__":
    main()
