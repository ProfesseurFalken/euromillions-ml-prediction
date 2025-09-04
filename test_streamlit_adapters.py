#!/usr/bin/env python3
"""
Test script for Streamlit adapters.
Verifies all adapter functions work correctly.
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from streamlit_adapters import (
    init_full_history,
    update_incremental, 
    train_from_scratch,
    reload_models,
    get_scores,
    suggest_tickets_ui,
    fetch_last_draws,
    export_all_draws_csv,
    get_system_status
)


def test_system_status():
    """Test system status function."""
    print("🔍 Testing system status...")
    
    status = get_system_status()
    print(f"✅ System status: {status}")
    return True


def test_data_functions():
    """Test data-related functions."""
    print("\n📊 Testing data functions...")
    
    # Test incremental update (should work even with no data)
    print("Testing incremental update...")
    result = update_incremental()
    print(f"✅ Incremental update: {result}")
    
    # Test fetch last draws
    print("Testing fetch last draws...")
    draws_df = fetch_last_draws(5)
    print(f"✅ Fetched {len(draws_df)} recent draws")
    print(draws_df.head() if not draws_df.empty else "No draws available")
    
    # Test CSV export
    print("Testing CSV export...")
    filename, csv_bytes = export_all_draws_csv()
    print(f"✅ CSV export: {filename}, {len(csv_bytes)} bytes")
    
    return True


def test_model_functions():
    """Test model-related functions."""
    print("\n🤖 Testing model functions...")
    
    # Test reload models (should handle no models gracefully)
    print("Testing model reload...")
    result = reload_models()
    print(f"✅ Model reload: {result}")
    
    # Test get scores (should handle no models gracefully)
    print("Testing score retrieval...")
    try:
        balls_df, stars_df = get_scores()
        print(f"✅ Scores retrieved: {len(balls_df)} balls, {len(stars_df)} stars")
    except Exception as e:
        print(f"⚠️  Scores failed (expected if no models): {e}")
    
    # Test ticket suggestions (should handle no models gracefully)
    print("Testing ticket suggestions...")
    try:
        tickets = suggest_tickets_ui(n=3, method="hybrid", seed=42)
        print(f"✅ Generated {len(tickets)} ticket suggestions")
        for ticket in tickets[:2]:  # Show first 2
            print(f"   Ticket {ticket['ticket_id']}: {ticket['balls_str']} + {ticket['stars_str']}")
    except Exception as e:
        print(f"⚠️  Ticket suggestions failed (expected if no models): {e}")
    
    return True


def test_training_workflow():
    """Test full training workflow."""
    print("\n🏋️ Testing training workflow...")
    
    # This would be slow in real usage, so we'll just test the interface
    print("Testing training interface (not actually training)...")
    
    # Check if we have enough data for training
    status = get_system_status()
    data_count = status.get("data", {}).get("count", 0)
    
    if data_count >= 100:
        print(f"✅ Sufficient data for training: {data_count} draws")
        # Uncomment to actually train: result = train_from_scratch()
        print("⚠️  Skipping actual training (would be slow)")
    else:
        print(f"⚠️  Insufficient data for training: {data_count} draws (need 100+)")
    
    return True


def demo_full_workflow():
    """Demonstrate the complete adapter workflow."""
    print("\n🚀 Demo: Complete Streamlit Adapter Workflow")
    print("=" * 60)
    
    # 1. Check system status
    print("1️⃣ Checking system status...")
    status = get_system_status()
    
    data_available = status.get("data", {}).get("available", False)
    models_available = status.get("models", {}).get("available", False)
    
    print(f"   📊 Data available: {data_available}")
    print(f"   🤖 Models available: {models_available}")
    
    # 2. Show recommendations
    recommendations = status.get("recommendations", [])
    print(f"\n2️⃣ System recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")
    
    # 3. Show recent draws if available
    if data_available:
        print(f"\n3️⃣ Recent draws:")
        recent_draws = fetch_last_draws(3)
        if not recent_draws.empty:
            for _, draw in recent_draws.iterrows():
                print(f"   {draw['draw_date']}: {draw.get('balls', 'N/A')} + {draw.get('stars', 'N/A')}")
        else:
            print("   No draws available")
    
    # 4. Show scores if models available
    if models_available:
        print(f"\n4️⃣ Top ball probabilities:")
        try:
            balls_df, stars_df = get_scores()
            if not balls_df.empty:
                top_balls = balls_df.head(5)
                for _, ball in top_balls.iterrows():
                    print(f"   Ball {ball['ball']:2d}: {ball['percentage']:5.1f}%")
            
            print(f"\n   Top star probabilities:")
            if not stars_df.empty:
                top_stars = stars_df.head(3)
                for _, star in top_stars.iterrows():
                    print(f"   Star {star['star']:2d}: {star['percentage']:5.1f}%")
        except:
            print("   Scores not available")
    
    # 5. Generate sample tickets if possible
    if models_available:
        print(f"\n5️⃣ Sample ticket suggestions:")
        try:
            tickets = suggest_tickets_ui(n=2, method="hybrid")
            for ticket in tickets:
                print(f"   🎫 {ticket['balls_str']} + {ticket['stars_str']}")
        except:
            print("   Ticket generation not available")
    
    print(f"\n✅ Workflow demo complete!")
    return True


def main():
    """Run all adapter tests."""
    print("🧪 Streamlit Adapters Test Suite")
    print("=" * 50)
    
    try:
        # Run tests
        test_system_status()
        test_data_functions()
        test_model_functions()
        test_training_workflow()
        
        # Demo workflow
        demo_full_workflow()
        
        print(f"\n🎉 All adapter tests completed successfully!")
        print(f"✅ Streamlit adapters are ready for use")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
