#!/usr/bin/env python3
"""
Test the updated scraper with UK National Lottery integration.
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from scraper import EuromillionsScraper
from config import get_settings

def test_uk_scraper():
    """Test the UK National Lottery scraper integration."""
    
    print("🧪 Testing UK National Lottery Scraper Integration")
    print("=" * 60)
    
    # Initialize scraper
    scraper = EuromillionsScraper()
    
    # Test 1: UK-specific scraping method
    print("\n1️⃣ Testing UK-specific scraping method...")
    try:
        uk_draws = scraper.scrape_uk_national_lottery(limit=5)
        
        print(f"✅ Successfully scraped {len(uk_draws)} draws from UK National Lottery")
        
        if uk_draws:
            print("\n📊 Sample draws:")
            for i, draw in enumerate(uk_draws[:3], 1):
                main_str = "-".join(f"{n:02d}" for n in draw['main_numbers'])
                star_str = "-".join(f"{s:02d}" for s in draw['star_numbers'])
                print(f"   {i}. {draw['draw_date'].strftime('%Y-%m-%d')}: [{main_str}] + [{star_str}]")
                print(f"      ID: {draw['draw_id']}, Source: {draw.get('source', 'N/A')}")
        
    except Exception as e:
        print(f"❌ UK scraping failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Generic scraping method (should now use UK as primary)
    print(f"\n2️⃣ Testing generic scraping method (should use UK as primary)...")
    try:
        generic_draws = scraper.scrape_latest(limit=3)
        
        print(f"✅ Successfully scraped {len(generic_draws)} draws via generic method")
        
        if generic_draws:
            print("\n📊 Sample draws from generic method:")
            for i, draw in enumerate(generic_draws, 1):
                main_str = "-".join(f"{n:02d}" for n in draw['main_numbers'])
                star_str = "-".join(f"{s:02d}" for s in draw['star_numbers'])
                print(f"   {i}. {draw['draw_date'].strftime('%Y-%m-%d')}: [{main_str}] + [{star_str}]")
                print(f"      ID: {draw['draw_id']}, Source: {draw.get('source', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Generic scraping failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Validation checks
    print(f"\n3️⃣ Testing data validation...")
    
    test_draws = uk_draws if 'uk_draws' in locals() and uk_draws else (
        generic_draws if 'generic_draws' in locals() and generic_draws else []
    )
    
    if test_draws:
        validation_passed = True
        
        for draw in test_draws[:2]:  # Test first 2 draws
            # Check main numbers
            main_nums = draw['main_numbers']
            if len(main_nums) != 5:
                print(f"   ❌ Invalid main numbers count: {len(main_nums)}")
                validation_passed = False
            elif not all(1 <= n <= 50 for n in main_nums):
                print(f"   ❌ Main numbers out of range: {main_nums}")
                validation_passed = False
            elif main_nums != sorted(main_nums):
                print(f"   ❌ Main numbers not sorted: {main_nums}")
                validation_passed = False
            
            # Check star numbers
            star_nums = draw['star_numbers']
            if len(star_nums) != 2:
                print(f"   ❌ Invalid star numbers count: {len(star_nums)}")
                validation_passed = False
            elif not all(1 <= s <= 12 for s in star_nums):
                print(f"   ❌ Star numbers out of range: {star_nums}")
                validation_passed = False
            elif star_nums != sorted(star_nums):
                print(f"   ❌ Star numbers not sorted: {star_nums}")
                validation_passed = False
            
            # Check individual number fields match arrays
            if (draw['n1'] != main_nums[0] or draw['n2'] != main_nums[1] or 
                draw['n3'] != main_nums[2] or draw['n4'] != main_nums[3] or 
                draw['n5'] != main_nums[4]):
                print(f"   ❌ Individual main number fields don't match array")
                validation_passed = False
            
            if draw['s1'] != star_nums[0] or draw['s2'] != star_nums[1]:
                print(f"   ❌ Individual star number fields don't match array")
                validation_passed = False
        
        if validation_passed:
            print("   ✅ All validation checks passed!")
        
    else:
        print("   ⚠️  No draws to validate")
    
    # Test 4: URL configuration check
    print(f"\n4️⃣ Testing URL configuration...")
    print(f"   UK URLs: {scraper.uk_urls}")
    print(f"   Base URLs: {scraper.base_urls}")
    
    print(f"\n🎉 UK National Lottery integration test complete!")

if __name__ == "__main__":
    test_uk_scraper()
