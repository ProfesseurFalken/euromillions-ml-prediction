#!/usr/bin/env python3
"""
Test script to check the UK National Lottery EuroMillions page.
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def test_uk_national_lottery():
    """Test the UK National Lottery EuroMillions draw history page."""
    
    url = "https://www.national-lottery.co.uk/results/euromillions/draw-history"
    
    print(f"🔍 Testing: {url}")
    print("=" * 60)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-GB,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        # Fetch the page
        print("📡 Fetching page...")
        response = requests.get(url, headers=headers, timeout=15)
        
        print(f"✅ Status: {response.status_code}")
        print(f"📏 Content length: {len(response.content):,} bytes")
        print(f"🌐 Final URL: {response.url}")
        
        if response.status_code != 200:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get title
        title = soup.title.string if soup.title else "No title"
        print(f"📄 Title: {title}")
        
        # Look for EuroMillions draw data patterns
        print(f"\n🔍 Analyzing page structure...")
        
        # Look for draw results containers
        draw_containers = soup.find_all(['div', 'article', 'section'], 
                                       class_=re.compile(r'(draw|result|euromillion)', re.I))
        print(f"📊 Found {len(draw_containers)} potential draw containers")
        
        # Look for number patterns (Euromillions format: 5 main + 2 stars)
        text = response.text
        
        # Pattern for Euromillions numbers (e.g., "05 12 23 34 45" and "03 07")
        main_number_pattern = r'\b(?:\d{1,2}[\s\-]+){4}\d{1,2}\b'
        star_number_pattern = r'\b\d{1,2}[\s\-]+\d{1,2}\b'
        
        main_matches = re.findall(main_number_pattern, text)
        star_matches = re.findall(star_number_pattern, text)
        
        print(f"🎱 Found {len(main_matches)} potential main number sequences")
        print(f"⭐ Found {len(star_matches)} potential star number sequences")
        
        # Look for dates
        date_pattern = r'\b(?:\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4}|\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2})\b'
        date_matches = re.findall(date_pattern, text)
        print(f"📅 Found {len(date_matches)} potential dates")
        
        # Look for specific class names or IDs that might contain draw data
        interesting_elements = soup.find_all(attrs={'class': re.compile(r'(ball|number|draw|result)', re.I)})
        print(f"🎯 Found {len(interesting_elements)} elements with ball/number/draw/result classes")
        
        # Look for tables
        tables = soup.find_all('table')
        print(f"📋 Found {len(tables)} tables")
        
        # Show first few potential draws if found
        if main_matches[:3]:
            print(f"\n🎲 Sample potential main number sequences:")
            for i, match in enumerate(main_matches[:3], 1):
                print(f"   {i}. {match.strip()}")
        
        if date_matches[:5]:
            print(f"\n📆 Sample potential dates:")
            for i, match in enumerate(date_matches[:5], 1):
                print(f"   {i}. {match}")
        
        # Show page structure
        print(f"\n🏗️  Page structure overview:")
        if soup.body:
            main_divs = soup.body.find_all('div', recursive=False)
            print(f"   Main divs: {len(main_divs)}")
            
            for div in main_divs[:5]:  # Show first 5
                classes = div.get('class', [])
                id_attr = div.get('id', '')
                print(f"   - div class='{' '.join(classes)}' id='{id_attr}'")
        
        # Check if this looks like a results page
        indicators = [
            'euromillion' in text.lower(),
            'draw' in text.lower(),
            'result' in text.lower(),
            len(main_matches) > 0,
            len(date_matches) > 0
        ]
        
        success_score = sum(indicators)
        print(f"\n📊 Page analysis score: {success_score}/5")
        
        if success_score >= 3:
            print("✅ This looks like a valid EuroMillions results page!")
            return True
        else:
            print("⚠️  This may not be a typical EuroMillions results page")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_uk_national_lottery()
