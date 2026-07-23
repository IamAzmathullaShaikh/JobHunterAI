import asyncio
import random
from urllib.parse import quote
from typing import List, Optional
from bs4 import BeautifulSoup
from loguru import logger
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

from core.scrapers.base import BaseScraper
from core.schemas.job_listing import JobListingCreate

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

class FounditScraper(BaseScraper):
    @property
    def name(self) -> str:
        return "Foundit"

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
        url = f"https://www.foundit.in/srp/results?query={quote(search_query)}&locations={quote(target_location)}"

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
                log.debug(f"Navigating to {url}...")
                await page.goto(url, timeout=35000, wait_until="domcontentloaded")
                await asyncio.sleep(random.uniform(2.5, 4.0))

                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")
                
                cards = (
                    soup.find_all("div", class_="srpResultCardContainer") or 
                    soup.find_all("div", class_="card-template") or
                    soup.find_all("div", class_="srpResultCard")
                )
                
                log.info(f"Discovered {len(cards)} raw cards on Foundit.")

                for card in cards[:limit]:
                    try:
                        title_tag = card.find("div", class_="card-headline") or card.find("a", class_="jobTitle") or card.find("h3")
                        if not title_tag:
                            continue

                        title = title_tag.get_text(strip=True)
                        anchor = card.find("a")
                        job_url = anchor["href"] if anchor and anchor.has_attr("href") else url
                        if job_url.startswith("//"):
                            job_url = "https:" + job_url
                        elif job_url.startswith("/"):
                            job_url = "https://www.foundit.in" + job_url

                        raw_id = card.get("id", f"foundit-{random.randint(100000, 999999)}")
                        comp_tag = card.find("div", class_="company-name") or card.find("span", class_="company-name")
                        company_name = comp_tag.get_text(strip=True) if comp_tag else "Confidential"

                        loc_tag = card.find("div", class_="location") or card.find("span", class_="loc")
                        loc_text = loc_tag.get_text(strip=True) if loc_tag else target_location

                        desc_tag = card.find("div", class_="card-description") or card.find("p", class_="job-desc")
                        desc_text = desc_tag.get_text(strip=True) if desc_tag else f"{title} at {company_name}"

                        jobs.append(
                            JobListingCreate(
                                job_id_raw=str(raw_id),
                                title=title,
                                company_name=company_name,
                                location=loc_text,
                                work_place_type="Onsite",
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
                log.error(f"Foundit scraper encountered execution error: {e}")
            finally:
                await context.close()
                await browser.close()

        return jobs
