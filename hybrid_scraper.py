#!/usr/bin/env python3
"""
Hybrid Scraper
==============

Combines the speed of the original scraper with enhanced error handling.
"""

import time
from typing import List, Dict, Any, Optional
from loguru import logger


def hybrid_scrape_latest(limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Hybrid scraper that tries original first, then enhanced as fallback.
    
    Strategy:
    1. Try original scraper (fast, reliable when working)
    2. If original fails or returns insufficient data, try enhanced scraper
    3. Combine and deduplicate results
    """
    logger.info(f"🔄 Starting hybrid scrape for {limit} draws (offset: {offset})")
    
    all_draws = []
    
    # Step 1: Try original scraper
    try:
        logger.info("📊 Trying original scraper...")
        from scraper import get_scraper
        
        original_scraper = get_scraper()
        original_draws = original_scraper.scrape_latest(limit=limit + offset, offset=0)
        
        if original_draws:
            logger.info(f"✅ Original scraper got {len(original_draws)} draws")
            
            # Apply offset manually
            if offset > 0:
                original_draws = original_draws[offset:]
            
            all_draws.extend(original_draws[:limit])
            
            # If we have enough draws and they look valid, return them
            if len(all_draws) >= limit and _validate_draws_quick(all_draws):
                logger.info(f"🎯 Original scraper provided sufficient quality data")
                return all_draws[:limit]
        else:
            logger.warning("⚠️ Original scraper returned no draws")
            
    except Exception as e:
        logger.warning(f"❌ Original scraper failed: {e}")
    
    # Step 2: Try enhanced scraper if needed
    remaining_needed = limit - len(all_draws)
    
    if remaining_needed > 0:
        logger.info(f"🚀 Trying enhanced scraper for {remaining_needed} more draws...")
        
        try:
            from enhanced_scraper import EnhancedEuromillionsScraper
            
            enhanced_scraper = EnhancedEuromillionsScraper()
            enhanced_draws = enhanced_scraper.scrape_latest_draws(limit=remaining_needed + 5)  # Get a few extra
            
            if enhanced_draws:
                logger.info(f"✅ Enhanced scraper got {len(enhanced_draws)} draws")
                all_draws.extend(enhanced_draws)
            else:
                logger.warning("⚠️ Enhanced scraper returned no draws")
                
        except Exception as e:
            logger.error(f"❌ Enhanced scraper failed: {e}")
    
    # Step 3: Deduplicate and return best results
    unique_draws = _deduplicate_hybrid_draws(all_draws)
    final_draws = unique_draws[:limit]
    
    logger.info(f"🎯 Hybrid scrape completed: {len(final_draws)} draws from {len(all_draws)} total")
    
    return final_draws


def _validate_draws_quick(draws: List[Dict[str, Any]]) -> bool:
    """Quick validation of draw data quality."""
    if not draws:
        return False
    
    valid_count = 0
    
    for draw in draws[:5]:  # Check first 5 draws
        try:
            # Check required fields exist
            main_nums = [draw[f'n{i}'] for i in range(1, 6)]
            stars = [draw['s1'], draw['s2']]
            
            # Check basic ranges
            if (all(isinstance(n, (int, float)) and 1 <= n <= 50 for n in main_nums) and
                all(isinstance(s, (int, float)) and 1 <= s <= 12 for s in stars)):
                valid_count += 1
                
        except (KeyError, TypeError, ValueError):
            continue
    
    # Consider valid if at least 80% of checked draws are valid
    return valid_count >= len(draws[:5]) * 0.8


def _deduplicate_hybrid_draws(draws: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicate draws from multiple sources."""
    seen_signatures = set()
    unique_draws = []
    
    for draw in draws:
        try:
            # Create signature from numbers and date
            main_nums = tuple(sorted([int(draw[f'n{i}']) for i in range(1, 6)]))
            stars = tuple(sorted([int(draw['s1']), int(draw['s2'])]))
            
            # Use draw_date if available, otherwise use numbers as signature
            draw_date = draw.get('draw_date', '')
            if isinstance(draw_date, str) and len(draw_date) >= 10:
                date_key = draw_date[:10]  # Use YYYY-MM-DD part
            else:
                date_key = f"unknown-{len(unique_draws)}"
            
            signature = (date_key, main_nums, stars)
            
            if signature not in seen_signatures:
                seen_signatures.add(signature)
                unique_draws.append(draw)
                
        except (KeyError, ValueError, TypeError) as e:
            logger.debug(f"Skipping invalid draw during deduplication: {e}")
            continue
    
    return unique_draws


def get_best_available_draws(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Get the best available draws using multiple strategies.
    
    This is the recommended function to use for getting EuroMillions data.
    """
    strategies = [
        ("hybrid", lambda: hybrid_scrape_latest(limit=limit)),
        ("original_only", lambda: _try_original_only(limit)),
        ("enhanced_only", lambda: _try_enhanced_only(limit)),
    ]
    
    for strategy_name, strategy_func in strategies:
        try:
            logger.info(f"🎯 Trying strategy: {strategy_name}")
            draws = strategy_func()
            
            if draws and len(draws) > 0:
                logger.info(f"✅ Strategy '{strategy_name}' succeeded with {len(draws)} draws")
                return draws
            else:
                logger.warning(f"⚠️ Strategy '{strategy_name}' returned no draws")
                
        except Exception as e:
            logger.warning(f"❌ Strategy '{strategy_name}' failed: {e}")
            continue
    
    logger.error("🚨 All scraping strategies failed!")
    return []


def _try_original_only(limit: int) -> List[Dict[str, Any]]:
    """Try only the original scraper."""
    from scraper import get_scraper
    scraper = get_scraper()
    return scraper.scrape_latest(limit=limit)


def _try_enhanced_only(limit: int) -> List[Dict[str, Any]]:
    """Try only the enhanced scraper."""
    from enhanced_scraper import EnhancedEuromillionsScraper
    scraper = EnhancedEuromillionsScraper()
    return scraper.scrape_latest_draws(limit=limit)


# Convenience functions for backward compatibility
def scrape_latest_hybrid(limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
    """Hybrid scraping function - recommended for production use."""
    return hybrid_scrape_latest(limit=limit, offset=offset)


if __name__ == "__main__":
    # Test the hybrid scraper
    print("🎯 Testing Hybrid EuroMillions Scraper")
    print("=" * 50)
    
    start_time = time.time()
    draws = get_best_available_draws(limit=10)
    end_time = time.time()
    
    print(f"⏱️  Completed in {end_time - start_time:.2f} seconds")
    print(f"📊 Retrieved {len(draws)} draws")
    print()
    
    for i, draw in enumerate(draws, 1):
        try:
            main_nums = [draw[f'n{j}'] for j in range(1, 6)]
            stars = [draw['s1'], draw['s2']]
            date = draw.get('draw_date', 'N/A')
            source = draw.get('source', 'unknown')
            
            print(f"{i:2d}. {date}: {main_nums} | ⭐ {stars} (source: {source})")
            
        except KeyError as e:
            print(f"{i:2d}. ❌ Invalid draw format: {e}")
    
    print("\n🏆 Hybrid scraper test completed!")