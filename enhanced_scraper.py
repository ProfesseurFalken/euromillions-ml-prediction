#!/usr/bin/env python3
"""
Enhanced EuroMillions Scraper
============================

Improved scraper with better error handling, multiple sources,
and more robust parsing strategies.
"""

import re
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from bs4 import BeautifulSoup
from loguru import logger
import json
import time
import random
from urllib.parse import urljoin, urlparse


class EnhancedEuromillionsScraper:
    """Enhanced scraper with multiple sources and robust parsing."""
    
    def __init__(self):
        """Initialize enhanced scraper."""
        self.session = requests.Session()
        self.setup_session()
        
        # Multiple sources for better reliability
        self.sources = {
            "uk_national": {
                "name": "UK National Lottery",
                "base_url": "https://www.national-lottery.co.uk",
                "draw_history": "https://www.national-lottery.co.uk/results/euromillions/draw-history",
                "priority": 1,
                "parser": self._parse_uk_national_lottery
            },
            "euro_millions_com": {
                "name": "Euro-Millions.com",
                "base_url": "https://www.euro-millions.com",
                "draw_history": "https://www.euro-millions.com/results",
                "priority": 2,
                "parser": self._parse_euro_millions_com
            },
            "fdj_france": {
                "name": "FDJ France",
                "base_url": "https://www.fdj.fr",
                "draw_history": "https://www.fdj.fr/resultats-et-rapports-officiels/euromillions",
                "priority": 3,
                "parser": self._parse_fdj_france
            }
        }
        
        # Enhanced selectors for different websites
        self.selectors = {
            "numbers": [
                ".ball-number, .main-number, .numero",
                ".result-ball, .winning-number",
                ".ball, .number, .num",
                "[class*='ball'], [class*='number']",
                ".draw-results .number",
            ],
            "stars": [
                ".star-number, .lucky-star, .etoile",
                ".star, .lucky",
                "[class*='star'], [class*='lucky']",
                ".draw-results .star",
            ],
            "dates": [
                ".draw-date, .date, .when",
                ".result-date, .draw-info",
                "[class*='date'], [class*='when']",
                "time, .time",
            ],
            "jackpot": [
                ".jackpot, .prize, .gain",
                ".jackpot-amount, .prize-amount",
                "[class*='jackpot'], [class*='prize']",
            ]
        }
    
    def setup_session(self):
        """Setup HTTP session with rotating user agents."""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        ]
        
        self.session.headers.update({
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        })
    
    def scrape_latest_draws(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Scrape latest draws using multiple sources."""
        all_draws = []
        
        # Sort sources by priority
        sorted_sources = sorted(self.sources.items(), key=lambda x: x[1]["priority"])
        
        for source_id, source_config in sorted_sources:
            logger.info(f"Trying source: {source_config['name']}")
            
            try:
                draws = source_config["parser"](limit)
                
                if draws:
                    logger.info(f"✅ Got {len(draws)} draws from {source_config['name']}")
                    all_draws.extend(draws)
                    
                    # If we have enough draws, break
                    if len(all_draws) >= limit:
                        break
                else:
                    logger.warning(f"⚠️  No draws from {source_config['name']}")
                    
            except Exception as e:
                logger.error(f"❌ Failed to scrape {source_config['name']}: {e}")
                continue
        
        # Remove duplicates and sort by date
        unique_draws = self._deduplicate_draws(all_draws)
        return sorted(unique_draws, key=lambda x: x.get('draw_date', ''), reverse=True)[:limit]
    
    def _parse_uk_national_lottery(self, limit: int) -> List[Dict[str, Any]]:
        """Parse UK National Lottery with enhanced pattern matching."""
        url = self.sources["uk_national"]["draw_history"]
        
        try:
            response = self._fetch_with_retry(url, max_retries=3)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Enhanced pattern matching for UK site
            draws = []
            
            # Method 1: Look for draw result containers
            draw_containers = soup.find_all(['div', 'section', 'article'], class_=re.compile(r'(draw|result|winning)'))
            
            for container in draw_containers[:limit]:
                draw_data = self._extract_draw_from_container(container, 'uk_national')
                if draw_data:
                    draws.append(draw_data)
            
            # Method 2: Pattern matching in text
            if len(draws) < limit:
                text_draws = self._extract_draws_from_text(soup.get_text(), limit - len(draws))
                draws.extend(text_draws)
            
            return draws
            
        except Exception as e:
            logger.error(f"UK National Lottery parsing failed: {e}")
            return []
    
    def _parse_euro_millions_com(self, limit: int) -> List[Dict[str, Any]]:
        """Parse Euro-Millions.com with multiple strategies."""
        url = self.sources["euro_millions_com"]["draw_history"]
        
        try:
            response = self._fetch_with_retry(url, max_retries=3)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            draws = []
            
            # Look for result links
            result_links = soup.find_all('a', href=re.compile(r'/results/\d{2}-\d{2}-\d{4}'))
            
            for link in result_links[:limit]:
                draw_url = urljoin(url, link['href'])
                draw_data = self._parse_single_draw(draw_url)
                if draw_data:
                    draws.append(draw_data)
                    
                # Be nice to the server
                time.sleep(0.5)
            
            return draws
            
        except Exception as e:
            logger.error(f"Euro-Millions.com parsing failed: {e}")
            return []
    
    def _parse_fdj_france(self, limit: int) -> List[Dict[str, Any]]:
        """Parse FDJ France site."""
        url = self.sources["fdj_france"]["draw_history"]
        
        try:
            response = self._fetch_with_retry(url, max_retries=3)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # FDJ often uses JSON data embedded in script tags
            script_tags = soup.find_all('script', type='application/json')
            
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    draws = self._extract_draws_from_json_data(data, limit)
                    if draws:
                        return draws
                except (json.JSONDecodeError, KeyError):
                    continue
            
            # Fallback to HTML parsing
            return self._extract_draws_from_html(soup, limit)
            
        except Exception as e:
            logger.error(f"FDJ France parsing failed: {e}")
            return []
    
    def _extract_draw_from_container(self, container, source_type: str) -> Optional[Dict[str, Any]]:
        """Extract draw data from a container element."""
        try:
            # Extract numbers using multiple selector strategies
            main_numbers = []
            star_numbers = []
            
            # Try different selectors
            for selector in self.selectors["numbers"]:
                number_elements = container.select(selector)
                for elem in number_elements:
                    try:
                        num = int(elem.get_text().strip())
                        if 1 <= num <= 50 and len(main_numbers) < 5:
                            main_numbers.append(num)
                    except (ValueError, AttributeError):
                        continue
                
                if len(main_numbers) >= 5:
                    break
            
            # Extract stars
            for selector in self.selectors["stars"]:
                star_elements = container.select(selector)
                for elem in star_elements:
                    try:
                        num = int(elem.get_text().strip())
                        if 1 <= num <= 12 and len(star_numbers) < 2:
                            star_numbers.append(num)
                    except (ValueError, AttributeError):
                        continue
                
                if len(star_numbers) >= 2:
                    break
            
            # Extract date
            draw_date = self._extract_date_from_container(container)
            
            # Extract jackpot
            jackpot = self._extract_jackpot_from_container(container)
            
            # Validate we have complete data
            if len(main_numbers) == 5 and len(star_numbers) == 2:
                main_numbers.sort()
                star_numbers.sort()
                
                draw_id = draw_date or datetime.now().strftime('%Y-%m-%d')
                
                return {
                    "draw_id": draw_id,
                    "draw_date": draw_date or draw_id,
                    "n1": main_numbers[0], "n2": main_numbers[1], "n3": main_numbers[2],
                    "n4": main_numbers[3], "n5": main_numbers[4],
                    "s1": star_numbers[0], "s2": star_numbers[1],
                    "jackpot": jackpot,
                    "source": source_type
                }
            
            return None
            
        except Exception as e:
            logger.debug(f"Container parsing failed: {e}")
            return None
    
    def _extract_draws_from_text(self, text: str, limit: int) -> List[Dict[str, Any]]:
        """Extract draws using advanced regex patterns."""
        draws = []
        
        # Enhanced regex patterns
        patterns = [
            # Pattern: 12-25-33-41-48 + 2-9 (with date)
            r'(\d{4}-\d{2}-\d{2}).*?(\d{1,2})\s*[-,]\s*(\d{1,2})\s*[-,]\s*(\d{1,2})\s*[-,]\s*(\d{1,2})\s*[-,]\s*(\d{1,2})\s*.*?(\d{1,2})\s*[-,]\s*(\d{1,2})',
            
            # Pattern: Numbers: 1, 5, 12, 23, 44 Stars: 3, 8
            r'Numbers?\s*:?\s*(\d{1,2})\s*,\s*(\d{1,2})\s*,\s*(\d{1,2})\s*,\s*(\d{1,2})\s*,\s*(\d{1,2})\s*.*?Stars?\s*:?\s*(\d{1,2})\s*,\s*(\d{1,2})',
            
            # Pattern: Winning numbers 5 12 23 44 49 Lucky Stars 3 8
            r'[Ww]inning.*?(\d{1,2})\s+(\d{1,2})\s+(\d{1,2})\s+(\d{1,2})\s+(\d{1,2}).*?[Ss]tars?\s+(\d{1,2})\s+(\d{1,2})',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                try:
                    groups = match.groups()
                    
                    # Check if first group is a date
                    if len(groups) >= 8 and re.match(r'\d{4}-\d{2}-\d{2}', groups[0]):
                        draw_date = groups[0]
                        numbers = [int(x) for x in groups[1:8]]
                    else:
                        draw_date = datetime.now().strftime('%Y-%m-%d')
                        numbers = [int(x) for x in groups[:7]]
                    
                    main_numbers = sorted(numbers[:5])
                    star_numbers = sorted(numbers[5:7])
                    
                    # Validate ranges
                    if (all(1 <= n <= 50 for n in main_numbers) and 
                        all(1 <= s <= 12 for s in star_numbers)):
                        
                        draws.append({
                            "draw_id": draw_date,
                            "draw_date": draw_date,
                            "n1": main_numbers[0], "n2": main_numbers[1], "n3": main_numbers[2],
                            "n4": main_numbers[3], "n5": main_numbers[4],
                            "s1": star_numbers[0], "s2": star_numbers[1],
                            "jackpot": None,
                            "source": "text_extraction"
                        })
                        
                        if len(draws) >= limit:
                            break
                            
                except (ValueError, IndexError) as e:
                    logger.debug(f"Pattern match failed: {e}")
                    continue
            
            if len(draws) >= limit:
                break
        
        return draws
    
    def _extract_date_from_container(self, container) -> Optional[str]:
        """Extract date from container using multiple strategies."""
        # Try date selectors
        for selector in self.selectors["dates"]:
            date_elements = container.select(selector)
            for elem in date_elements:
                date_text = elem.get_text().strip()
                parsed_date = self._parse_date_string(date_text)
                if parsed_date:
                    return parsed_date
        
        # Try datetime attributes
        datetime_elem = container.find(attrs={"datetime": True})
        if datetime_elem:
            return self._parse_date_string(datetime_elem.get("datetime"))
        
        # Try data attributes
        for attr in ["data-date", "data-draw-date", "data-when"]:
            if container.has_attr(attr):
                return self._parse_date_string(container[attr])
        
        return None
    
    def _parse_date_string(self, date_str: str) -> Optional[str]:
        """Parse various date formats to YYYY-MM-DD."""
        if not date_str:
            return None
            
        # Clean the string
        date_str = re.sub(r'[^\d\-/\w\s]', '', date_str).strip()
        
        formats = [
            '%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y',
            '%Y/%m/%d', '%d/%m/%Y', '%m/%d/%Y',
            '%d %B %Y', '%d %b %Y', '%B %d %Y', '%b %d %Y',
            '%d %B, %Y', '%d %b, %Y', '%B %d, %Y', '%b %d, %Y',
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # Try regex extraction
        date_match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_str)
        if date_match:
            year, month, day = date_match.groups()
            try:
                parsed = datetime(int(year), int(month), int(day))
                return parsed.strftime('%Y-%m-%d')
            except ValueError:
                pass
        
        return None
    
    def _extract_jackpot_from_container(self, container) -> Optional[float]:
        """Extract jackpot amount from container."""
        for selector in self.selectors["jackpot"]:
            jackpot_elements = container.select(selector)
            for elem in jackpot_elements:
                text = elem.get_text().strip()
                amount = self._parse_currency_amount(text)
                if amount:
                    return amount
        return None
    
    def _parse_currency_amount(self, text: str) -> Optional[float]:
        """Parse currency amounts from text."""
        # Remove currency symbols and clean
        cleaned = re.sub(r'[€$£,\s]', '', text)
        
        # Find number patterns
        amount_match = re.search(r'(\d+(?:\.\d+)?)', cleaned)
        if amount_match:
            try:
                amount = float(amount_match.group(1))
                
                # Handle millions/thousands indicators
                if 'million' in text.lower() or 'm' in text.lower():
                    amount *= 1_000_000
                elif 'thousand' in text.lower() or 'k' in text.lower():
                    amount *= 1_000
                
                return amount
            except ValueError:
                pass
        
        return None
    
    def _extract_draws_from_json_data(self, data: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """Extract draws from JSON data structure."""
        draws = []
        
        # Common JSON structures for lottery data
        possible_keys = ['results', 'draws', 'data', 'lottery', 'euromillions']
        
        def search_json_recursive(obj, depth=0):
            if depth > 5:  # Limit recursion depth
                return
                
            if isinstance(obj, dict):
                # Look for draw data in dictionary
                for key, value in obj.items():
                    if key.lower() in ['date', 'numbers', 'stars', 'main', 'lucky']:
                        # Potential draw data found
                        draw_data = self._parse_json_draw(obj)
                        if draw_data:
                            draws.append(draw_data)
                            return
                    elif isinstance(value, (dict, list)):
                        search_json_recursive(value, depth + 1)
                        
            elif isinstance(obj, list):
                for item in obj:
                    if len(draws) >= limit:
                        break
                    search_json_recursive(item, depth + 1)
        
        search_json_recursive(data)
        return draws[:limit]
    
    def _parse_json_draw(self, draw_obj: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse a single draw from JSON object."""
        try:
            # Extract date
            date_str = None
            for date_key in ['date', 'draw_date', 'when', 'dateDrawn']:
                if date_key in draw_obj:
                    date_str = self._parse_date_string(str(draw_obj[date_key]))
                    break
            
            # Extract main numbers
            main_numbers = []
            for num_key in ['numbers', 'main_numbers', 'mainNumbers', 'balls']:
                if num_key in draw_obj:
                    nums = draw_obj[num_key]
                    if isinstance(nums, list):
                        main_numbers = [int(n) for n in nums if isinstance(n, (int, str)) and str(n).isdigit()]
                    break
            
            # Extract star numbers
            star_numbers = []
            for star_key in ['stars', 'lucky_stars', 'luckyStars', 'euroNumbers']:
                if star_key in draw_obj:
                    stars = draw_obj[star_key]
                    if isinstance(stars, list):
                        star_numbers = [int(s) for s in stars if isinstance(s, (int, str)) and str(s).isdigit()]
                    break
            
            # Validate data
            if len(main_numbers) == 5 and len(star_numbers) == 2:
                main_numbers.sort()
                star_numbers.sort()
                
                if (all(1 <= n <= 50 for n in main_numbers) and 
                    all(1 <= s <= 12 for s in star_numbers)):
                    
                    draw_id = date_str or datetime.now().strftime('%Y-%m-%d')
                    
                    return {
                        "draw_id": draw_id,
                        "draw_date": date_str or draw_id,
                        "n1": main_numbers[0], "n2": main_numbers[1], "n3": main_numbers[2],
                        "n4": main_numbers[3], "n5": main_numbers[4],
                        "s1": star_numbers[0], "s2": star_numbers[1],
                        "jackpot": draw_obj.get('jackpot'),
                        "source": "json_extraction"
                    }
            
            return None
            
        except (ValueError, KeyError, TypeError) as e:
            logger.debug(f"JSON draw parsing failed: {e}")
            return None
    
    def _extract_draws_from_html(self, soup: BeautifulSoup, limit: int) -> List[Dict[str, Any]]:
        """Extract draws from HTML using generic patterns."""
        draws = []
        
        # Look for tables with draw data
        tables = soup.find_all('table')
        for table in tables:
            table_draws = self._extract_draws_from_table(table, limit - len(draws))
            draws.extend(table_draws)
            if len(draws) >= limit:
                break
        
        # Look for structured divs
        if len(draws) < limit:
            result_divs = soup.find_all('div', class_=re.compile(r'(result|draw|winning)', re.I))
            for div in result_divs:
                if len(draws) >= limit:
                    break
                draw_data = self._extract_draw_from_container(div, 'html_extraction')
                if draw_data:
                    draws.append(draw_data)
        
        return draws[:limit]
    
    def _extract_draws_from_table(self, table, limit: int) -> List[Dict[str, Any]]:
        """Extract draws from table structure."""
        draws = []
        rows = table.find_all('tr')
        
        for row in rows[1:]:  # Skip header row
            if len(draws) >= limit:
                break
                
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 7:  # Need at least 7 cells for 5 numbers + 2 stars
                try:
                    # Try to extract numbers from cells
                    numbers = []
                    for cell in cells:
                        text = cell.get_text().strip()
                        if text.isdigit():
                            numbers.append(int(text))
                    
                    if len(numbers) >= 7:
                        main_numbers = sorted(numbers[:5])
                        star_numbers = sorted(numbers[5:7])
                        
                        if (all(1 <= n <= 50 for n in main_numbers) and 
                            all(1 <= s <= 12 for s in star_numbers)):
                            
                            # Try to extract date from first cell
                            date_cell = cells[0].get_text().strip()
                            draw_date = self._parse_date_string(date_cell) or datetime.now().strftime('%Y-%m-%d')
                            
                            draws.append({
                                "draw_id": draw_date,
                                "draw_date": draw_date,
                                "n1": main_numbers[0], "n2": main_numbers[1], "n3": main_numbers[2],
                                "n4": main_numbers[3], "n5": main_numbers[4],
                                "s1": star_numbers[0], "s2": star_numbers[1],
                                "jackpot": None,
                                "source": "table_extraction"
                            })
                
                except (ValueError, IndexError):
                    continue
        
        return draws
    
    def _fetch_with_retry(self, url: str, max_retries: int = 3) -> requests.Response:
        """Fetch URL with retry logic."""
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                return response
                
            except requests.RequestException as e:
                last_exception = e
                if attempt == max_retries - 1:
                    break
                
                wait_time = (attempt + 1) * 2
                logger.warning(f"Attempt {attempt + 1} failed for {url}, retrying in {wait_time}s...")
                time.sleep(wait_time)
        
        # If we get here, all attempts failed
        raise last_exception or requests.RequestException(f"Failed to fetch {url} after {max_retries} attempts")
    
    def _deduplicate_draws(self, draws: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate draws based on draw_id and numbers."""
        seen = set()
        unique_draws = []
        
        for draw in draws:
            # Create signature from numbers - filter out None values and ensure they're integers
            main_nums_raw = [draw.get(f'n{i}') for i in range(1, 6) if draw.get(f'n{i}') is not None]
            stars_raw = [s for s in [draw.get('s1'), draw.get('s2')] if s is not None]
            
            # Convert to integers and sort
            try:
                main_nums = tuple(sorted([int(n) for n in main_nums_raw if isinstance(n, (int, str, float))]))
                stars = tuple(sorted([int(s) for s in stars_raw if isinstance(s, (int, str, float))]))
            except (ValueError, TypeError):
                continue
                
            signature = (draw.get('draw_id'), main_nums, stars)
            
            if signature not in seen and len(main_nums) == 5 and len(stars) == 2:
                seen.add(signature)
                unique_draws.append(draw)
        
        return unique_draws
    
    def _parse_single_draw(self, url: str) -> Optional[Dict[str, Any]]:
        """Parse a single draw from its URL."""
        try:
            response = self._fetch_with_retry(url, max_retries=2)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract from main content area
            main_content = soup.find('main') or soup.find('body')
            if main_content:
                return self._extract_draw_from_container(main_content, 'single_draw')
            
            return None
            
        except Exception as e:
            logger.debug(f"Single draw parsing failed for {url}: {e}")
            return None


# Wrapper function to maintain compatibility
def enhanced_scrape_latest(limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
    """Enhanced scraping function with better reliability."""
    scraper = EnhancedEuromillionsScraper()
    
    try:
        all_draws = scraper.scrape_latest_draws(limit + offset)
        
        # Apply offset
        if offset > 0:
            all_draws = all_draws[offset:]
        
        return all_draws[:limit]
        
    except Exception as e:
        logger.error(f"Enhanced scraping failed: {e}")
        
        # Fallback - return empty list if everything fails
        logger.error("All scraping methods failed, returning empty list")
        return []


if __name__ == "__main__":
    # Test the enhanced scraper
    print("🚀 Testing Enhanced EuroMillions Scraper")
    print("=" * 50)
    
    scraper = EnhancedEuromillionsScraper()
    draws = scraper.scrape_latest_draws(limit=5)
    
    print(f"✅ Retrieved {len(draws)} draws")
    
    for i, draw in enumerate(draws, 1):
        main_nums = [draw[f'n{j}'] for j in range(1, 6)]
        stars = [draw['s1'], draw['s2']]
        source = draw.get('source', 'unknown')
        
        print(f"{i}. {draw['draw_date']}: {main_nums} | ⭐ {stars} (source: {source})")
    
    print("\n🎯 Enhanced scraper test completed!")