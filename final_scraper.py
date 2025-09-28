import asyncio
import aiohttp
import json
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Optional, Dict
import csv
import re
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class CarListing:
    id: str
    title: str
    price: str
    location: str
    url: str
    brand: str
    model: str
    year: str
    mileage: str
    engine_volume: str
    transmission: str
    body_type: str
    color: str
    fuel_type: str
    phone: str
    seller_name: str
    seller_rating: str
    post_date: str

class FinalRahatsatScraper:
    def __init__(self):
        self.base_url = "https://rahatsat.az/systems/ajax/ads.php"
        self.site_url = "https://rahatsat.az"

    def get_listing_headers(self, referer=None):
        """Headers for listing page requests"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7,az;q=0.6',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        if referer:
            headers['Referer'] = referer
        return headers

    def get_ajax_headers(self, referer=None):
        """Headers for AJAX requests with proper authentication"""
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7,az;q=0.6',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'cookie': '_ym_uid=1755794772512445640; _ym_d=1755794772; _ga=GA1.1.1631696722.1755794772; PHPSESSID=e29231daae6fd483bbde04d60d5a0220; metrics_visit=384352; _ym_visorc=w; _ym_isad=1; _ga_HYZ4QJRTM8=GS2.1.s1759079238$o4$g1$t1759083659$j60$l0$h0',
            'dnt': '1',
            'origin': 'https://rahatsat.az',
            'priority': 'u=1, i',
            'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'x-csrf-token': '64e93d7d0fac877ed1d3905294a70b8c8e0b98f78fd129efdc6ce6a0cd966058',
            'x-requested-with': 'XMLHttpRequest'
        }
        if referer:
            headers['referer'] = referer
        return headers

    async def get_basic_listings(self, session: aiohttp.ClientSession, category_id: int, max_pages: int = 5) -> List[Dict]:
        """Get basic listing information from category pages"""
        basic_listings = []

        for page in range(1, max_pages + 1):
            payload = f'id_c={category_id}&page={page}&action=load_catalog_ads'
            headers = self.get_ajax_headers()
            headers['content-length'] = str(len(payload))

            try:
                async with session.post(self.base_url, data=payload, headers=headers) as response:
                    if response.status == 200:
                        text = await response.text()
                        try:
                            result = json.loads(text)
                            if result.get('found'):
                                content = result.get('content', '')
                                if content.strip():
                                    listings = self.parse_basic_listings(content)
                                    basic_listings.extend(listings)
                                    logger.info(f"Page {page}: Found {len(listings)} basic listings")
                                else:
                                    logger.info(f"Page {page}: Empty content, stopping")
                                    break
                        except json.JSONDecodeError:
                            logger.error(f"Page {page}: Failed to parse JSON")
                    else:
                        logger.error(f"Page {page}: HTTP {response.status}")
            except Exception as e:
                logger.error(f"Error fetching page {page}: {e}")

            # Add delay between page requests
            if page < max_pages:
                await asyncio.sleep(2)

        return basic_listings

    def parse_basic_listings(self, html_content: str) -> List[Dict]:
        """Parse basic listing information from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        listings = []

        items = soup.find_all('div', class_='item-grid')
        for item in items:
            try:
                title_link = item.find('a', href=True)
                if not title_link:
                    continue

                title = title_link.get('title', '').strip()
                url = title_link.get('href', '')
                listing_id = url.split('-')[-1] if '-' in url else ''

                price_elem = item.find('span', class_='item-grid-price-now')
                price = price_elem.get_text(strip=True) if price_elem else 'N/A'

                location_elem = item.find('span', class_='item-grid-city')
                location = location_elem.get_text(strip=True) if location_elem else 'N/A'

                listings.append({
                    'id': listing_id,
                    'title': title,
                    'price': price,
                    'location': location,
                    'url': url
                })

            except Exception as e:
                logger.error(f"Error parsing basic listing: {e}")
                continue

        return listings

    async def get_phone_number(self, session: aiohttp.ClientSession, listing_id: str, listing_url: str) -> str:
        """Get phone number via AJAX call using proper authentication"""
        try:
            payload = f'id_ad={listing_id}&action=show_phone'
            headers = self.get_ajax_headers(referer=listing_url)
            headers['content-length'] = str(len(payload))

            async with session.post(self.base_url, data=payload, headers=headers) as response:
                if response.status == 200:
                    text = await response.text()
                    try:
                        result = json.loads(text)
                        if result.get('auth') == 1:
                            html = result.get('html', '')
                            # Extract phone from href="tel:+994517221737"
                            phone_match = re.search(r'tel:([^"]+)', html)
                            if phone_match:
                                phone = phone_match.group(1)
                                logger.debug(f"Found phone for {listing_id}: {phone}")
                                return phone
                        else:
                            logger.debug(f"Phone request failed for {listing_id}: auth={result.get('auth')}")
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error for phone {listing_id}: {e}")
                else:
                    logger.error(f"Phone request HTTP {response.status} for {listing_id}")
        except Exception as e:
            logger.error(f"Error getting phone for {listing_id}: {e}")

        # Add delay after phone request
        await asyncio.sleep(1.5)
        return ""

    async def get_detailed_listing(self, session: aiohttp.ClientSession, basic_listing: Dict) -> CarListing:
        """Get detailed information from individual listing page"""
        listing_url = basic_listing['url']
        listing_id = basic_listing['id']

        try:
            headers = self.get_listing_headers()

            async with session.get(listing_url, headers=headers) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch {listing_url}: HTTP {response.status}")
                    return self.create_basic_listing(basic_listing)

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                # Add delay before phone extraction
                await asyncio.sleep(1)

                # Get phone number via AJAX
                phone = await self.get_phone_number(session, listing_id, listing_url)

                # Parse detailed information
                detailed_info = self.parse_detailed_info(soup, basic_listing, phone)
                return detailed_info

        except Exception as e:
            logger.error(f"Error getting details for {listing_url}: {e}")
            return self.create_basic_listing(basic_listing)

    def parse_detailed_info(self, soup: BeautifulSoup, basic_listing: Dict, phone: str) -> CarListing:
        """Parse detailed information from listing page"""

        # Car specifications
        specs = {}
        properties = soup.find_all('div', class_='list-properties-item')
        for prop in properties:
            label_elem = prop.find('span', class_='list-properties-span1')
            value_elem = prop.find('span', class_='list-properties-span2')

            if label_elem and value_elem:
                label = label_elem.get_text(strip=True)
                value = value_elem.get_text(strip=True)
                specs[label] = value

        # Seller information
        seller_name = ""
        seller_link = soup.find('a', class_='ad-view-card-user-link-profile')
        if not seller_link:
            seller_link = soup.find('a', href=lambda x: x and '/user/' in x)
        if seller_link:
            seller_name = seller_link.get_text(strip=True)

        # Rating
        rating = "0"
        rating_elem = soup.find('a', href=lambda x: x and '/reviews' in x)
        if rating_elem:
            rating_text = rating_elem.get_text(strip=True)
            rating_match = re.search(r'\((\d+)\)', rating_text)
            if rating_match:
                rating = rating_match.group(1)

        # Post date
        post_date = ""
        date_elem = soup.find('span', class_='ad-view-title-info-label')
        if date_elem:
            post_date = date_elem.get_text(strip=True)

        return CarListing(
            id=basic_listing['id'],
            title=basic_listing['title'],
            price=basic_listing['price'],
            location=basic_listing['location'],
            url=basic_listing['url'],
            brand=specs.get('Marka', ''),
            model=specs.get('Model', ''),
            year=specs.get('Buraxılış ili', ''),
            mileage=specs.get('Yürüş, km', ''),
            engine_volume=specs.get('Mühərrik, sm³', ''),
            transmission=specs.get('Sürətlər qutusu', ''),
            body_type=specs.get('Kuzov növü', ''),
            color=specs.get('Rəng', ''),
            fuel_type=specs.get('Yanacaq növü', ''),
            phone=phone,
            seller_name=seller_name,
            seller_rating=rating,
            post_date=post_date
        )

    def create_basic_listing(self, basic_listing: Dict) -> CarListing:
        """Create a CarListing with only basic info when detailed parsing fails"""
        return CarListing(
            id=basic_listing['id'],
            title=basic_listing['title'],
            price=basic_listing['price'],
            location=basic_listing['location'],
            url=basic_listing['url'],
            brand="",
            model="",
            year="",
            mileage="",
            engine_volume="",
            transmission="",
            body_type="",
            color="",
            fuel_type="",
            phone="",
            seller_name="",
            seller_rating="",
            post_date=""
        )

    async def scrape_all_data(self, category_id: int, max_pages: int = 10, max_details: int = 100, batch_size: int = 5) -> List[CarListing]:
        """Main method to scrape all available data"""
        timeout = aiohttp.ClientTimeout(total=180, connect=30)

        async with aiohttp.ClientSession(
            timeout=timeout,
            cookie_jar=aiohttp.CookieJar()
        ) as session:

            logger.info(f"Getting basic listings from {max_pages} pages...")
            basic_listings = await self.get_basic_listings(session, category_id, max_pages)

            logger.info(f"Found {len(basic_listings)} basic listings")

            # Limit the number of detailed scrapes
            basic_listings = basic_listings[:max_details]
            logger.info(f"Getting detailed info for {len(basic_listings)} listings...")

            detailed_listings = []

            # Process in batches
            for i in range(0, len(basic_listings), batch_size):
                batch = basic_listings[i:i + batch_size]
                batch_num = i // batch_size + 1
                total_batches = (len(basic_listings) + batch_size - 1) // batch_size

                logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} listings)")

                # Process batch concurrently
                tasks = []
                for basic_listing in batch:
                    task = self.get_detailed_listing(session, basic_listing)
                    tasks.append(task)

                batch_results = await asyncio.gather(*tasks, return_exceptions=True)

                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        logger.error(f"Error processing listing {batch[j]['id']}: {result}")
                        result = self.create_basic_listing(batch[j])

                    detailed_listings.append(result)

                # Delay between batches
                if i + batch_size < len(basic_listings):
                    await asyncio.sleep(2)

            return detailed_listings

    def save_to_csv(self, listings: List[CarListing], filename: str = 'rahatsat_cars.csv'):
        """Save listings to CSV"""
        fieldnames = [
            'id', 'title', 'price', 'location', 'url',
            'brand', 'model', 'year', 'mileage', 'engine_volume', 'transmission',
            'body_type', 'color', 'fuel_type', 'phone', 'seller_name',
            'seller_rating', 'post_date'
        ]

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for listing in listings:
                writer.writerow({
                    'id': listing.id,
                    'title': listing.title,
                    'price': listing.price,
                    'location': listing.location,
                    'url': listing.url,
                    'brand': listing.brand,
                    'model': listing.model,
                    'year': listing.year,
                    'mileage': listing.mileage,
                    'engine_volume': listing.engine_volume,
                    'transmission': listing.transmission,
                    'body_type': listing.body_type,
                    'color': listing.color,
                    'fuel_type': listing.fuel_type,
                    'phone': listing.phone,
                    'seller_name': listing.seller_name,
                    'seller_rating': listing.seller_rating,
                    'post_date': listing.post_date
                })

    def save_to_excel(self, listings: List[CarListing], filename: str = 'rahatsat_cars.xlsx'):
        """Save listings to Excel with analysis"""
        # Main data
        main_data = []
        for listing in listings:
            main_data.append({
                'ID': listing.id,
                'Title': listing.title,
                'Price': listing.price,
                'Location': listing.location,
                'URL': listing.url,
                'Brand': listing.brand,
                'Model': listing.model,
                'Year': listing.year,
                'Mileage': listing.mileage,
                'Engine Volume': listing.engine_volume,
                'Transmission': listing.transmission,
                'Body Type': listing.body_type,
                'Color': listing.color,
                'Fuel Type': listing.fuel_type,
                'Phone': listing.phone,
                'Seller Name': listing.seller_name,
                'Seller Rating': listing.seller_rating,
                'Post Date': listing.post_date
            })

        # Create Excel file with analysis
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Main sheet
            df_main = pd.DataFrame(main_data)
            df_main.to_excel(writer, sheet_name='All Cars', index=False)

            # Brand summary
            if main_data:
                brand_counts = df_main['Brand'].value_counts().reset_index()
                brand_counts.columns = ['Brand', 'Count']
                brand_counts.to_excel(writer, sheet_name='Brand Summary', index=False)

                # Location summary
                location_counts = df_main['Location'].value_counts().head(20).reset_index()
                location_counts.columns = ['Location', 'Count']
                location_counts.to_excel(writer, sheet_name='Top Locations', index=False)

