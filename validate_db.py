#!/usr/bin/env python3
"""
Database Validation Check
========================
"""
import sqlite3
import os

if os.path.exists('data/draws.db'):
    conn = sqlite3.connect('data/draws.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT draw_id, draw_date, n1, n2, n3, n4, n5, s1, s2, jackpot FROM draws ORDER BY draw_date DESC LIMIT 5')
    rows = cursor.fetchall()
    
    print('📊 RECENT DRAWS FROM DATABASE:')
    valid_count = 0
    for row in rows:
        draw_id, date, n1, n2, n3, n4, n5, s1, s2, jackpot = row
        main_nums = [n1, n2, n3, n4, n5]
        stars = [s1, s2]
        
        main_ok = all(1 <= n <= 50 for n in main_nums if n is not None)
        stars_ok = all(1 <= s <= 12 for s in stars if s is not None)
        
        status = "✅ VALID" if main_ok and stars_ok else "❌ INVALID"
        if main_ok and stars_ok:
            valid_count += 1
            
        print(f'- {date}: {main_nums} | Stars: {stars} | {status}')
    
    print(f'\nValidation Summary: {valid_count}/{len(rows)} draws are valid')
    conn.close()
else:
    print('❌ Database not found')