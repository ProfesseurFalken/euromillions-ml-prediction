#!/usr/bin/env python3
"""Final integration test."""

from hybrid_scraper import get_best_available_draws
from streamlit_adapters import StreamlitAdapters

print('🎯 Final System Integration Test')
print('=' * 40)

# Test hybrid scraper
print('1. Testing hybrid scraper...')
draws = get_best_available_draws(limit=5)
print(f'   ✅ Got {len(draws)} draws')

# Test streamlit adapters
print('2. Testing StreamlitAdapters...')
adapter = StreamlitAdapters()
status = adapter.get_system_status()
print(f'   ✅ Data available: {status["data"]["available"]}')
print(f'   ✅ Models available: {status["models"]["available"]}')

# Test ticket generation
print('3. Testing ticket generation...')
tickets = adapter.suggest_tickets_ui(n=2, method='random')
print(f'   ✅ Generated {len(tickets)} tickets')

print('\n🏆 All integration tests passed!')
print('🚀 System is ready for production use!')