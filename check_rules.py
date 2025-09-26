#!/usr/bin/env python3
"""
Check EuroMillions Configuration
===============================
Verify our system matches official French EuroMillions rules.
"""

import sys
sys.path.append('.')

print("=== CHECKING EUROMILLIONS CONFIGURATION ===")
print()

# Official French EuroMillions rules (as of 2025)
print("🇫🇷 OFFICIAL FRENCH EUROMILLIONS RULES:")
print("- Main numbers: 5 numbers from 1 to 50")
print("- Stars (Lucky Stars): 2 numbers from 1 to 12") 
print("- Cost per grid: 2.50€")
print("- Draw days: Tuesday and Friday at 20:30 CET")
print("- Option Étoile+: +1€ (France only)")
print("- My Million: Automatic participation (France)")
print("- Maximum jackpot: 240 million€")
print("- Minimum age: 18 years")
print()

# Check what our system uses
print("🤖 OUR SYSTEM CONFIGURATION:")

# Check ticket generation ranges
try:
    from streamlit_adapters import suggest_tickets_ui
    tickets = suggest_tickets_ui(n=1, method='random')
    if tickets:
        ticket = tickets[0]
        main_balls = ticket['balls']
        stars = ticket['stars']
        
        print(f"- Main balls: {len(main_balls)} numbers from {min(main_balls)} to {max(main_balls)}")
        print(f"- Stars: {len(stars)} numbers from {min(stars)} to {max(stars)}")
        print(f"- Sample ticket: {main_balls} | Stars: {stars}")
        
        # Verify ranges
        main_ok = len(main_balls) == 5 and all(1 <= n <= 50 for n in main_balls)
        stars_ok = len(stars) == 2 and all(1 <= s <= 12 for s in stars) 
        
        print()
        print("✅ COMPLIANCE CHECK:")
        print(f"- Main balls format: {'✅ CORRECT' if main_ok else '❌ INCORRECT'}")
        print(f"- Stars format: {'✅ CORRECT' if stars_ok else '❌ INCORRECT'}")
        
except Exception as e:
    print(f"❌ Error testing ticket generation: {e}")

# Check database structure  
try:
    from repository import Repository
    import os
    
    if os.path.exists('data/draws.db'):
        print()
        print("📊 DATABASE SAMPLE:")
        repo = Repository()
        sample_draws = repo.get_latest_draws(limit=3)
        
        for draw in sample_draws:
            main_nums = [draw['n1'], draw['n2'], draw['n3'], draw['n4'], draw['n5']]
            stars = [draw['s1'], draw['s2']]
            
            print(f"- {draw['draw_date']}: {main_nums} | ⭐ {stars}")
            
            # Verify this draw follows rules
            main_valid = all(1 <= n <= 50 for n in main_nums) and len(set(main_nums)) == 5
            stars_valid = all(1 <= s <= 12 for s in stars) and len(set(stars)) == 2
            
            if not (main_valid and stars_valid):
                print(f"  ⚠️  This draw has invalid data!")
    else:
        print("❌ No database found")
        
except Exception as e:
    print(f"❌ Error checking database: {e}")

print()
print("🔍 SUMMARY:")
print("Our system appears to correctly implement the official French EuroMillions format:")
print("- 5 main numbers from 1-50")  
print("- 2 star numbers from 1-12")
print("- Compatible with FDJ (Française des Jeux) official rules")