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

class GlassdoorScraper(BaseScraper):
    @property
    def name(self) -> str:
        return "Glassdoor"

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
        url = f"https://www.glassdoor.co.in/Job/jobs.htm?sc.keyword={quote(search_query)}&locKeyword={quote(target_location)}"

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
                log.debug(f"Navigating to Glassdoor: {url}...")
                await page.goto(url, timeout=35000, wait_until="domcontentloaded")
                await asyncio.sleep(random.uniform(3.0, 4.5))

                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")
                
                cards = (
                    soup.find_all("li", class_="JobsList_jobListItem__23312") or
                    soup.find_all("div", attrs={"data-test": "job-listing-single"}) or
                    soup.find_all("li", attrs={"data-test": "jobListing"})
                )
                
                log.info(f"Discovered {len(cards)} raw cards on Glassdoor.")

                for card in cards[:limit]:
                    try:
                        title_tag = card.find("a", attrs={"data-test": "job-title"}) or card.find("a", class_="JobCard_jobTitle___y9P")
                        if not title_tag:
                            continue

                        title = title_tag.get_text(strip=True)
                        href = title_tag.get("href", "")
                        job_url = f"https://www.glassdoor.co.in{href}" if href.startswith("/") else href

                        raw_id = card.get("data-id", f"gd-{random.randint(100000, 999999)}")
                        comp_tag = card.find("span", class_="EmployerProfile_compactEmployerName__LE242") or card.find("div", class_="EmployerProfile_employerName__93_S5")
                        company_name = comp_tag.get_text(strip=True) if comp_tag else "Confidential"

                        loc_tag = card.find("div", attrs={"data-test": "emp-location"}) or card.find("span", class_="JobCard_location__21_xW")
                        loc_text = loc_tag.get_text(strip=True) if loc_tag else target_location

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
                                description_raw=f"{title} position at {company_name}.",
                                description_clean=f"{title} position at {company_name}."
                            )
                        )
                    except Exception as card_err:
                        log.warning(f"Skipping corrupt structural card: {card_err}")

            except Exception as e:
                log.error(f"Glassdoor scraper encountered execution error: {e}")
            finally:
                await context.close()
                await browser.close()

        return jobs