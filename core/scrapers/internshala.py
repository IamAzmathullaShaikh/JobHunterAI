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

class InternshalaScraper(BaseScraper):
    @property
    def name(self) -> str:
        return "Internshala"

    async def scrape(
        self, 
        search_query: str, 
        location: Optional[str] = None, 
        limit: int = 10, 
        job_type: str = "Internship"
    ) -> List[JobListingCreate]:
        log = logger.bind(scraper=self.name)
        target_location = location or "India"
        log.info(f"Spawning stealth instance for Query: '{search_query}' inside '{target_location}' [{job_type}]")
        
        jobs: List[JobListingCreate] = []
        slug = search_query.lower().strip().replace(" ", "-")
        url = f"https://internshala.com/internships/keywords-{quote(slug)}/"

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
                log.debug(f"Navigating to Internshala: {url}...")
                await page.goto(url, timeout=35000, wait_until="domcontentloaded")
                await asyncio.sleep(random.uniform(2.0, 3.5))

                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")
                
                cards = soup.find_all("div", class_="individual_internship") or soup.find_all("div", class_="container-fluid")
                log.info(f"Discovered {len(cards)} raw cards on Internshala.")

                for card in cards[:limit]:
                    try:
                        title_tag = card.find("h3", class_="job-internship-name") or card.find("a", class_="view_detail_id")
                        if not title_tag:
                            continue

                        title = title_tag.get_text(strip=True)
                        anchor = card.find("a", class_="view_detail_id") or card.find("a", href=True)
                        href = anchor["href"] if anchor and anchor.has_attr("href") else ""
                        job_url = f"https://internshala.com{href}" if href.startswith("/") else href or url

                        raw_id = card.get("data-href") or card.get("id") or f"ishala-{random.randint(100000, 999999)}"
                        
                        comp_tag = card.find("p", class_="company-name") or card.find("div", class_="company_name")
                        company_name = comp_tag.get_text(strip=True) if comp_tag else "Listed Startup"

                        loc_tag = card.find("a", class_="location_link") or card.find("span", class_="location") or card.find("div", id="location_names")
                        loc_text = loc_tag.get_text(strip=True) if loc_tag else target_location

                        desc_text = f"Internshala opportunity: {title} at {company_name} ({loc_text})."

                        jobs.append(
                            JobListingCreate(
                                job_id_raw=str(raw_id),
                                title=title,
                                company_name=company_name,
                                location=loc_text,
                                work_place_type="Remote" if "remote" in loc_text.lower() or "work from home" in loc_text.lower() else "Onsite",
                                job_type="Internship",
                                source=self.name,
                                url=job_url,
                                description_raw=desc_text,
                                description_clean=desc_text[:300]
                            )
                        )
                    except Exception as card_err:
                        log.warning(f"Skipping corrupt structural card: {card_err}")

            except Exception as e:
                log.error(f"Internshala scraper encountered execution error: {e}")
            finally:
                await context.close()
                await browser.close()

        return jobs
