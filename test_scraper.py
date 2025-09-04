"""
Test script for the EuromillionsScraper.
Demonstrates scraping functionality with error handling.
"""
from scraper import get_scraper
from repository import get_repository, init_database
import json

def test_scraper():
    """Test the scraper functionality."""
    print("🕷️ Testing Euromillions Scraper...")
    
    # Get scraper instance
    scraper = get_scraper()
    
    # Test URL discovery
    print("\n1. Testing URL discovery...")
    try:
        urls = scraper.list_recent_draw_urls(limit=5)
        print(f"   📋 Found {len(urls)} draw URLs:")
        for i, url in enumerate(urls[:3], 1):
            print(f"   {i}. {url}")
        if len(urls) > 3:
            print(f"   ... and {len(urls) - 3} more")
    except Exception as e:
        print(f"   ❌ URL discovery failed: {e}")
        return
    
    # Test single draw parsing
    if urls:
        print(f"\n2. Testing draw parsing...")
        try:
            test_url = urls[0]
            print(f"   🎯 Parsing: {test_url}")
            
            draw_data = scraper.parse_draw(test_url)
            
            print(f"   📅 Draw ID: {draw_data['draw_id']}")
            print(f"   📅 Date: {draw_data['draw_date']}")
            print(f"   🎱 Numbers: {draw_data['n1']}-{draw_data['n2']}-{draw_data['n3']}-{draw_data['n4']}-{draw_data['n5']}")
            print(f"   ⭐ Stars: {draw_data['s1']}-{draw_data['s2']}")
            print(f"   💰 Jackpot: €{draw_data['jackpot']:,.0f}" if draw_data['jackpot'] else "   💰 Jackpot: Not found")
            print(f"   🏆 Prize categories: {len(draw_data['prize_table_json'])}")
            print(f"   📄 Raw HTML length: {len(draw_data['raw_html'])} chars")
            
        except Exception as e:
            print(f"   ❌ Draw parsing failed: {e}")
            return
    
    # Test batch scraping
    print(f"\n3. Testing batch scraping...")
    try:
        draws = scraper.scrape_latest(limit=3)
        print(f"   📊 Scraped {len(draws)} draws")
        
        for draw in draws:
            print(f"   📅 {draw['draw_id']}: {draw['n1']}-{draw['n2']}-{draw['n3']}-{draw['n4']}-{draw['n5']} + {draw['s1']}-{draw['s2']}")
        
    except Exception as e:
        print(f"   ❌ Batch scraping failed: {e}")
        return
    
    # Test integration with repository
    print(f"\n4. Testing repository integration...")
    try:
        # Initialize database
        init_database()
        repo = get_repository()
        
        # Insert scraped data
        result = repo.upsert_draws(draws)
        print(f"   💾 Database result: {result}")
        
        # Verify data
        df = repo.all_draws_df()
        print(f"   📈 Total draws in database: {len(df)}")
        
        if not df.empty:
            latest = repo.latest_draw_date()
            print(f"   📅 Latest draw in DB: {latest}")
        
    except Exception as e:
        print(f"   ❌ Repository integration failed: {e}")
        return
    
    print("\n✅ Scraper test completed successfully!")
    print("\n💡 Usage examples:")
    print("   from scraper import get_scraper")
    print("   scraper = get_scraper()")
    print("   draws = scraper.scrape_latest(limit=10)")
    print("   # Then save to database with repository.upsert_draws(draws)")

def test_validation():
    """Test the validation functions."""
    print("\n🧪 Testing validation...")
    
    scraper = get_scraper()
    
    # Test valid data
    valid_numbers = {"main": [1, 15, 23, 35, 50], "stars": [3, 12]}
    try:
        scraper._validate_draw_data(valid_numbers, "test-2024-01-01")
        print("   ✅ Valid data passed validation")
    except ValueError as e:
        print(f"   ❌ Valid data failed: {e}")
    
    # Test invalid main numbers
    invalid_main = {"main": [0, 15, 23, 35, 51], "stars": [3, 12]}
    try:
        scraper._validate_draw_data(invalid_main, "test-2024-01-01")
        print("   ❌ Invalid main numbers should have failed")
    except ValueError:
        print("   ✅ Invalid main numbers correctly rejected")
    
    # Test invalid star numbers
    invalid_stars = {"main": [1, 15, 23, 35, 50], "stars": [0, 13]}
    try:
        scraper._validate_draw_data(invalid_stars, "test-2024-01-01")
        print("   ❌ Invalid star numbers should have failed")
    except ValueError:
        print("   ✅ Invalid star numbers correctly rejected")

if __name__ == "__main__":
    test_scraper()
    test_validation()
