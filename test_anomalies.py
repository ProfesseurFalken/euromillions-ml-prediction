#!/usr/bin/env python3
"""
Test Multiple Tickets for Anomalies
===================================
"""

from streamlit_adapters import suggest_tickets_ui

print("=== TESTING MULTIPLE TICKETS FOR ANOMALIES ===")

# Test 10 tickets with different methods
for method in ["random", "topk", "hybrid"]:
    print(f"\nTesting {method} method with 10 tickets:")
    tickets = suggest_tickets_ui(n=10, method=method)
    
    error_count = 0
    for i, ticket in enumerate(tickets, 1):
        balls_count = len(ticket["balls"])
        stars_count = len(ticket["stars"])
        
        if balls_count != 5 or stars_count != 2:
            print(f"  ❌ Ticket {i}: {balls_count} balls + {stars_count} stars (WRONG!)")
            print(f"     Balls: {ticket['balls']}")
            print(f"     Stars: {ticket['stars']}")
            error_count += 1
        elif i <= 3:  # Show first 3 as examples
            print(f"  ✅ Ticket {i}: {balls_count}+{stars_count} - {ticket['balls']} | {ticket['stars']}")
    
    if error_count == 0:
        print(f"  All 10 tickets have correct 5+2 format")
    else:
        print(f"  Found {error_count} tickets with wrong format!")