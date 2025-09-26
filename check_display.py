#!/usr/bin/env python3
"""
Check Display Format
===================
Check how tickets are formatted and displayed.
"""

from streamlit_adapters import suggest_tickets_ui

print("=== CHECKING DISPLAY FORMAT ===")
print()

tickets = suggest_tickets_ui(n=1, method='random')
if tickets:
    ticket = tickets[0]
    
    print("Raw ticket data:")
    print(f"  balls: {ticket['balls']}")
    print(f"  stars: {ticket['stars']}")
    print(f"  balls_str: {ticket['balls_str']}")
    print(f"  stars_str: {ticket['stars_str']}")
    print()
    
    print("How it appears in UI:")
    print(f"  Main: {ticket['balls_str']}")
    print(f"  Stars: {ticket['stars_str']}")
    print()
    
    print("Full display line (as shown in Streamlit):")
    balls_str = ticket['balls_str'] 
    stars_str = ticket['stars_str']
    print(f"**1.** {balls_str} | ⭐ {stars_str}")
    print()
    
    # Check if maybe there's some formatting issue
    all_numbers = ticket['balls'] + ticket['stars']
    print(f"All numbers together: {all_numbers} (total: {len(all_numbers)})")
    print(f"Expected format: 5 main + 2 stars = 7 total")
    
    # Let's also check the individual counts
    print()
    print("Detailed breakdown:")
    print(f"  Main balls count: {len(ticket['balls'])}")
    print(f"  Stars count: {len(ticket['stars'])}")
    print(f"  Main balls range: {min(ticket['balls'])}-{max(ticket['balls'])}")
    print(f"  Stars range: {min(ticket['stars'])}-{max(ticket['stars'])}")
else:
    print("No tickets generated")