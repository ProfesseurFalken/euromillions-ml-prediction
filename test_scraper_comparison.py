#!/usr/bin/env python3
"""
Test and Compare Scrapers
========================

Compare original scraper vs enhanced scraper performance.
"""

import time
from datetime import datetime
from typing import Dict, List, Any


def test_original_scraper():
    """Test the original scraper."""
    print("🔄 Testing Original Scraper")
    print("-" * 40)
    
    try:
        from scraper import get_scraper
        
        start_time = time.time()
        scraper = get_scraper()
        draws = scraper.scrape_latest(limit=10)
        end_time = time.time()
        
        print(f"✅ Original scraper completed in {end_time - start_time:.2f}s")
        print(f"📊 Retrieved {len(draws)} draws")
        
        for i, draw in enumerate(draws[:3], 1):
            try:
                main_nums = [draw[f'n{j}'] for j in range(1, 6)]
                stars = [draw['s1'], draw['s2']]
                date = draw.get('draw_date', 'N/A')
                print(f"   {i}. {date}: {main_nums} | ⭐ {stars}")
            except KeyError as e:
                print(f"   {i}. Invalid draw format: {e}")
        
        return len(draws)
        
    except Exception as e:
        print(f"❌ Original scraper failed: {e}")
        return 0


def test_enhanced_scraper():
    """Test the enhanced scraper."""
    print("\n🚀 Testing Enhanced Scraper")
    print("-" * 40)
    
    try:
        from enhanced_scraper import enhanced_scrape_latest
        
        start_time = time.time()
        draws = enhanced_scrape_latest(limit=10)
        end_time = time.time()
        
        print(f"✅ Enhanced scraper completed in {end_time - start_time:.2f}s")
        print(f"📊 Retrieved {len(draws)} draws")
        
        for i, draw in enumerate(draws[:3], 1):
            try:
                main_nums = [draw[f'n{j}'] for j in range(1, 6)]
                stars = [draw['s1'], draw['s2']]
                date = draw.get('draw_date', 'N/A')
                source = draw.get('source', 'unknown')
                print(f"   {i}. {date}: {main_nums} | ⭐ {stars} (source: {source})")
            except KeyError as e:
                print(f"   {i}. Invalid draw format: {e}")
        
        return len(draws)
        
    except Exception as e:
        print(f"❌ Enhanced scraper failed: {e}")
        return 0


def validate_draw_format(draws: List[Dict[str, Any]]) -> Dict[str, int]:
    """Validate draw format and return statistics."""
    stats = {
        "valid_draws": 0,
        "invalid_format": 0,
        "invalid_ranges": 0,
        "missing_dates": 0,
        "duplicate_numbers": 0,
    }
    
    for draw in draws:
        try:
            # Check if all required fields exist
            main_nums = [draw[f'n{i}'] for i in range(1, 6)]
            stars = [draw['s1'], draw['s2']]
            draw_date = draw.get('draw_date')
            
            # Check number ranges
            if not all(1 <= n <= 50 for n in main_nums):
                stats["invalid_ranges"] += 1
                continue
                
            if not all(1 <= s <= 12 for s in stars):
                stats["invalid_ranges"] += 1
                continue
            
            # Check for duplicate numbers
            if len(set(main_nums)) != 5 or len(set(stars)) != 2:
                stats["duplicate_numbers"] += 1
                continue
            
            # Check date
            if not draw_date:
                stats["missing_dates"] += 1
            
            stats["valid_draws"] += 1
            
        except (KeyError, TypeError, ValueError):
            stats["invalid_format"] += 1
    
    return stats


def main():
    """Main comparison test."""
    print("🎯 EuroMillions Scraper Comparison Test")
    print("=" * 50)
    
    # Test original scraper
    original_count = test_original_scraper()
    
    # Test enhanced scraper
    enhanced_count = test_enhanced_scraper()
    
    # Summary
    print("\n📈 Summary")
    print("-" * 20)
    print(f"Original Scraper: {original_count} draws")
    print(f"Enhanced Scraper: {enhanced_count} draws")
    
    if enhanced_count > original_count:
        print("🏆 Enhanced scraper performed better!")
        improvement = ((enhanced_count - original_count) / max(original_count, 1)) * 100
        print(f"   Improvement: {improvement:.1f}% more draws retrieved")
    elif original_count > enhanced_count:
        print("🔄 Original scraper performed better")
    else:
        print("🤝 Both scrapers performed equally")
    
    # Test format validation
    if enhanced_count > 0:
        print("\n🔍 Testing Enhanced Scraper Draw Quality")
        print("-" * 40)
        
        try:
            from enhanced_scraper import enhanced_scrape_latest
            test_draws = enhanced_scrape_latest(limit=20)
            stats = validate_draw_format(test_draws)
            
            print(f"✅ Valid draws: {stats['valid_draws']}")
            print(f"❌ Invalid format: {stats['invalid_format']}")
            print(f"🔢 Invalid ranges: {stats['invalid_ranges']}")
            print(f"📅 Missing dates: {stats['missing_dates']}")
            print(f"🔄 Duplicate numbers: {stats['duplicate_numbers']}")
            
            if stats['valid_draws'] > 0:
                quality_score = (stats['valid_draws'] / len(test_draws)) * 100
                print(f"📊 Data quality: {quality_score:.1f}%")
        
        except Exception as e:
            print(f"❌ Quality test failed: {e}")


if __name__ == "__main__":
    main()