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

class GoogleJobsScraper(BaseScraper):
    @property
    def name(self) -> str:
        return "Google Jobs"

    async def scrape(
        self, 
        search_query: str, 
        location: Optional[str] = None, 
        limit: int = 10, 
        job_type: str = "Full-Time"
    ) -> List[JobListingCreate]:
        log = logger.bind(scraper=self.name)
        target_location = location or "India"
        log.info(f"Spawning stealth instance for Query: '{search_query}' inside '{target_location}' [{job_type}]")
        
        jobs: List[JobListingCreate] = []
        url = f"https://www.google.com/search?q={quote(search_query)}+jobs+in+{quote(target_location)}&ibp=htl;jobs"

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
                log.debug(f"Navigating to Google Jobs: {url}...")
                await page.goto(url, timeout=35000, wait_until="domcontentloaded")
                await asyncio.sleep(random.uniform(2.5, 4.0))

                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")
                
                cards = soup.find_all("li", class_="iK21B") or soup.find_all("div", attrs={"data-job-id": True})
                log.info(f"Discovered {len(cards)} raw cards on Google Jobs.")

                for card in cards[:limit]:
                    try:
                        title_tag = card.find("div", class_="BjA83e") or card.find("div", class_="P82fP")
                        if not title_tag:
                            continue

                        title = title_tag.get_text(strip=True)
                        raw_id = card.get("data-job-id", f"gj-{random.randint(100000, 999999)}")

                        comp_tag = card.find("div", class_="vL1T3")
                        company_name = comp_tag.get_text(strip=True) if comp_tag else "Listed on Google Jobs"

                        loc_tag = card.find("div", class_="Qk3f8b")
                        loc_text = loc_tag.get_text(strip=True) if loc_tag else target_location

                        desc_tag = card.find("div", class_="HB423d")
                        desc_text = desc_tag.get_text(strip=True) if desc_tag else f"{title} opportunity in {loc_text}."

                        jobs.append(
                            JobListingCreate(
                                job_id_raw=str(raw_id),
                                title=title,
                                company_name=company_name,
                                location=loc_text,
                                work_place_type="Onsite",
                                job_type=job_type,
                                source=self.name,
                                url=url,
                                description_raw=desc_text,
                                description_clean=desc_text[:300]
                            )
                        )
                    except Exception as card_err:
                        log.warning(f"Skipping corrupt structural card: {card_err}")

            except Exception as e:
                log.error(f"Google Jobs scraper encountered execution error: {e}")
            finally:
                await context.close()
                await browser.close()

        return jobs