async def main():
    scraper = FinalRahatsatScraper()

    # Configuration
    category_id = 553  # Cars category
    max_pages = 50      # Pages to scrape for basic listings
    max_details = 50   # Maximum number of detailed listings to scrape
    batch_size = 5     # Process listings in batches

    print("🚗 Rahatsat.az Car Scraper")
    print("=" * 50)
    print(f"Category: Cars ({category_id})")
    print(f"Max pages: {max_pages}")
    print(f"Max detailed listings: {max_details}")
    print(f"Batch size: {batch_size}")
    print()
    print("📞 Note: Using provided session credentials to fetch phone numbers")
    print("=" * 50)

    try:
        detailed_listings = await scraper.scrape_all_data(
            category_id, max_pages, max_details, batch_size
        )

        logger.info(f"Total listings scraped: {len(detailed_listings)}")

        if detailed_listings:
            # Save to files
            scraper.save_to_csv(detailed_listings)
            scraper.save_to_excel(detailed_listings)
            print(f"\n✅ Data saved to:")
            print(f"   📄 rahatsat_cars.csv")
            print(f"   📊 rahatsat_cars.xlsx")

            # Statistics
            brands = [l.brand for l in detailed_listings if l.brand]
            phones = [l.phone for l in detailed_listings if l.phone]
            complete_specs = [l for l in detailed_listings if l.brand and l.year and l.mileage]

            print(f"\n📊 Statistics:")
            print(f"   Total listings: {len(detailed_listings)}")
            print(f"   With brand info: {len(brands)}")
            print(f"   With phone numbers: {len(phones)}")
            print(f"   Complete specs: {len(complete_specs)}")

            # Top brands
            if brands:
                from collections import Counter
                top_brands = Counter(brands).most_common(5)
                print(f"\n🏆 Top brands:")
                for brand, count in top_brands:
                    print(f"   {brand}: {count} cars")

            # Sample output
            print(f"\n📋 Sample listings:")
            for i, listing in enumerate(detailed_listings[:5]):
                print(f"   {i+1}. {listing.title}")
                print(f"      🏷️  {listing.brand} {listing.model} ({listing.year})")
                print(f"      💰 {listing.price}")
                print(f"      📞 {listing.phone or 'No phone'}")
                print(f"      📍 {listing.location}")
                print()

        else:
            logger.warning("No listings found")

    except Exception as e:
        logger.error(f"Error during scraping: {e}")

if __name__ == "__main__":
    asyncio.run(main())