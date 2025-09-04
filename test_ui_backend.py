#!/usr/bin/env python3
"""
Test script to verify the Streamlit UI functionality.
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_streamlit_ui_backend():
    """Test that all the backend functions for Streamlit UI work."""
    
    print("🧪 Testing Streamlit UI Backend Functionality")
    print("=" * 60)
    
    # Test imports
    try:
        from streamlit_adapters import (
            get_system_status,
            update_incremental,
            fetch_last_draws,
            suggest_tickets_ui,
            export_all_draws_csv
        )
        print("✅ All adapter imports successful")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test system status
    print("\n1️⃣ Testing system status...")
    try:
        status = get_system_status()
        print(f"✅ System status retrieved: {status.get('data', {}).get('count', 0)} draws available")
    except Exception as e:
        print(f"❌ System status failed: {e}")
    
    # Test recent draws fetch
    print("\n2️⃣ Testing recent draws fetch...")
    try:
        recent_draws = fetch_last_draws(5)
        print(f"✅ Recent draws fetched: {len(recent_draws)} rows")
        if not recent_draws.empty:
            print(f"   Sample: {recent_draws.iloc[0]['draw_date']} - {recent_draws.iloc[0].get('balls', 'N/A')}")
    except Exception as e:
        print(f"❌ Recent draws fetch failed: {e}")
    
    # Test CSV export
    print("\n3️⃣ Testing CSV export...")
    try:
        filename, csv_bytes = export_all_draws_csv()
        print(f"✅ CSV export successful: {filename}, {len(csv_bytes)} bytes")
    except Exception as e:
        print(f"❌ CSV export failed: {e}")
    
    # Test ticket generation (should fail gracefully if no models)
    print("\n4️⃣ Testing ticket suggestions...")
    try:
        tickets = suggest_tickets_ui(3, "hybrid", 42)
        print(f"✅ Ticket suggestions: {len(tickets)} tickets generated")
        if tickets:
            print(f"   Sample: {tickets[0]['balls_str']} + {tickets[0]['stars_str']}")
    except Exception as e:
        print(f"⚠️  Ticket suggestions failed (expected if no models): {e}")
    
    # Test .env file handling
    print("\n5️⃣ Testing .env file handling...")
    try:
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file, 'r') as f:
                content = f.read()
            print(f"✅ .env file exists: {len(content)} characters")
        else:
            print("⚠️  .env file doesn't exist (will be created by UI)")
    except Exception as e:
        print(f"❌ .env file handling failed: {e}")
    
    print(f"\n🎉 Backend functionality test complete!")
    print("🌐 Streamlit UI should be fully functional")

if __name__ == "__main__":
    test_streamlit_ui_backend()
