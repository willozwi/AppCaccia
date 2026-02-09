import sqlite3
import datetime as dt
from typing import Optional, List, Dict
import os

class GestionaleCacciaDB:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Usa percorso assoluto nella directory dello script principale
            # Questo assicura che il database sia sempre nello stesso posto
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_path = os.path.join(script_dir, "gestionale_caccia.db")
        else:
            self.db_path = db_path
        
        print(f"[DEBUG] Database path: {self.db_path}")  # Per debug
        self.init_database()
    
    
    def get_connection(self):
        """Crea connessione al database con timeout aumentato e WAL mode"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        
        # TASK 2: Blindare database contro lock
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA busy_timeout=5000')
        
        return conn
    
    def init_database(self):
        """Inizializza il database con le tabelle necessarie"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabella cacciatori
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cacciatori (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_tessera TEXT UNIQUE NOT NULL,
                cognome TEXT NOT NULL,
                nome TEXT NOT NULL,
                data_nascita DATE,
                luogo_nascita TEXT,
                codice_fiscale TEXT UNIQUE,
                indirizzo TEXT,
                comune TEXT,
                provincia TEXT,
                cap TEXT,
                telefono TEXT,
                cellulare TEXT,
                email TEXT,
                attivo INTEGER DEFAULT 1,
                note TEXT,
                data_inserimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_modifica TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabella libretti regionali
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS libretti_regionali (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cacciatore_id INTEGER NOT NULL,
                anno INTEGER NOT NULL,
                numero_libretto TEXT UNIQUE NOT NULL,
                data_rilascio DATE,
                data_scadenza DATE,
                stato TEXT DEFAULT 'ATTIVO',
                note TEXT,
                file_path TEXT,
                data_inserimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_modifica TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cacciatore_id) REFERENCES cacciatori(id),
                UNIQUE(cacciatore_id, anno)
            )
        """)
        
        # Tabella fogli caccia A3
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fogli_caccia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_foglio TEXT UNIQUE NOT NULL,
                anno INTEGER NOT NULL,
                cacciatore_id INTEGER,
                tipo TEXT DEFAULT 'A3',
                data_consegna DATE,
                consegnato_da TEXT,
                data_rilascio DATE,
                rilasciato_a TEXT,
                data_restituzione DATE,
                restituito_da TEXT,
                stato TEXT DEFAULT 'DISPONIBILE',
                consegnato INTEGER NOT NULL DEFAULT 0,
                restituito INTEGER NOT NULL DEFAULT 0,
                note TEXT,
                file_path TEXT,
                data_inserimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_modifica TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cacciatore_id) REFERENCES cacciatori(id)
            )
        """)
        
        # Tabella autorizzazioni RAS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS autorizzazioni_ras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cacciatore_id INTEGER NOT NULL,
                anno INTEGER NOT NULL,
                tipo_autorizzazione TEXT,
                numero_protocollo TEXT,
                data_richiesta DATE,
                data_rilascio DATE,
                data_scadenza DATE,
                stato TEXT DEFAULT 'IN_ATTESA',
                note TEXT,
                file_path TEXT,
                data_inserimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_modifica TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cacciatore_id) REFERENCES cacciatori(id)
            )
        """)
        
        # Tabella documenti
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documenti (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cacciatore_id INTEGER,
                tipo_documento TEXT NOT NULL,
                nome_file TEXT NOT NULL,
                file_path TEXT NOT NULL,
                descrizione TEXT,
                anno INTEGER,
                data_documento DATE,
                data_inserimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cacciatore_id) REFERENCES cacciatori(id)
            )
        """)
        
        # Tabella log attività
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS log_attivita (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                utente TEXT,
                azione TEXT NOT NULL,
                tabella TEXT,
                record_id INTEGER,
                dettagli TEXT,
                data_ora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabella allegati restituzioni (scansioni fogli restituiti)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS restituzioni_allegati (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_foglio TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                uploaded_by TEXT,
                FOREIGN KEY (numero_foglio) REFERENCES fogli_caccia(numero_foglio)
            )
        """)
        
        # Indice per query veloci su numero_foglio
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_restituzioni_allegati_foglio 
            ON restituzioni_allegati(numero_foglio)
        """)
        
        
        
        # ========== MIGRATION SAFE: Colonna consegnato ==========
        # Aggiungi colonna consegnato se non esiste già
        try:
            cursor.execute("SELECT consegnato FROM fogli_caccia LIMIT 1")
        except sqlite3.OperationalError:
            # Colonna non esiste, aggiungila
            cursor.execute("ALTER TABLE fogli_caccia ADD COLUMN consegnato INTEGER NOT NULL DEFAULT 0")
            conn.commit()

        # ========== MIGRATION SAFE: Colonna restituito ==========
        # Aggiungi colonna restituito se non esiste già
        try:
            cursor.execute("SELECT restituito FROM fogli_caccia LIMIT 1")
        except sqlite3.OperationalError:
            # Colonna non esiste, aggiungila
            cursor.execute("ALTER TABLE fogli_caccia ADD COLUMN restituito INTEGER NOT NULL DEFAULT 0")
            conn.commit()

        # ========== MIGRATION SAFE: Colonna stampato ==========
        # Aggiungi colonna stampato se non esiste già
        try:
            cursor.execute("SELECT stampato FROM fogli_caccia LIMIT 1")
        except sqlite3.OperationalError:
            # Colonna non esiste, aggiungila
            cursor.execute("ALTER TABLE fogli_caccia ADD COLUMN stampato INTEGER NOT NULL DEFAULT 0")
            conn.commit()
        
        # ========== INDICI PER PERFORMANCE ==========
        # Indici cacciatori
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cacciatori_cf ON cacciatori(codice_fiscale)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cacciatori_tessera ON cacciatori(numero_tessera)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cacciatori_attivo ON cacciatori(attivo)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cacciatori_cognome ON cacciatori(cognome)")
        
        # Indici fogli_caccia
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_fogli_anno ON fogli_caccia(anno)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_fogli_stato ON fogli_caccia(stato)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_fogli_cacciatore ON fogli_caccia(cacciatore_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_fogli_numero ON fogli_caccia(numero_foglio)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_fogli_consegnato ON fogli_caccia(consegnato)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_fogli_restituito ON fogli_caccia(restituito)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_fogli_stampato ON fogli_caccia(stampato)")
        
        # Indici libretti_regionali
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_libretti_anno ON libretti_regionali(anno)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_libretti_cacciatore ON libretti_regionali(cacciatore_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_libretti_stato ON libretti_regionali(stato)")
        
        # Indici autorizzazioni_ras
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_autorizzazioni_stato ON autorizzazioni_ras(stato)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_autorizzazioni_anno ON autorizzazioni_ras(anno)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_autorizzazioni_cacciatore ON autorizzazioni_ras(cacciatore_id)")
        
        # Indici log_attivita
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_log_data ON log_attivita(data_ora)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_log_tabella ON log_attivita(tabella)")
        
        conn.commit()
        conn.close()
    
    # ========== GESTIONE CACCIATORI ==========
    
    def aggiungi_cacciatore(self, dati: Dict) -> int:
        """Aggiunge un nuovo cacciatore"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO cacciatori (
                numero_tessera, cognome, nome, data_nascita, luogo_nascita,
                codice_fiscale, indirizzo, comune, provincia, cap,
                telefono, cellulare, email, note
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dati.get('numero_tessera'),
            dati.get('cognome'),
            dati.get('nome'),
            dati.get('data_nascita'),
            dati.get('luogo_nascita'),
            dati.get('codice_fiscale'),
            dati.get('indirizzo'),
            dati.get('comune'),
            dati.get('provincia'),
            dati.get('cap'),
            dati.get('telefono'),
            dati.get('cellulare'),
            dati.get('email'),
            dati.get('note')
        ))
        
        cacciatore_id = cursor.lastrowid
        
        self.log_attivita('SISTEMA', 'INSERT', 'cacciatori', cacciatore_id, 
                         f"Aggiunto cacciatore: {dati.get('cognome')} {dati.get('nome')}")
        
        conn.commit()
        conn.close()
        return cacciatore_id
    
    def modifica_cacciatore(self, cacciatore_id: int, dati: Dict):
        """Modifica i dati di un cacciatore"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE cacciatori SET
                numero_tessera = ?,
                cognome = ?,
                nome = ?,
                data_nascita = ?,
                luogo_nascita = ?,
                codice_fiscale = ?,
                indirizzo = ?,
                comune = ?,
                provincia = ?,
                cap = ?,
                telefono = ?,
                cellulare = ?,
                email = ?,
                note = ?,
                data_modifica = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            dati.get('numero_tessera'),
            dati.get('cognome'),
            dati.get('nome'),
            dati.get('data_nascita'),
            dati.get('luogo_nascita'),
            dati.get('codice_fiscale'),
            dati.get('indirizzo'),
            dati.get('comune'),
            dati.get('provincia'),
            dati.get('cap'),
            dati.get('telefono'),
            dati.get('cellulare'),
            dati.get('email'),
            dati.get('note'),
            cacciatore_id
        ))
        
        self.log_attivita('SISTEMA', 'UPDATE', 'cacciatori', cacciatore_id,
                         f"Modificato cacciatore: {dati.get('cognome')} {dati.get('nome')}")
        
        conn.commit()
        conn.close()
    
    def elimina_cacciatore(self, cacciatore_id: int):
        """Disattiva un cacciatore (soft delete)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE cacciatori SET attivo = 0, data_modifica = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (cacciatore_id,))
        
        self.log_attivita('SISTEMA', 'DELETE', 'cacciatori', cacciatore_id,
                         "Disattivato cacciatore")
        
        conn.commit()
        conn.close()
    
    def get_cacciatore_by_cf(self, codice_fiscale: str):
        """
        Cerca un cacciatore per codice fiscale
        Ritorna il cacciatore o None se non trovato
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM cacciatori 
            WHERE UPPER(codice_fiscale) = UPPER(?)
            AND attivo = 1
        """, (codice_fiscale,))
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def aggiorna_cacciatore(self, cacciatore_id: int, dati_parziali: Dict):
        """
        Aggiorna solo i campi specificati di un cacciatore
        Usato per import automatico (non sovrascrive tutto)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Mappatura campi logici → campi database
        field_mapping = {
            'data_nascita': 'data_nascita',
            'comune_residenza': 'comune',  # Mapping!
            'numero_licenza': 'numero_tessera',  # Mapping!
            'telefono': 'telefono',
            'cellulare': 'cellulare',
            'email': 'email',
            'indirizzo': 'indirizzo',
            'cap': 'cap'
        }
        
        # Costruisci query dinamica con solo i campi forniti
        set_clauses = []
        values = []
        
        for logical_field, value in dati_parziali.items():
            if logical_field in field_mapping:
                db_field = field_mapping[logical_field]
                set_clauses.append(f"{db_field} = ?")
                values.append(value)
        
        if not set_clauses:
            return  # Nessun campo da aggiornare
        
        # Aggiungi data modifica
        set_clauses.append("data_modifica = CURRENT_TIMESTAMP")
        values.append(cacciatore_id)
        
        query = f"""
            UPDATE cacciatori SET
            {', '.join(set_clauses)}
            WHERE id = ?
        """
        
        cursor.execute(query, values)
        
        self.log_attivita('SISTEMA', 'UPDATE', 'cacciatori', cacciatore_id,
                         f"Aggiornato cacciatore (import): {', '.join(dati_parziali.keys())}")
        
        conn.commit()
        conn.close()
    
    def get_cacciatore(self, cacciatore_id: int) -> Optional[Dict]:
        """Recupera i dati di un cacciatore"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM cacciatori WHERE id = ?", (cacciatore_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_tutti_cacciatori(self, solo_attivi: bool = True) -> List[Dict]:
        """Recupera tutti i cacciatori"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM cacciatori"
        if solo_attivi:
            query += " WHERE attivo = 1"
        query += " ORDER BY cognome, nome"
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def cerca_cacciatori(self, termine: str) -> List[Dict]:
        """Cerca cacciatori per nome, cognome o numero tessera"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM cacciatori 
            WHERE attivo = 1 AND (
                cognome LIKE ? OR 
                nome LIKE ? OR 
                numero_tessera LIKE ? OR
                codice_fiscale LIKE ?
            )
            ORDER BY cognome, nome
        """, (f"%{termine}%", f"%{termine}%", f"%{termine}%", f"%{termine}%"))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ========== GESTIONE LIBRETTI REGIONALI ==========
    
    def aggiungi_libretto(self, dati: Dict) -> int:
        """Aggiunge un nuovo libretto regionale"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO libretti_regionali (
                cacciatore_id, anno, numero_libretto, data_rilascio,
                data_scadenza, stato, note, file_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dati.get('cacciatore_id'),
            dati.get('anno'),
            dati.get('numero_libretto'),
            dati.get('data_rilascio'),
            dati.get('data_scadenza'),
            dati.get('stato', 'ATTIVO'),
            dati.get('note'),
            dati.get('file_path')
        ))
        
        libretto_id = cursor.lastrowid
        
        self.log_attivita('SISTEMA', 'INSERT', 'libretti_regionali', libretto_id,
                         f"Aggiunto libretto {dati.get('numero_libretto')} anno {dati.get('anno')}")
        
        conn.commit()
        conn.close()
        return libretto_id
    
    def get_libretti_cacciatore(self, cacciatore_id: int) -> List[Dict]:
        """Recupera tutti i libretti di un cacciatore"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM libretti_regionali 
            WHERE cacciatore_id = ?
            ORDER BY anno DESC
        """, (cacciatore_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_libretti_anno(self, anno: int) -> List[Dict]:
        """Recupera tutti i libretti di un anno"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT l.*, c.cognome, c.nome, c.numero_tessera
            FROM libretti_regionali l
            JOIN cacciatori c ON l.cacciatore_id = c.id
            WHERE l.anno = ?
            ORDER BY c.cognome, c.nome
        """, (anno,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ========== GESTIONE FOGLI CACCIA ==========
    
    def aggiungi_foglio_caccia(self, dati: Dict) -> int:
        """Aggiunge un nuovo foglio caccia"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO fogli_caccia (
                    numero_foglio, anno, cacciatore_id, tipo,
                    data_consegna, consegnato_da, data_rilascio, rilasciato_a,
                    data_restituzione, restituito_da, stato, note, file_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dati.get('numero_foglio'),
                dati.get('anno'),
                dati.get('cacciatore_id'),
                dati.get('tipo', 'A3'),
                dati.get('data_consegna'),
                dati.get('consegnato_da'),
                dati.get('data_rilascio'),
                dati.get('rilasciato_a'),
                dati.get('data_restituzione'),
                dati.get('restituito_da'),
                dati.get('stato', 'DISPONIBILE'),
                dati.get('note'),
                dati.get('file_path')
            ))
            
            foglio_id = cursor.lastrowid
            conn.commit()
            
            # Log dopo il commit per evitare lock
            try:
                self.log_attivita('SISTEMA', 'INSERT', 'fogli_caccia', foglio_id,
                                 f"Aggiunto foglio {dati.get('numero_foglio')}")
            except:
                pass  # Non bloccare per errori di log
            
            return foglio_id
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def modifica_foglio_caccia(self, foglio_id: int, dati: Dict):
        """Modifica un foglio caccia"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE fogli_caccia SET
                cacciatore_id = ?,
                data_consegna = ?,
                consegnato_da = ?,
                data_rilascio = ?,
                rilasciato_a = ?,
                data_restituzione = ?,
                restituito_da = ?,
                stato = ?,
                note = ?,
                data_modifica = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            dati.get('cacciatore_id'),
            dati.get('data_consegna'),
            dati.get('consegnato_da'),
            dati.get('data_rilascio'),
            dati.get('rilasciato_a'),
            dati.get('data_restituzione'),
            dati.get('restituito_da'),
            dati.get('stato'),
            dati.get('note'),
            foglio_id
        ))
        
        self.log_attivita('SISTEMA', 'UPDATE', 'fogli_caccia', foglio_id,
                         f"Modificato foglio caccia")
        
        conn.commit()
        conn.close()
    
    def set_consegnato(self, foglio_id: int, value: bool) -> None:
        """Imposta lo stato consegnato di un foglio (checkbox) e aggiorna il campo stato"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Aggiorna sia il campo consegnato che il campo stato
            # Se consegnato=True -> stato='CONSEGNATO'
            # Se consegnato=False -> stato='DISPONIBILE' (o mantiene lo stato precedente se era RILASCIATO/RESTITUITO)
            
            if value:
                # Checkbox spuntata -> imposta CONSEGNATO
                cursor.execute("""
                    UPDATE fogli_caccia 
                    SET consegnato = 1, 
                        stato = 'CONSEGNATO',
                        data_modifica = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (foglio_id,))
            else:
                # Checkbox tolta -> riporta a DISPONIBILE solo se era CONSEGNATO
                cursor.execute("""
                    UPDATE fogli_caccia 
                    SET consegnato = 0,
                        stato = CASE 
                            WHEN stato = 'CONSEGNATO' THEN 'DISPONIBILE'
                            ELSE stato
                        END,
                        data_modifica = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (foglio_id,))
            
            conn.commit()
            
            # Log opzionale (non bloccante)
            try:
                self.log_attivita('SISTEMA', 'UPDATE', 'fogli_caccia', foglio_id,
                                 f"Consegnato: {value}, stato aggiornato")
            except:
                pass
                
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            raise e
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass
    
    def toggle_consegnato(self, foglio_id: int) -> bool:
        """Toggle stato consegnato e ritorna nuovo valore, mantenendo stato coerente"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Leggi valore attuale
            cursor.execute("SELECT consegnato, stato FROM fogli_caccia WHERE id = ?", (foglio_id,))
            row = cursor.fetchone()

            if not row:
                raise ValueError(f"Foglio ID {foglio_id} non trovato")

            current_value = row[0]
            new_value = 1 if current_value == 0 else 0

            # Aggiorna consegnato E stato in modo coerente
            if new_value == 1:
                cursor.execute("""
                    UPDATE fogli_caccia
                    SET consegnato = 1,
                        stato = 'CONSEGNATO',
                        data_modifica = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (foglio_id,))
            else:
                cursor.execute("""
                    UPDATE fogli_caccia
                    SET consegnato = 0,
                        stato = CASE
                            WHEN stato = 'CONSEGNATO' THEN 'DISPONIBILE'
                            ELSE stato
                        END,
                        data_modifica = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (foglio_id,))

            conn.commit()

            # Log (non bloccante)
            try:
                self.log_attivita('SISTEMA', 'UPDATE', 'fogli_caccia', foglio_id,
                                 f"Toggle consegnato: {bool(new_value)}, stato aggiornato")
            except Exception:
                pass

            return bool(new_value)
            
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            raise e
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass
    
    def set_restituito(self, foglio_id: int, value: bool) -> None:
        """Imposta lo stato restituito di un foglio (checkbox) e aggiorna il campo stato"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Aggiorna sia il campo restituito che il campo stato
            # Se restituito=True -> stato='RESTITUITO'
            # Se restituito=False -> stato='RILASCIATO' (o mantiene lo stato precedente)
            
            if value:
                # Checkbox spuntata -> imposta RESTITUITO
                cursor.execute("""
                    UPDATE fogli_caccia 
                    SET restituito = 1,
                        stato = 'RESTITUITO',
                        data_modifica = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (foglio_id,))
            else:
                # Checkbox tolta -> riporta a RILASCIATO solo se era RESTITUITO
                cursor.execute("""
                    UPDATE fogli_caccia 
                    SET restituito = 0,
                        stato = CASE 
                            WHEN stato = 'RESTITUITO' THEN 'RILASCIATO'
                            ELSE stato
                        END,
                        data_modifica = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (foglio_id,))
            
            conn.commit()
            
            # Log opzionale
            try:
                self.log_attivita('SISTEMA', 'UPDATE', 'fogli_caccia', foglio_id,
                                 f"Restituito: {value}, stato aggiornato")
            except:
                pass
                
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            raise e
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass
    
    def set_stampato(self, foglio_id: int, value: bool) -> None:
        """Imposta lo stato stampato di un foglio (checkbox)"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE fogli_caccia
                SET stampato = ?, data_modifica = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (1 if value else 0, foglio_id))

            conn.commit()

            try:
                self.log_attivita('SISTEMA', 'UPDATE', 'fogli_caccia', foglio_id,
                                 f"Stampato: {value}")
            except:
                pass

        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            raise e
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass

    def set_data_rilascio(self, foglio_id: int, data: str) -> None:
        """Imposta la data rilascio di un foglio (campo editabile)"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE fogli_caccia 
                SET data_rilascio = ?, data_modifica = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (data if data else None, foglio_id))
            
            conn.commit()
            
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            raise e
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass
    
    
    def set_data_restituzione(self, foglio_id: int, value) -> None:
        """Imposta la data restituzione di un foglio (campo editabile)"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Convert date object to string if needed, or set to None
            if value is None:
                data_str = None
            elif hasattr(value, 'strftime'):
                # It's a date object
                data_str = value.strftime('%Y-%m-%d')
            else:
                # It's already a string or None
                data_str = value if value else None
            
            cursor.execute("""
                UPDATE fogli_caccia 
                SET data_restituzione = ?, data_modifica = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (data_str, foglio_id))
            
            conn.commit()
            
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            raise e
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass
    
    def update_contatto_telefonico(self, cacciatore_id: int, value: str) -> None:
        """Aggiorna il contatto telefonico (cellulare) di un cacciatore"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cellulare = value.strip() if value else None

            cursor.execute("""
                UPDATE cacciatori
                SET cellulare = ?
                WHERE id = ?
            """, (cellulare, cacciatore_id))

            conn.commit()

        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            raise e
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass

    def aggiorna_restituzione_foglio(self, foglio_id: int, data_restituzione: str,
                                     restituito_da: str = None, note: str = None) -> None:
        """Aggiorna i dati di restituzione di un foglio"""
        conn = None
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                
                # Convert date if needed
                if hasattr(data_restituzione, 'strftime'):
                    data_str = data_restituzione.strftime('%Y-%m-%d')
                else:
                    data_str = data_restituzione
                
                cursor.execute("""
                    UPDATE fogli_caccia 
                    SET data_restituzione = ?, restituito_da = ?, note = ?, 
                        data_modifica = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (data_str, restituito_da, note, foglio_id))
                
                conn.commit()
                
                # Log activity
                try:
                    self.log_attivita('SISTEMA', 'UPDATE', 'fogli_caccia', foglio_id,
                                     f"Aggiornata restituzione: data={data_str}")
                except:
                    pass
                
                break  # Success
                
            except Exception as e:
                if "database is locked" in str(e) and retry_count < max_retries - 1:
                    retry_count += 1
                    import time
                    time.sleep(0.1 * retry_count)
                    continue
                else:
                    if conn:
                        try:
                            conn.rollback()
                        except:
                            pass
                    raise e
            finally:
                if conn:
                    try:
                        conn.close()
                    except:
                        pass
    
    def annulla_restituzione_foglio(self, foglio_id: int) -> None:
        """Annulla la restituzione di un foglio (reset campi e stato a RILASCIATO)"""
        conn = None
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                
                # Reset restitution fields and change stato back to RILASCIATO
                cursor.execute("""
                    UPDATE fogli_caccia 
                    SET data_restituzione = NULL, 
                        restituito_da = NULL,
                        restituito = 0,
                        stato = 'RILASCIATO',
                        data_modifica = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (foglio_id,))
                
                conn.commit()
                
                # Log activity
                try:
                    self.log_attivita('SISTEMA', 'DELETE', 'fogli_caccia', foglio_id,
                                     "Annullata restituzione foglio")
                except:
                    pass
                
                break  # Success
                
            except Exception as e:
                if "database is locked" in str(e) and retry_count < max_retries - 1:
                    retry_count += 1
                    import time
                    time.sleep(0.1 * retry_count)
                    continue
                else:
                    if conn:
                        try:
                            conn.rollback()
                        except:
                            pass
                    raise e
            finally:
                if conn:
                    try:
                        conn.close()
                    except:
                        pass
    
    # ========== ALLEGATI RESTITUZIONI ==========
    
    def get_restituzione_allegati(self, numero_foglio: str) -> List[Dict]:
        """Recupera gli allegati (scansioni) per un foglio restituito"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, numero_foglio, file_name, file_path, uploaded_at, uploaded_by
            FROM restituzioni_allegati
            WHERE numero_foglio = ?
            ORDER BY uploaded_at DESC
        """, (numero_foglio,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def count_allegati_per_foglio(self, lista_num_foglio: List[str]) -> Dict[str, int]:
        """Conta gli allegati per una lista di fogli (batch query efficiente)"""
        if not lista_num_foglio:
            return {}
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Crea placeholders per query IN
        placeholders = ','.join('?' * len(lista_num_foglio))
        
        cursor.execute(f"""
            SELECT numero_foglio, COUNT(*) as count
            FROM restituzioni_allegati
            WHERE numero_foglio IN ({placeholders})
            GROUP BY numero_foglio
        """, lista_num_foglio)
        
        rows = cursor.fetchall()
        conn.close()
        
        # Converti in dizionario
        return {row['numero_foglio']: row['count'] for row in rows}
    
    def add_restituzione_allegato(self, numero_foglio: str, file_name: str, 
                                   file_path: str, uploaded_by: str = None) -> int:
        """Aggiunge un allegato (scansione) per un foglio restituito"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO restituzioni_allegati 
                (numero_foglio, file_name, file_path, uploaded_by, uploaded_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (numero_foglio, file_name, file_path, uploaded_by))
            
            allegato_id = cursor.lastrowid
            conn.commit()
            
            # Log activity
            try:
                self.log_attivita('SISTEMA', 'INSERT', 'restituzioni_allegati', allegato_id,
                                 f"Allegato caricato: {file_name} per foglio {numero_foglio}")
            except:
                pass
            
            return allegato_id
            
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            raise e
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass
    
    def delete_restituzione_allegato(self, allegato_id: int) -> Dict:
        """Elimina un allegato e ritorna le sue info per cancellare il file"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Prima recupera le info del file
            cursor.execute("""
                SELECT numero_foglio, file_name, file_path
                FROM restituzioni_allegati
                WHERE id = ?
            """, (allegato_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            file_info = dict(row)
            
            # Elimina il record
            cursor.execute("DELETE FROM restituzioni_allegati WHERE id = ?", (allegato_id,))
            conn.commit()
            
            # Log activity
            try:
                self.log_attivita('SISTEMA', 'DELETE', 'restituzioni_allegati', allegato_id,
                                 f"Allegato eliminato: {file_info['file_name']}")
            except:
                pass
            
            return file_info
            
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            raise e
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass
    
    
    
    def get_fogli_anno(self, anno: int, stato: Optional[str] = None) -> List[Dict]:
        """Recupera i fogli caccia di un anno, opzionalmente filtrati per stato"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT f.*, c.cognome, c.nome, c.numero_tessera, c.telefono, c.cellulare
            FROM fogli_caccia f
            LEFT JOIN cacciatori c ON f.cacciatore_id = c.id
            WHERE f.anno = ?
        """
        params = [anno]

        if stato:
            query += " AND f.stato = ?"
            params.append(stato)

        query += " ORDER BY f.numero_foglio"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_fogli_anno_ordinati_per_cacciatore(self, anno: int, stato: Optional[str] = None) -> List[Dict]:
        """Recupera i fogli caccia di un anno ordinati alfabeticamente per cacciatore (Cognome → Nome → N. Foglio)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT f.*, c.cognome, c.nome, c.numero_tessera, c.telefono, c.cellulare
            FROM fogli_caccia f
            LEFT JOIN cacciatori c ON f.cacciatore_id = c.id
            WHERE f.anno = ?
        """
        params = [anno]
        
        if stato:
            query += " AND f.stato = ?"
            params.append(stato)
        
        # Ordinamento alfabetico: Cognome (case-insensitive) → Nome → Numero Foglio
        # UPPER() gestisce correttamente caratteri speciali come accenti
        query += " ORDER BY UPPER(COALESCE(c.cognome, f.rilasciato_a, '')), UPPER(COALESCE(c.nome, '')), f.numero_foglio"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_statistiche_fogli(self, anno: int) -> Dict:
        """Recupera statistiche sui fogli caccia di un anno"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as totale,
                SUM(CASE WHEN UPPER(stato) = 'DISPONIBILE' THEN 1 ELSE 0 END) as disponibili,
                SUM(CASE WHEN UPPER(stato) = 'CONSEGNATO' THEN 1 ELSE 0 END) as consegnati,
                SUM(CASE WHEN UPPER(stato) IN ('STAMPATO', 'RILASCIATO') THEN 1 ELSE 0 END) as rilasciati,
                SUM(CASE WHEN UPPER(stato) LIKE '%RINNOVARE%' THEN 1 ELSE 0 END) as da_rinnovare,
                SUM(CASE WHEN UPPER(stato) = 'RESTITUITO' THEN 1 ELSE 0 END) as restituiti
            FROM fogli_caccia
            WHERE anno = ?
        """, (anno,))
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else {}

    def cancella_tutti_fogli_anno(self, anno: int) -> int:
        """Cancella tutti i fogli caccia di un anno specifico e i relativi allegati.
        Restituisce il numero di fogli eliminati."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Recupera i numeri foglio dell'anno per eliminare gli allegati correlati
            cursor.execute(
                "SELECT numero_foglio FROM fogli_caccia WHERE anno = ?", (anno,)
            )
            numeri = [row['numero_foglio'] for row in cursor.fetchall()]

            allegati_eliminati = 0
            if numeri:
                # Elimina allegati restituzioni collegati ai fogli dell'anno
                placeholders = ','.join('?' * len(numeri))
                cursor.execute(
                    f"DELETE FROM restituzioni_allegati WHERE numero_foglio IN ({placeholders})",
                    numeri
                )
                allegati_eliminati = cursor.rowcount

            # Elimina tutti i fogli dell'anno
            cursor.execute("DELETE FROM fogli_caccia WHERE anno = ?", (anno,))
            fogli_eliminati = cursor.rowcount

            conn.commit()

            # Log attività
            self.log_attivita(
                'SISTEMA', 'DELETE_ALL', 'fogli_caccia', 0,
                f"Cancellati {fogli_eliminati} fogli e {allegati_eliminati} allegati per anno {anno}"
            )

            return fogli_eliminati
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    # ========== GESTIONE AUTORIZZAZIONI RAS ==========
    
    def aggiungi_autorizzazione(self, dati: Dict) -> int:
        """Aggiunge una nuova richiesta di autorizzazione RAS"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO autorizzazioni_ras (
                cacciatore_id, anno, tipo_autorizzazione, numero_protocollo,
                data_richiesta, data_rilascio, data_scadenza, stato, note, file_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dati.get('cacciatore_id'),
            dati.get('anno'),
            dati.get('tipo_autorizzazione'),
            dati.get('numero_protocollo'),
            dati.get('data_richiesta'),
            dati.get('data_rilascio'),
            dati.get('data_scadenza'),
            dati.get('stato', 'IN_ATTESA'),
            dati.get('note'),
            dati.get('file_path')
        ))
        
        auth_id = cursor.lastrowid
        
        self.log_attivita('SISTEMA', 'INSERT', 'autorizzazioni_ras', auth_id,
                         f"Aggiunta autorizzazione RAS")
        
        conn.commit()
        conn.close()
        return auth_id
    
    def get_autorizzazioni_cacciatore(self, cacciatore_id: int) -> List[Dict]:
        """Recupera tutte le autorizzazioni di un cacciatore"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM autorizzazioni_ras 
            WHERE cacciatore_id = ?
            ORDER BY anno DESC, data_richiesta DESC
        """, (cacciatore_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ========== GESTIONE DOCUMENTI ==========
    
    def aggiungi_documento(self, dati: Dict) -> int:
        """Aggiunge un documento"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO documenti (
                cacciatore_id, tipo_documento, nome_file, file_path,
                descrizione, anno, data_documento
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            dati.get('cacciatore_id'),
            dati.get('tipo_documento'),
            dati.get('nome_file'),
            dati.get('file_path'),
            dati.get('descrizione'),
            dati.get('anno'),
            dati.get('data_documento')
        ))
        
        doc_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return doc_id
    
    def get_documenti_cacciatore(self, cacciatore_id: int) -> List[Dict]:
        """Recupera tutti i documenti di un cacciatore"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM documenti 
            WHERE cacciatore_id = ?
            ORDER BY data_documento DESC, data_inserimento DESC
        """, (cacciatore_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ========== LOG ATTIVITÀ ==========
    
    def log_attivita(self, utente: str, azione: str, tabella: str, 
                     record_id: int, dettagli: str = None):
        """Registra un'attività nel log"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO log_attivita (utente, azione, tabella, record_id, dettagli)
                VALUES (?, ?, ?, ?, ?)
            """, (utente, azione, tabella, record_id, dettagli))
            
            conn.commit()
        except Exception as e:
            # Log silenzioso - non bloccare operazioni principali
            pass
        finally:
            if conn:
                conn.close()
    
    def get_log_attivita(self, limit: int = 100) -> List[Dict]:
        """Recupera il log delle attività recenti"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM log_attivita
            ORDER BY data_ora DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ========== STATISTICHE ==========
    
    def get_statistiche_generali(self) -> Dict:
        """Recupera statistiche generali del sistema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Cacciatori attivi
        cursor.execute("SELECT COUNT(*) as count FROM cacciatori WHERE attivo = 1")
        stats['cacciatori_attivi'] = cursor.fetchone()['count']
        
        # Libretti anno corrente
        anno_corrente = dt.datetime.now().year
        cursor.execute("SELECT COUNT(*) as count FROM libretti_regionali WHERE anno = ?", (anno_corrente,))
        stats['libretti_anno_corrente'] = cursor.fetchone()['count']
        
        # Fogli caccia anno corrente
        cursor.execute("SELECT COUNT(*) as count FROM fogli_caccia WHERE anno = ?", (anno_corrente,))
        stats['fogli_anno_corrente'] = cursor.fetchone()['count']
        
        # Autorizzazioni in attesa
        cursor.execute("SELECT COUNT(*) as count FROM autorizzazioni_ras WHERE stato = 'IN_ATTESA'")
        stats['autorizzazioni_in_attesa'] = cursor.fetchone()['count']
        
        conn.close()
        return stats
