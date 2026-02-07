"""
Costanti centralizzate per il gestionale caccia
Versione: 1.1
"""

class StatoFoglio:
    """Stati fogli caccia standardizzati"""
    DISPONIBILE = 'DISPONIBILE'
    CONSEGNATO = 'CONSEGNATO'
    RILASCIATO = 'RILASCIATO'
    RESTITUITO = 'RESTITUITO'
    
    # Mapping stati legacy per retrocompatibilità
    LEGACY_MAPPING = {
        'Consegnato': 'CONSEGNATO',
        'Stampato': 'RILASCIATO',
        'Da rinnovare': 'DISPONIBILE',
    }
    
    @classmethod
    def all(cls):
        """Ritorna tutti gli stati validi"""
        return [
            cls.DISPONIBILE,
            cls.CONSEGNATO,
            cls.RILASCIATO,
            cls.RESTITUITO
        ]
    
    @classmethod
    def display_names(cls):
        """Nomi visualizzati nell'interfaccia"""
        return {
            cls.DISPONIBILE: 'Disponibile',
            cls.CONSEGNATO: 'Consegnato',
            cls.RILASCIATO: 'Rilasciato',
            cls.RESTITUITO: 'Restituito'
        }
    
    @classmethod
    def normalize(cls, stato: str) -> str:
        """Normalizza uno stato legacy al valore standard"""
        if not stato:
            return cls.DISPONIBILE
        
        # Se già normalizzato
        if stato.upper() in cls.all():
            return stato.upper()
        
        # Se legacy
        return cls.LEGACY_MAPPING.get(stato, stato.upper())


class StatoLibretto:
    """Stati libretti regionali"""
    ATTIVO = 'ATTIVO'
    SCADUTO = 'SCADUTO'
    SOSPESO = 'SOSPESO'
    REVOCATO = 'REVOCATO'
    
    @classmethod
    def all(cls):
        return [cls.ATTIVO, cls.SCADUTO, cls.SOSPESO, cls.REVOCATO]
    
    @classmethod
    def display_names(cls):
        return {
            cls.ATTIVO: 'Attivo',
            cls.SCADUTO: 'Scaduto',
            cls.SOSPESO: 'Sospeso',
            cls.REVOCATO: 'Revocato'
        }


class StatoAutorizzazione:
    """Stati autorizzazioni RAS"""
    IN_ATTESA = 'IN_ATTESA'
    APPROVATA = 'APPROVATA'
    RIFIUTATA = 'RIFIUTATA'
    SCADUTA = 'SCADUTA'
    
    @classmethod
    def all(cls):
        return [cls.IN_ATTESA, cls.APPROVATA, cls.RIFIUTATA, cls.SCADUTA]
    
    @classmethod
    def display_names(cls):
        return {
            cls.IN_ATTESA: 'In Attesa',
            cls.APPROVATA: 'Approvata',
            cls.RIFIUTATA: 'Rifiutata',
            cls.SCADUTA: 'Scaduta'
        }


# Configurazioni generali
class Config:
    """Configurazioni applicazione"""
    DB_NAME = "gestionale_caccia.db"
    BACKUP_DIR = "backups"
    DOCS_DIR = "documenti"
    
    # Formati date
    DATE_FORMAT = "%Y-%m-%d"
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    DISPLAY_DATE_FORMAT = "%d/%m/%Y"
    
    # Limiti
    MAX_FILE_SIZE_MB = 50
    MAX_BATCH_SIZE = 100
    DB_TIMEOUT_SECONDS = 30.0
    
    # Versione
    VERSION = "1.1.0"
    APP_NAME = "Gestionale Caccia - Polizia Locale"
