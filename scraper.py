"""
EuromillionsScraper for fetching and parsing draw data from official sources.
Handles HTML variations with multiple selectors and regex fallbacks.
"""
import re
import requests
from datetime import datetime
from typing import List, Dict, Optional, Any
from bs4 import BeautifulSoup
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from config import get_settings


class EuromillionsScraper:
    """Scraper for Euromillions draw data with robust parsing."""
    
    def __init__(self):
        """Initialize scraper with settings."""
        self.settings = get_settings()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.settings.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Official Euromillions URLs (you may need to adjust based on your region)
        self.base_urls = [
            "https://www.national-lottery.co.uk",  # UK National Lottery (primary)
            "https://www.euro-millions.com",
            "https://www.euromillions.com"
        ]
        
        # UK National Lottery specific URLs
        self.uk_urls = {
            "draw_history": "https://www.national-lottery.co.uk/results/euromillions/draw-history",
            "latest_results": "https://www.national-lottery.co.uk/results/euromillions",
            "archive": "https://www.national-lottery.co.uk/results/euromillions/draw-history"
        }
        
        # Common URL patterns for draws
        self.draw_url_patterns = [
            r'/euromillions/results/(\d{4}-\d{2}-\d{2})',
            r'/draw/(\d{4}-\d{2}-\d{2})',
            r'/results/(\d{4}-\d{2}-\d{2})',
            r'/euromillions/(\d{4}/\d{2}/\d{2})',
        ]
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def _fetch_page(self, url: str) -> BeautifulSoup:
        """
        Fetch and parse a web page with retries.
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup: Parsed HTML content
            
        Raises:
            requests.RequestException: If all retries fail
        """
        logger.info(f"Fetching: {url}")
        
        response = self.session.get(
            url,
            timeout=self.settings.request_timeout,
            allow_redirects=True
        )
        response.raise_for_status()
        
        # Parse with lxml parser
        soup = BeautifulSoup(response.content, 'lxml')
        logger.debug(f"Successfully parsed page: {len(response.content)} bytes")
        
        return soup
    
    def list_recent_draw_urls(self, limit: int = 20) -> List[str]:
        """
        Fetch recent draw URLs from official pages.
        
        Args:
            limit: Maximum number of URLs to return
            
        Returns:
            List[str]: Draw URLs (newest first)
        """
        all_urls = []
        
        # Try different base URLs and archive pages
        archive_paths = [
            "/results",
            "/euromillions/results",
            "/games/euromillions/results",
            "/draw-history",
            "/archive"
        ]
        
        for base_url in self.base_urls:
            for archive_path in archive_paths:
                try:
                    url = f"{base_url}{archive_path}"
                    soup = self._fetch_page(url)
                    urls = self._extract_draw_urls_from_page(soup, base_url)
                    all_urls.extend(urls)
                    
                    if len(all_urls) >= limit:
                        break
                        
                except Exception as e:
                    logger.warning(f"Failed to fetch from {url}: {e}")
                    continue
            
            if len(all_urls) >= limit:
                break
        
        # Remove duplicates and sort by date (newest first)
        unique_urls = list(dict.fromkeys(all_urls))  # Preserves order
        unique_urls = self._sort_urls_by_date(unique_urls)
        
        return unique_urls[:limit]
    
    def _extract_draw_urls_from_page(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract draw URLs from a results/archive page."""
        urls = []
        
        # Multiple selectors for different site layouts
        link_selectors = [
            'a[href*="results"]',
            'a[href*="draw"]',
            'a[href*="euromillions"]',
            '.result-link a',
            '.draw-link a',
            '.results-table a',
            'table a[href*="20"]',  # Links containing years
        ]
        
        for selector in link_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href:
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        href = base_url + href
                    elif not href.startswith('http'):
                        href = f"{base_url}/{href}"
                    
                    # Check if URL matches draw patterns
                    if self._is_draw_url(href):
                        urls.append(href)
        
        # Regex fallback for embedded URLs in text/scripts
        page_text = str(soup)
        for pattern in self.draw_url_patterns:
            matches = re.finditer(pattern, page_text)
            for match in matches:
                # Reconstruct full URL
                date_part = match.group(1)
                url = f"{base_url}/euromillions/results/{date_part}"
                urls.append(url)
        
        return urls
    
    def _is_draw_url(self, url: str) -> bool:
        """Check if URL appears to be a draw results URL."""
        # Look for date patterns in URL
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
            r'\d{2}-\d{2}-\d{4}',  # DD-MM-YYYY
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, url):
                return True
        
        return False
    
    def _sort_urls_by_date(self, urls: List[str]) -> List[str]:
        """Sort URLs by extracted date (newest first)."""
        def extract_date(url):
            # Extract date from URL for sorting
            for pattern in [r'(\d{4}-\d{2}-\d{2})', r'(\d{4}/\d{2}/\d{2})']:
                match = re.search(pattern, url)
                if match:
                    date_str = match.group(1).replace('/', '-')
                    try:
                        return datetime.strptime(date_str, '%Y-%m-%d')
                    except ValueError:
                        continue
            return datetime.min  # Fallback for unparseable dates
        
        return sorted(urls, key=extract_date, reverse=True)
    
    def parse_draw(self, url: str) -> Dict[str, Any]:
        """
        Parse a single draw page and extract all data.
        
        Args:
            url: URL of the draw page
            
        Returns:
            Dict containing draw data
            
        Raises:
            ValueError: If draw data is invalid
        """
        logger.info(f"Parsing draw: {url}")
        
        soup = self._fetch_page(url)
        raw_html = str(soup)
        
        # Extract draw ID and date from URL or page
        draw_id, draw_date = self._extract_draw_date(url, soup)
        
        # Extract numbers with multiple strategies
        numbers = self._extract_numbers(soup)
        
        # Extract jackpot amount
        jackpot = self._extract_jackpot(soup)
        
        # Extract prize table
        prize_table = self._extract_prize_table(soup)
        
        # Validate extracted data
        self._validate_draw_data(numbers, draw_id)
        
        return {
            "draw_id": draw_id,
            "draw_date": draw_date,
            "n1": numbers["main"][0],
            "n2": numbers["main"][1], 
            "n3": numbers["main"][2],
            "n4": numbers["main"][3],
            "n5": numbers["main"][4],
            "s1": numbers["stars"][0],
            "s2": numbers["stars"][1],
            "jackpot": jackpot,
            "prize_table_json": prize_table,
            "raw_html": raw_html
        }
    
    def _extract_draw_date(self, url: str, soup: BeautifulSoup) -> tuple[str, str]:
        """Extract draw ID and date from URL or page content."""
        # Try to extract from URL first
        for pattern in [r'(\d{4}-\d{2}-\d{2})', r'(\d{4}/\d{2}/\d{2})']:
            match = re.search(pattern, url)
            if match:
                date_str = match.group(1).replace('/', '-')
                return date_str, date_str
        
        # Try to extract from page content
        date_selectors = [
            '.draw-date',
            '.date',
            '[data-date]',
            '.result-date',
            'time[datetime]'
        ]
        
        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                date_text = element.get_text(strip=True)
                # Try to parse various date formats
                parsed_date = self._parse_date_text(date_text)
                if parsed_date:
                    return parsed_date, parsed_date
        
        # Regex fallback in page text
        page_text = soup.get_text()
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{1,2} \w+ \d{4})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, page_text)
            if match:
                parsed_date = self._parse_date_text(match.group(1))
                if parsed_date:
                    return parsed_date, parsed_date
        
        # Fallback to current date (should log warning)
        logger.warning(f"Could not extract date from {url}, using current date")
        today = datetime.now().strftime('%Y-%m-%d')
        return today, today
    
    def _parse_date_text(self, date_text: str) -> Optional[str]:
        """Parse various date formats to YYYY-MM-DD."""
        formats = [
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%m/%d/%Y', 
            '%d %B %Y',
            '%d %b %Y',
            '%B %d, %Y'
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_text.strip(), fmt)
                return parsed.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None
    
    def _extract_numbers(self, soup: BeautifulSoup) -> Dict[str, List[int]]:
        """Extract main numbers and star numbers from page."""
        # Multiple selectors for different layouts
        number_selectors = [
            '.ball-number',
            '.number',
            '.main-number',
            '.draw-ball',
            '[class*="ball"]',
            '.result-number'
        ]
        
        star_selectors = [
            '.star-number',
            '.star',
            '.lucky-star',
            '[class*="star"]',
            '.bonus-number'
        ]
        
        # Try structured extraction first
        main_numbers = []
        star_numbers = []
        
        # Extract main numbers
        for selector in number_selectors:
            elements = soup.select(selector)
            if len(elements) >= 5:
                for elem in elements[:5]:
                    try:
                        num = int(elem.get_text(strip=True))
                        if 1 <= num <= 50:
                            main_numbers.append(num)
                    except ValueError:
                        continue
                if len(main_numbers) == 5:
                    break
        
        # Extract star numbers
        for selector in star_selectors:
            elements = soup.select(selector)
            if len(elements) >= 2:
                for elem in elements[:2]:
                    try:
                        num = int(elem.get_text(strip=True))
                        if 1 <= num <= 12:
                            star_numbers.append(num)
                    except ValueError:
                        continue
                if len(star_numbers) == 2:
                    break
        
        # Regex fallback
        if len(main_numbers) < 5 or len(star_numbers) < 2:
            logger.warning("Falling back to regex extraction")
            main_numbers, star_numbers = self._extract_numbers_regex(soup)
        
        # Sort numbers as required
        main_numbers.sort()
        star_numbers.sort()
        
        return {
            "main": main_numbers,
            "stars": star_numbers
        }
    
    def _extract_numbers_regex(self, soup: BeautifulSoup) -> tuple[List[int], List[int]]:
        """Regex fallback for number extraction."""
        text = soup.get_text()
        
        # Common patterns for number sequences
        patterns = [
            r'(\d{1,2})\s*[-,\s]\s*(\d{1,2})\s*[-,\s]\s*(\d{1,2})\s*[-,\s]\s*(\d{1,2})\s*[-,\s]\s*(\d{1,2})\s*.*?(\d{1,2})\s*[-,\s]\s*(\d{1,2})',
            r'Numbers?\s*:?\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*.*?Stars?\s*:?\s*(\d+)\s*,\s*(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    numbers = [int(x) for x in match.groups()]
                    main = numbers[:5]
                    stars = numbers[5:7]
                    
                    # Validate ranges
                    if (all(1 <= n <= 50 for n in main) and 
                        all(1 <= s <= 12 for s in stars)):
                        return main, stars
                except (ValueError, IndexError):
                    continue
        
        # Last resort: find all numbers in valid ranges
        all_numbers = re.findall(r'\b\d{1,2}\b', text)
        main_candidates = [int(n) for n in all_numbers if 1 <= int(n) <= 50]
        star_candidates = [int(n) for n in all_numbers if 1 <= int(n) <= 12]
        
        if len(main_candidates) >= 5 and len(star_candidates) >= 2:
            return main_candidates[:5], star_candidates[:2]
        
        raise ValueError("Could not extract valid numbers from page")
    
    def _extract_jackpot(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract jackpot amount from page."""
        jackpot_selectors = [
            '.jackpot',
            '.jackpot-amount',
            '.prize-amount',
            '[class*="jackpot"]',
            '.main-prize'
        ]
        
        for selector in jackpot_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                amount = self._parse_currency_amount(text)
                if amount:
                    return amount
        
        # Regex fallback
        text = soup.get_text()
        patterns = [
            r'Jackpot[:\s]*[€£$]?([\d,]+(?:\.\d{2})?)\s*(?:million|M)?',
            r'[€£$]([\d,]+(?:\.\d{2})?)\s*(?:million|M)?.*?jackpot',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = self._parse_currency_amount(match.group(1))
                if amount:
                    return amount
        
        return None
    
    def _parse_currency_amount(self, text: str) -> Optional[float]:
        """Parse currency amount from text."""
        # Remove currency symbols and whitespace
        clean_text = re.sub(r'[€£$,\s]', '', text)
        
        try:
            amount = float(clean_text)
            
            # Handle millions
            if 'million' in text.lower() or 'M' in text:
                amount *= 1_000_000
            
            return amount
        except ValueError:
            return None
    
    def _extract_prize_table(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract prize breakdown table."""
        # This is a simplified version - you'd expand based on actual site structure
        prize_table = {}
        
        # Look for prize table elements
        table_selectors = [
            '.prize-table',
            '.breakdown-table', 
            '.results-table',
            'table'
        ]
        
        for selector in table_selectors:
            table = soup.select_one(selector)
            if table:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        try:
                            category = cells[0].get_text(strip=True)
                            winners = int(cells[1].get_text(strip=True).replace(',', ''))
                            prize_text = cells[2].get_text(strip=True)
                            prize_amount = self._parse_currency_amount(prize_text)
                            
                            prize_table[category] = {
                                "winners": winners,
                                "prize": prize_amount
                            }
                        except (ValueError, IndexError):
                            continue
                
                if prize_table:
                    break
        
        return prize_table
    
    def _validate_draw_data(self, numbers: Dict[str, List[int]], draw_id: str) -> None:
        """Validate extracted draw data."""
        main_numbers = numbers["main"]
        star_numbers = numbers["stars"]
        
        # Check counts
        if len(main_numbers) != 5:
            raise ValueError(f"Expected 5 main numbers, got {len(main_numbers)} for {draw_id}")
        
        if len(star_numbers) != 2:
            raise ValueError(f"Expected 2 star numbers, got {len(star_numbers)} for {draw_id}")
        
        # Check ranges
        if not all(1 <= n <= 50 for n in main_numbers):
            raise ValueError(f"Main numbers out of range (1-50): {main_numbers} for {draw_id}")
        
        if not all(1 <= s <= 12 for s in star_numbers):
            raise ValueError(f"Star numbers out of range (1-12): {star_numbers} for {draw_id}")
        
        # Check if sorted
        if main_numbers != sorted(main_numbers):
            raise ValueError(f"Main numbers not sorted: {main_numbers} for {draw_id}")
        
        if star_numbers != sorted(star_numbers):
            raise ValueError(f"Star numbers not sorted: {star_numbers} for {draw_id}")
    
    def scrape_uk_national_lottery(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Scrape EuroMillions draws specifically from UK National Lottery.
        
        Args:
            limit: Maximum number of draws to scrape
            offset: Number of draws to skip (for pagination)
            
        Returns:
            List[Dict]: Parsed draw data from UK National Lottery
        """
        logger.info(f"Scraping UK National Lottery: limit={limit}, offset={offset}")
        
        try:
            # Use the draw history page
            url = self.uk_urls["draw_history"]
            soup = self._fetch_page(url)
            
            # Parse the UK National Lottery specific format
            draws = self._parse_uk_draw_history(soup, limit, offset)
            
            logger.info(f"Successfully scraped {len(draws)} draws from UK National Lottery")
            return draws
            
        except Exception as e:
            logger.error(f"Failed to scrape UK National Lottery: {e}")
            
            # Fallback to generic scraping
            logger.info("Falling back to generic scraping...")
            return self.scrape_latest(limit)
    
    def _parse_uk_draw_history(self, soup: BeautifulSoup, limit: int, offset: int) -> List[Dict[str, Any]]:
        """
        Parse UK National Lottery draw history page format.
        
        Args:
            soup: Parsed HTML from UK lottery page
            limit: Maximum draws to return
            offset: Number of draws to skip
            
        Returns:
            List[Dict]: Parsed draw data
        """
        draws = []
        
        # UK National Lottery specific selectors
        # The page likely contains draw results in a specific structure
        
        # Look for draw result containers
        draw_selectors = [
            '.result-item',
            '.draw-result',
            '.euromillions-result',
            '[class*="result"]',
            '.lotto-result'
        ]
        
        draw_elements = []
        for selector in draw_selectors:
            elements = soup.select(selector)
            if elements:
                draw_elements = elements
                logger.debug(f"Found {len(elements)} draw elements with selector: {selector}")
                break
        
        if not draw_elements:
            # Try more generic approach - look for number patterns
            logger.info("No specific draw elements found, trying pattern matching...")
            return self._parse_uk_by_patterns(soup, limit, offset)
        
        # Process each draw element
        for i, element in enumerate(draw_elements):
            if i < offset:
                continue
            if len(draws) >= limit:
                break
                
            try:
                draw_data = self._parse_uk_single_draw(element)
                if draw_data:
                    draws.append(draw_data)
                    logger.debug(f"Parsed UK draw: {draw_data['draw_id']}")
            except Exception as e:
                logger.warning(f"Failed to parse UK draw element {i}: {e}")
                continue
        
        return draws
    
    def _parse_uk_single_draw(self, element) -> Optional[Dict[str, Any]]:
        """Parse a single UK draw result element."""
        
        # Extract date
        date_selectors = [
            '.date',
            '.draw-date', 
            '[class*="date"]',
            'time'
        ]
        
        draw_date = None
        for selector in date_selectors:
            date_elem = element.select_one(selector)
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                draw_date = self._parse_date(date_text)
                if draw_date:
                    break
        
        if not draw_date:
            # Try to extract date from the element's text
            element_text = element.get_text()
            draw_date = self._extract_date_from_text(element_text)
        
        # Extract numbers
        # UK lottery typically shows balls as individual elements or in a specific format
        number_selectors = [
            '.ball',
            '.number',
            '.main-ball',
            '.star-ball',
            '[class*="ball"]',
            '[class*="number"]'
        ]
        
        main_numbers = []
        star_numbers = []
        
        # Try to find ball elements
        for selector in number_selectors:
            ball_elements = element.select(selector)
            if ball_elements:
                for ball_elem in ball_elements:
                    try:
                        number = int(ball_elem.get_text(strip=True))
                        
                        # UK structure usually has main balls first, then stars
                        if len(main_numbers) < 5 and 1 <= number <= 50:
                            main_numbers.append(number)
                        elif len(star_numbers) < 2 and 1 <= number <= 12:
                            star_numbers.append(number)
                    except ValueError:
                        continue
        
        # If we didn't get numbers from ball elements, try pattern matching
        if len(main_numbers) < 5 or len(star_numbers) < 2:
            try:
                element_text = element.get_text()
                main_parsed, star_parsed = self._extract_numbers_from_text(element_text)
                
                if len(main_parsed) >= 5:
                    main_numbers = main_parsed[:5]
                if len(star_parsed) >= 2:
                    star_numbers = star_parsed[:2]
                    
            except Exception:
                pass
        
        # Validate we have complete data
        if len(main_numbers) == 5 and len(star_numbers) == 2 and draw_date:
            
            # Sort numbers
            main_numbers.sort()
            star_numbers.sort()
            
            # Generate draw ID
            date_str = draw_date.strftime('%Y-%m-%d')
            draw_id = f"euromillions-{date_str}"
            
            return {
                "draw_id": draw_id,
                "draw_date": draw_date,
                "main_numbers": main_numbers,
                "star_numbers": star_numbers,
                "n1": main_numbers[0],
                "n2": main_numbers[1], 
                "n3": main_numbers[2],
                "n4": main_numbers[3],
                "n5": main_numbers[4],
                "s1": star_numbers[0],
                "s2": star_numbers[1],
                "source": "uk_national_lottery"
            }
        
        return None
    
    def _parse_uk_by_patterns(self, soup: BeautifulSoup, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Parse UK page using regex patterns when structure parsing fails."""
        
        page_text = soup.get_text()
        draws = []
        
        # Look for patterns in the format we saw in testing
        # Main numbers: "13 - 30 - 31 - 32 - 36" or "06 - 09 - 10 - 13 - 37"
        # Dates: "06-09-2025" or similar
        
        # Pattern for main numbers (5 numbers, possibly with separators)
        main_pattern = r'(\d{1,2})\s*[-–]\s*(\d{1,2})\s*[-–]\s*(\d{1,2})\s*[-–]\s*(\d{1,2})\s*[-–]\s*(\d{1,2})'
        
        # Find all potential main number sequences
        main_matches = re.finditer(main_pattern, page_text)
        
        draw_count = 0
        skip_count = 0
        
        for match in main_matches:
            if skip_count < offset:
                skip_count += 1
                continue
            if draw_count >= limit:
                break
                
            try:
                # Extract main numbers
                main_nums = [int(match.group(i)) for i in range(1, 6)]
                
                # Validate main numbers are in range
                if not all(1 <= n <= 50 for n in main_nums):
                    continue
                
                # Look for star numbers nearby (this is more challenging)
                # We'll need to find the next occurrence of 2 numbers in the 1-12 range
                start_pos = match.end()
                context = page_text[start_pos:start_pos + 200]  # Look ahead 200 chars
                
                # Pattern for star numbers (2 numbers)
                star_pattern = r'(\d{1,2})\s*[-–]\s*(\d{1,2})'
                star_match = re.search(star_pattern, context)
                
                if star_match:
                    star_nums = [int(star_match.group(1)), int(star_match.group(2))]
                    
                    # Validate star numbers
                    if all(1 <= s <= 12 for s in star_nums):
                        
                        # Try to find a date nearby
                        date_context = page_text[max(0, match.start() - 100):match.end() + 100]
                        draw_date = self._extract_date_from_text(date_context)
                        
                        if not draw_date:
                            # Use a generic recent date if we can't find one
                            from datetime import datetime, timedelta
                            draw_date = datetime.now() - timedelta(days=draw_count)
                        
                        # Sort numbers
                        main_nums.sort()
                        star_nums.sort()
                        
                        # Create draw data
                        date_str = draw_date.strftime('%Y-%m-%d')
                        draw_id = f"euromillions-{date_str}-{draw_count}"
                        
                        draw_data = {
                            "draw_id": draw_id,
                            "draw_date": draw_date,
                            "main_numbers": main_nums,
                            "star_numbers": star_nums,
                            "n1": main_nums[0],
                            "n2": main_nums[1],
                            "n3": main_nums[2], 
                            "n4": main_nums[3],
                            "n5": main_nums[4],
                            "s1": star_nums[0],
                            "s2": star_nums[1],
                            "source": "uk_national_lottery_pattern"
                        }
                        
                        draws.append(draw_data)
                        draw_count += 1
                        
                        logger.debug(f"Pattern-parsed UK draw: {draw_id}")
            
            except Exception as e:
                logger.warning(f"Failed to pattern-parse draw: {e}")
                continue
        
        logger.info(f"Pattern parsing found {len(draws)} draws")
        return draws
    
    def _extract_date_from_text(self, text: str) -> Optional[datetime]:
        """Extract date from text using various patterns."""
        
        # Common date patterns
        patterns = [
            r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})',  # DD-MM-YYYY or MM-DD-YYYY
            r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})',  # YYYY-MM-DD
            r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})',  # DD Mon YYYY
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s+(\d{4})'  # Mon DD, YYYY
        ]
        
        month_names = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    if 'Jan|Feb|Mar' in pattern:
                        # Handle month name patterns
                        if pattern.endswith(r'(\d{4})'):  # DD Mon YYYY
                            day, month_name, year = match.groups()
                            month = month_names[month_name]
                            return datetime(int(year), month, int(day))
                        else:  # Mon DD, YYYY
                            month_name, day, year = match.groups()
                            month = month_names[month_name]
                            return datetime(int(year), month, int(day))
                    else:
                        # Handle numeric patterns
                        if pattern.startswith(r'(\d{4})'):  # YYYY-MM-DD
                            year, month, day = match.groups()
                            return datetime(int(year), int(month), int(day))
                        else:  # DD-MM-YYYY (assuming UK format)
                            day, month, year = match.groups()
                            return datetime(int(year), int(month), int(day))
                            
                except (ValueError, KeyError):
                    continue
        
        return None
    
    def scrape_latest(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Scrape latest draws by trying multiple sources.
        
        Args:
            limit: Maximum number of draws to scrape
            offset: Number of draws to skip (for pagination)
            
        Returns:
            List[Dict]: Parsed draw data
        """
        logger.info(f"Scraping latest {limit} draws (offset: {offset})...")
        
        # Try UK National Lottery first (most reliable)
        try:
            draws = self.scrape_uk_national_lottery(limit, offset)
            if draws:
                logger.info(f"Successfully got {len(draws)} draws from UK National Lottery")
                return draws
        except Exception as e:
            logger.warning(f"UK National Lottery scraping failed: {e}")
        
        # Fallback to generic URL-based scraping
        logger.info("Falling back to generic URL scraping...")
        
        # Get recent URLs
        urls = self.list_recent_draw_urls(limit + offset)
        logger.info(f"Found {len(urls)} draw URLs")
        
        # Skip offset URLs and process the rest
        urls_to_process = urls[offset:offset + limit]
        
        draws = []
        errors = 0
        
        for url in urls_to_process:
            try:
                draw_data = self.parse_draw(url)
                draws.append(draw_data)
                logger.info(f"Successfully parsed draw {draw_data['draw_id']}")
                
            except Exception as e:
                errors += 1
                logger.error(f"Failed to parse {url}: {e}")
                
                # Stop if too many errors
                if errors > len(urls_to_process) // 2:
                    logger.warning("Too many parse errors, stopping")
                    break
        
        logger.info(f"Scraped {len(draws)} draws with {errors} errors")
        return draws


# Convenience function
def get_scraper() -> EuromillionsScraper:
    """Get a scraper instance."""
    return EuromillionsScraper()
