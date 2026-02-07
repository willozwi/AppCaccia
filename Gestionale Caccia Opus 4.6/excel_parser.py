"""
Modulo per parsing e validazione dati da file Excel
Estrae dati anagrafici strutturati dai fogli caccia
Supporta:
- Fogli con colonne strutturate (Cognome, Nome, CF, ecc.)
- Template RAS (dati in testo libero)
"""

import openpyxl
import re
import datetime as dt
from typing import Dict, List, Optional, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExcelParser:
    """Parser per file Excel fogli caccia con estrazione dati strutturati"""
    
    # Mappatura intestazioni possibili (case-insensitive)
    HEADER_MAPPING = {
        'cognome': ['cognome', 'surname', 'last name'],
        'nome': ['nome', 'name', 'first name', 'firstname'],
        'codice_fiscale': ['codice fiscale', 'cf', 'cod. fiscale', 'codice_fiscale', 'tax code'],
        'data_nascita': ['data nascita', 'data di nascita', 'nascita', 'birth date', 'data_nascita'],
        'comune_residenza': ['comune', 'residenza', 'comune residenza', 'città', 'comune_residenza'],
        'numero_licenza': ['numero licenza', 'licenza', 'tesserino', 'numero', 'n. licenza'],
        'anno': ['anno', 'year', 'stagione'],
    }
    
    # Pattern per riconoscere template RAS
    RAS_KEYWORDS = [
        'regione autonoma della sardegna',
        'foglio venatorio',
        'in possesso del porto d\'arma',
        'assessorato',
    ]
    
    # Pattern per estrarre nome e cognome dal testo RAS
    RAS_NAME_PATTERNS = [
        # Pattern principale: "COGNOME NOME in possesso del porto"
        r"([A-ZÀ-Ÿ''\-]+)\s+([A-ZÀ-Ÿ''\-]+(?:\s+[A-ZÀ-Ÿ''\-]+)?)\s+in\s+possesso\s+del\s+porto",
        # Pattern alternativo: "Il sottoscritto COGNOME NOME"
        r"sottoscritto\s+([A-ZÀ-Ÿ''\-]+)\s+([A-ZÀ-Ÿ''\-]+)",
        # Pattern generico: due parole maiuscole consecutive
        r"\b([A-ZÀ-Ÿ''\-]{2,})\s+([A-ZÀ-Ÿ''\-]{2,})\b",
    ]
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.parse_source = None  # 'structured', 'ras_template', 'filename'
    
    def parse_excel_file(self, file_path: str, file_name: str = None) -> Optional[Dict]:
        """
        Legge file Excel e estrae dati strutturati
        
        Args:
            file_path: Percorso completo del file Excel
            file_name: Nome del file (per fallback parsing)
            
        Returns:
            Dict con dati estratti o None se errori critici
        """
        self.errors = []
        self.warnings = []
        self.parse_source = None
        
        if not file_name:
            file_name = file_path.split('/')[-1].split('\\')[-1]
        
        logger.info(f"[PARSE] Inizio parsing file: {file_name}")
        
        try:
            # Apri workbook
            wb = openpyxl.load_workbook(file_path, data_only=True)
            sheet = wb.active
            
            # === STEP 1: RICONOSCI TEMPLATE ===
            is_ras = self._is_ras_template(sheet)
            
            if is_ras:
                logger.info(f"[PARSE] Template RAS riconosciuto: {file_name}")
                dati = self._parse_ras_template(sheet, file_name)
            else:
                logger.info(f"[PARSE] Template strutturato: {file_name}")
                dati = self._parse_structured_template(sheet)
            
            # === STEP 2: FALLBACK SU FILENAME ===
            if not dati or not dati.get('cognome') or not dati.get('nome'):
                logger.warning(f"[PARSE] Parsing contenuto fallito, fallback su filename: {file_name}")
                dati_filename = self._parse_from_filename(file_name)
                
                if dati_filename:
                    # Merge con dati esistenti (filename vince su campi vuoti)
                    if not dati:
                        dati = {}
                    
                    if not dati.get('cognome'):
                        dati['cognome'] = dati_filename.get('cognome')
                    if not dati.get('nome'):
                        dati['nome'] = dati_filename.get('nome')
                    if not dati.get('stato'):
                        dati['stato'] = dati_filename.get('stato')
                    
                    self.parse_source = 'filename'
                    logger.info(f"[PARSE] Dati estratti da filename: cognome={dati.get('cognome')}, nome={dati.get('nome')}")
            
            wb.close()
            
            # === STEP 3: VALIDAZIONE FINALE ===
            if not dati or not dati.get('cognome') or not dati.get('nome'):
                self.errors.append("Impossibile estrarre Cognome e Nome dal file")
                logger.error(f"[PARSE] FALLITO per {file_name}: Cognome/Nome non estratti")
                return None
            
            # Aggiungi metadata
            dati['file_path'] = file_path
            dati['file_name'] = file_name
            dati['import_date'] = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            dati['parse_source'] = self.parse_source
            
            logger.info(f"[PARSE] SUCCESS: {file_name} | source={self.parse_source} | cognome={dati.get('cognome')} | nome={dati.get('nome')}")
            
            return dati
            
        except Exception as e:
            self.errors.append(f"Errore lettura file: {str(e)}")
            logger.error(f"[PARSE] Errore parsing {file_name}: {e}")
            return None
    
    def _is_ras_template(self, sheet) -> bool:
        """
        Determina se il foglio Excel è un template RAS
        Cerca keywords tipiche nelle prime 20 righe
        """
        for row_idx in range(1, 21):
            for cell in sheet[row_idx]:
                if cell.value and isinstance(cell.value, str):
                    value_lower = cell.value.lower()
                    for keyword in self.RAS_KEYWORDS:
                        if keyword in value_lower:
                            return True
        return False
    
    def _parse_ras_template(self, sheet, file_name: str) -> Optional[Dict]:
        """
        Estrae dati da template RAS (testo libero)
        Cerca in celle A1-A60 il pattern "COGNOME NOME in possesso del porto"
        """
        self.parse_source = 'ras_template'
        dati = {}
        
        # Cerca nelle celle A1-A60 (colonna A, prime 60 righe)
        for row_idx in range(1, 61):
            cell = sheet[f'A{row_idx}']
            
            if not cell.value:
                continue
            
            text = str(cell.value)
            
            # Prova ogni pattern
            for pattern in self.RAS_NAME_PATTERNS:
                match = re.search(pattern, text, re.IGNORECASE)
                
                if match:
                    cognome = match.group(1).strip().upper()
                    nome = match.group(2).strip().title()
                    
                    # Validazione minima
                    if len(cognome) >= 2 and len(nome) >= 2:
                        dati['cognome'] = cognome
                        dati['nome'] = nome
                        logger.info(f"[PARSE] RAS match at A{row_idx}: cognome={cognome}, nome={nome}")
                        break
            
            if dati.get('cognome'):
                break
        
        # Se non trovato, warning
        if not dati.get('cognome'):
            self.warnings.append("Template RAS riconosciuto ma nome/cognome non estratti dal testo")
            logger.warning(f"[PARSE] RAS template ma pattern non matchato in {file_name}")
        
        return dati if dati else None
    
    def _parse_structured_template(self, sheet) -> Optional[Dict]:
        """Parsing originale per template strutturati con colonne"""
        self.parse_source = 'structured'
        
        # Trova riga intestazioni
        header_row = self._find_header_row(sheet)
        
        if not header_row:
            self.warnings.append("Intestazioni colonne non trovate")
            return None
        
        # Mappa colonne
        column_map = self._map_columns(sheet, header_row)
        
        # Estrai dati (prima riga dati dopo intestazioni)
        data_row = header_row + 1
        dati = self._extract_data(sheet, data_row, column_map)
        
        return dati
    
    def _parse_from_filename(self, file_name: str) -> Optional[Dict]:
        """
        Estrae Cognome, Nome e Stato dal nome file
        
        Supporta formati:
        - Cognome Nome(Stato).xlsx
        - Cognome Nome (Stato).xlsx
        - Cognome_Nome_Stato.xlsx
        - Cognome Nome.xlsx
        """
        dati = {}
        
        # Rimuovi estensione
        name_no_ext = re.sub(r'\.(xlsx|xls)$', '', file_name, flags=re.IGNORECASE)
        
        # Pattern 1: "Cognome Nome(Stato)" o "Cognome Nome (Stato)"
        pattern1 = r"^(.+?)\s*\(([^)]+)\)$"
        match = re.match(pattern1, name_no_ext)
        
        if match:
            nome_completo = match.group(1).strip()
            stato_raw = match.group(2).strip()
            
            # Separa cognome e nome
            parti = nome_completo.split()
            if len(parti) >= 2:
                dati['cognome'] = parti[0].upper()
                dati['nome'] = ' '.join(parti[1:]).title()
            
            # Mappa stato
            dati['stato'] = self._map_stato(stato_raw)
            
            logger.info(f"[PARSE] Filename pattern1: cognome={dati.get('cognome')}, nome={dati.get('nome')}, stato={dati.get('stato')}")
            return dati
        
        # Pattern 2: "Cognome_Nome_Stato"
        pattern2 = r"^([A-Za-zÀ-ÿ''\-]+)_([A-Za-zÀ-ÿ''\-]+)_(.+)$"
        match = re.match(pattern2, name_no_ext)
        
        if match:
            dati['cognome'] = match.group(1).strip().upper()
            dati['nome'] = match.group(2).strip().title()
            dati['stato'] = self._map_stato(match.group(3))
            
            logger.info(f"[PARSE] Filename pattern2: cognome={dati.get('cognome')}, nome={dati.get('nome')}")
            return dati
        
        # Pattern 3: "Cognome Nome" (senza stato)
        pattern3 = r"^([A-Za-zÀ-ÿ''\-]+)\s+([A-Za-zÀ-ÿ''\-]+(?:\s+[A-Za-zÀ-ÿ''\-]+)?)$"
        match = re.match(pattern3, name_no_ext)
        
        if match:
            dati['cognome'] = match.group(1).strip().upper()
            dati['nome'] = match.group(2).strip().title()
            dati['stato'] = 'RILASCIATO'  # Default
            
            logger.info(f"[PARSE] Filename pattern3: cognome={dati.get('cognome')}, nome={dati.get('nome')}")
            return dati
        
        logger.warning(f"[PARSE] Nessun pattern filename matchato: {file_name}")
        return None
    
    def _map_stato(self, stato_raw: str) -> str:
        """Mappa stato da stringa a valore standardizzato"""
        if not stato_raw:
            return 'RILASCIATO'
        
        stato_upper = stato_raw.upper()
        
        if 'CONSEGNATO' in stato_upper:
            return 'CONSEGNATO'
        elif 'STAMPATO' in stato_upper or 'STAMPATA' in stato_upper:
            return 'STAMPATO'
        elif 'RINNOVARE' in stato_upper:
            return 'DA_RINNOVARE'
        else:
            return 'RILASCIATO'
    
    def _find_header_row(self, sheet) -> Optional[int]:
        """
        Trova la riga con le intestazioni delle colonne
        Cerca nelle prime 20 righe
        """
        for row_idx in range(1, 21):
            row_values = [str(cell.value).lower().strip() 
                         if cell.value else '' 
                         for cell in sheet[row_idx]]
            
            # Cerca almeno 2 intestazioni chiave
            found = 0
            for key in ['cognome', 'nome', 'codice_fiscale']:
                for possible_header in self.HEADER_MAPPING[key]:
                    if any(possible_header in val for val in row_values):
                        found += 1
                        break
            
            if found >= 2:
                return row_idx
        
        return None
    
    def _map_columns(self, sheet, header_row: int) -> Dict[str, int]:
        """Mappa le intestazioni alle colonne"""
        column_map = {}
        
        headers = []
        for col_idx, cell in enumerate(sheet[header_row], start=1):
            header_val = str(cell.value).lower().strip() if cell.value else ''
            headers.append((col_idx, header_val))
        
        for field, possible_headers in self.HEADER_MAPPING.items():
            for col_idx, header in headers:
                for possible in possible_headers:
                    if possible in header:
                        column_map[field] = col_idx
                        break
                if field in column_map:
                    break
        
        return column_map
    
    def _extract_data(self, sheet, row: int, column_map: Dict[str, int]) -> Dict:
        """Estrae dati dalla riga specificata"""
        dati = {}
        
        for field, col_idx in column_map.items():
            cell = sheet.cell(row=row, column=col_idx)
            value = cell.value
            
            if field == 'data_nascita':
                value = self._parse_date(value)
            
            if isinstance(value, str):
                value = value.strip()
            
            dati[field] = value
        
        return dati
    
    def _parse_date(self, value) -> Optional[str]:
        """Converte date Excel in formato standard YYYY-MM-DD"""
        if value is None:
            return None
        
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d')
        
        if isinstance(value, str):
            formats = [
                '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d',
                '%d/%m/%y', '%d-%m-%y',
            ]

            for fmt in formats:
                try:
                    dt_obj = dt.datetime.strptime(value.strip(), fmt)
                    return dt_obj.strftime('%Y-%m-%d')
                except ValueError:
                    continue

        if isinstance(value, (int, float)):
            try:
                dt_obj = dt.datetime(1899, 12, 30) + dt.timedelta(days=int(value))
                return dt_obj.strftime('%Y-%m-%d')
            except Exception:
                pass
        
        self.warnings.append(f"Data non riconosciuta: {value}")
        return None
    
    def _validate_data(self, dati: Dict) -> bool:
        """Valida dati estratti - SOLO cognome/nome obbligatori per ora"""
        if not dati.get('cognome'):
            self.errors.append("Cognome mancante")
            return False
        
        if not dati.get('nome'):
            self.errors.append("Nome mancante")
            return False
        
        return True
    
    def get_errors(self) -> List[str]:
        """Ritorna lista errori"""
        return self.errors
    
    def get_warnings(self) -> List[str]:
        """Ritorna lista warning"""
        return self.warnings
