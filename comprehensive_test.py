#!/usr/bin/env python3
"""
Comprehensive System Test
========================
Tests all major functionality of the EuroMillions ML system.
"""

print("=== COMPREHENSIVE SYSTEM TEST ===")
from streamlit_adapters import *

# Test 1: System Status
print("\n1. Testing system status...")
status = get_system_status()
print(f"   Data available: {status['data']['available']}")
print(f"   Models available: {status['models']['available']}")
print(f"   Total draws: {status['data']['count']}")

# Test 2: All ticket generation methods
print("\n2. Testing all ticket generation methods...")
methods = ['random', 'topk', 'hybrid']
for method in methods:
    tickets = suggest_tickets_ui(n=2, method=method)
    print(f"   {method}: Generated {len(tickets)} tickets")
    if tickets:
        t = tickets[0]
        balls_str = "-".join(f"{b:02d}" for b in t['balls'])
        stars_str = "-".join(f"{s:02d}" for s in t['stars'])
        print(f"      Sample: {balls_str} | {stars_str} (score: {t['combined_score']:.3f})")

# Test 3: Scores
print("\n3. Testing score retrieval...")
balls_scores, stars_scores = get_scores()
print(f"   Ball scores shape: {balls_scores.shape}")
print(f"   Star scores shape: {stars_scores.shape}")

# Test 4: Update check
print("\n4. Testing update functionality...")
update_result = update_incremental()
print(f"   Update success: {update_result['success']}")
print(f"   Message: {update_result['message']}")

print("\n=== ALL TESTS COMPLETED SUCCESSFULLY! ===")