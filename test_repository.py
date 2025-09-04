"""
Test script for the Euromillions repository.
Demonstrates database operations and data management.
"""
from repository import get_repository, init_database
from datetime import datetime
import json

def test_repository():
    """Test the repository functionality."""
    print("🧪 Testing Euromillions Repository...")
    
    # Initialize database
    print("\n1. Initializing database...")
    init_database()
    
    # Get repository instance
    repo = get_repository()
    
    # Test data
    sample_draws = [
        {
            "draw_id": "2024-001",
            "draw_date": "2024-01-05",
            "n1": 7, "n2": 15, "n3": 23, "n4": 31, "n5": 45,
            "s1": 3, "s2": 8,
            "jackpot": 25000000.0,
            "prize_table": {
                "5+2": {"winners": 0, "prize": 25000000},
                "5+1": {"winners": 3, "prize": 125000},
                "5+0": {"winners": 5, "prize": 25000}
            },
            "raw_html": "<html>Sample draw data</html>"
        },
        {
            "draw_id": "2024-002", 
            "draw_date": "2024-01-09",
            "n1": 12, "n2": 18, "n3": 27, "n4": 35, "n5": 42,
            "s1": 1, "s2": 9,
            "jackpot": 30000000.0,
            "prize_table": {
                "5+2": {"winners": 1, "prize": 30000000},
                "5+1": {"winners": 2, "prize": 150000},
                "5+0": {"winners": 8, "prize": 30000}
            }
        }
    ]
    
    # Test upsert
    print("\n2. Inserting sample draws...")
    result = repo.upsert_draws(sample_draws)
    print(f"   📊 Insert result: {result}")
    
    # Test latest draw date
    print("\n3. Getting latest draw date...")
    latest_date = repo.latest_draw_date()
    print(f"   📅 Latest draw: {latest_date}")
    
    # Test get specific draw
    print("\n4. Getting specific draw...")
    draw = repo.get_draw_by_id("2024-001")
    if draw:
        print(f"   🎱 Draw 2024-001: Numbers {draw['n1']}-{draw['n2']}-{draw['n3']}-{draw['n4']}-{draw['n5']}, Stars {draw['s1']}-{draw['s2']}")
        print(f"   💰 Jackpot: €{draw['jackpot']:,.0f}")
    
    # Test all draws DataFrame
    print("\n5. Getting all draws as DataFrame...")
    df = repo.all_draws_df()
    print(f"   📈 Total draws in DataFrame: {len(df)}")
    if not df.empty:
        print(f"   📊 Columns: {list(df.columns)}")
        print(f"   📅 Date range: {df['draw_date'].min()} to {df['draw_date'].max()}")
    
    # Test update existing draw
    print("\n6. Testing update of existing draw...")
    updated_draw = sample_draws[0].copy()
    updated_draw["jackpot"] = 26000000.0  # Update jackpot
    result = repo.upsert_draws([updated_draw])
    print(f"   🔄 Update result: {result}")
    
    # Get database stats
    print("\n7. Database statistics...")
    stats = repo.get_stats()
    for key, value in stats.items():
        print(f"   📊 {key}: {value}")
    
    print("\n✅ Repository test completed successfully!")

if __name__ == "__main__":
    test_repository()
