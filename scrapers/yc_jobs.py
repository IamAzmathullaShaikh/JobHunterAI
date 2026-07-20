import asyncio
import random
from urllib.parse import quote
from typing import List, Optional
from bs4 import BeautifulSoup
from loguru import logger
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

from scrapers.base import BaseScraper
from schemas.job_listing import JobListingCreate

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

class YCJobsScraper(BaseScraper):
    @property
    def name(self) -> str:
        return "YC Jobs"

    async def scrape(
        self, 
        search_query: str, 
        location: Optional[str] = None, 
        limit: int = 10, 
        job_type: str = "Full-Time"
    ) -> List[JobListingCreate]:
        log = logger.bind(scraper=self.name)
        target_location = location or "Remote"
        log.info(f"Spawning stealth instance for Query: '{search_query}' inside '{target_location}' [{job_type}]")
        
        jobs: List[JobListingCreate] = []
        url = f"https://www.ycombinator.com/jobs?query={quote(search_query)}"

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )
            
            context = await browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                locale="en-US",
                timezone_id="Asia/Kolkata"
            )
            
            await Stealth().apply_stealth_async(context)
            page = await context.new_page()
            
            try:
                log.debug(f"Navigating to YC Jobs: {url}...")
                await page.goto(url, timeout=35000, wait_until="domcontentloaded")
                await asyncio.sleep(random.uniform(2.5, 4.0))

                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")
                
                cards = soup.find_all("li", class_="mb-4") or soup.find_all("div", class_="job-row") or soup.find_all("tr")
                log.info(f"Discovered {len(cards)} raw cards on YC Jobs.")

                for card in cards[:limit]:
                    try:
                        title_tag = card.find("a", class_="font-bold") or card.find("a", class_="job-name") or card.find("a")
                        if not title_tag:
                            continue

                        title = title_tag.get_text(strip=True)
                        href = title_tag.get("href", "")
                        job_url = f"https://www.ycombinator.com{href}" if href.startswith("/") else href or url

                        raw_id = f"yc-{random.randint(100000, 999999)}"
                        comp_tag = card.find("span", class_="startup-name") or card.find("div", class_="company-name")
                        company_name = comp_tag.get_text(strip=True) if comp_tag else "Y Combinator Startup"

                        loc_tag = card.find("span", class_="job-location") or card.find("div", class_="location")
                        loc_text = loc_tag.get_text(strip=True) if loc_tag else target_location

                        desc_text = f"Y Combinator backed role: {title} at {company_name}."

                        jobs.append(
                            JobListingCreate(
                                job_id_raw=str(raw_id),
                                title=title,
                                company_name=company_name,
                                location=loc_text,
                                work_place_type="Remote" if "remote" in loc_text.lower() else "Onsite",
                                job_type=job_type,
                                source=self.name,
                                url=job_url,
                                description_raw=desc_text,
                                description_clean=desc_text[:300]
                            )
                        )
                    except Exception as card_err:
                        log.warning(f"Skipping corrupt structural card: {card_err}")

            except Exception as e:
                log.error(f"YC Jobs scraper encountered execution error: {e}")
            finally:
                await context.close()
                await browser.close()

        return jobs