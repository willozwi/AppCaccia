#!/usr/bin/env python3
"""
Fix Datetime Method Calls

Updates all datetime.now(), datetime.strptime(), etc calls to dt.datetime.*
in files that have already been updated to use 'import datetime as dt'.
"""

import os
import re

def fix_datetime_calls(filepath):
    """Fix datetime method calls in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace datetime method calls with dt.datetime
        # Use word boundaries to avoid replacing dt.datetime.now() again
        content = re.sub(r'(?<!dt\.)datetime\.now\(', 'dt.datetime.now(', content)
        content = re.sub(r'(?<!dt\.)datetime\.strptime\(', 'dt.datetime.strptime(', content)
        content = re.sub(r'(?<!dt\.)datetime\.today\(', 'dt.datetime.today(', content)
        content = re.sub(r'(?<!dt\.)datetime\.date\(', 'dt.datetime.date(', content)
        
        # Fix timedelta usage
        content = re.sub(r'(?<!dt\.)timedelta\(', 'dt.timedelta(', content)
        
        # Excel parser has a variable named dt, need special handling
        if 'excel_parser.py' in filepath:
            # Restore variable assignment
            content = content.replace('dt.datetime.datetime.strptime', 'dt_obj = dt.datetime.strptime')
            content = content.replace('dt = dt.datetime.strptime', 'dt_obj = dt.datetime.strptime')
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

# Files to fix
files_to_fix = [
    r'pages\report_statistiche.py',
    r'pages\libretti_regionali.py',
    r'pages\import_fogli.py',
    r'pages\documenti.py',
    r'pages\autorizzazioni_ras.py',
    r'pages\anagrafe_cacciatori.py',
    r'migrate_stati.py',
    r'database.py',
    r'smoke_test_header_parse.py',
    r'excel_parser.py'
]

print("Fixing datetime method calls...")
fixed_count = 0

for file in files_to_fix:
    filepath = os.path.join(r'c:\Users\DPIRAS\Desktop\Gestionale Caccia', file)
    if os.path.exists(filepath):
        if fix_datetime_calls(filepath):
            print(f"  [OK] {file}")
            fixed_count += 1
        else:
            print(f"  [SKIP] {file} (no changes needed)")
    else:
        print(f"  [NOT FOUND] {file}")

print(f"\nFixed {fixed_count} files")
