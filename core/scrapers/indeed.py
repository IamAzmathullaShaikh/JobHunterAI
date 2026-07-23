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
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
]

class IndeedScraper(BaseScraper):
    @property
    def name(self) -> str:
        return "Indeed"

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
        
        # Determine domain (defaulting to Indian regional domain if India is in location string)
        domain = "in.indeed.com" if "india" in target_location.lower() else "www.indeed.com"
        url = f"https://{domain}/jobs?q={quote(search_query)}&l={quote(target_location)}"

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-infobars",
                    f"--window-size={random.randint(1280, 1440)},{random.randint(800, 900)}"
                ]
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
                await page.goto(url, timeout=45000, wait_until="domcontentloaded")
                await asyncio.sleep(random.uniform(2.5, 4.0))

                # Scroll to load dynamically rendered cards
                for _ in range(2):
                    await page.evaluate(f"window.scrollBy(0, {random.randint(300, 600)});")
                    await asyncio.sleep(random.uniform(1.0, 2.0))

                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")
                
                # Target primary container tags for Indeed cards
                cards = (
                    soup.find_all("div", class_="cardOutline") or 
                    soup.find_all("div", class_="job_seen_beacon") or 
                    soup.find_all("td", class_="resultContent")
                )
                
                log.info(f"Discovered {len(cards)} raw job listing cards in view stream.")

                for card in cards[:limit]:
                    try:
                        title_anchor = card.find("a", class_="jxf413") or card.find("a", id=lambda x: x and x.startswith("job_")) or card.find("h2", class_="jobTitle")
                        if not title_anchor:
                            continue

                        title = title_anchor.get_text(strip=True)
                        jk_id = title_anchor.get("data-jk") or card.find_parent("div", class_="job_seen_beacon")
                        
                        # Extract relative link or job key
                        if isinstance(jk_id, str):
                            job_url = f"https://{domain}/viewjob?jk={jk_id}"
                            raw_id = f"ind-{jk_id}"
                        else:
                            href = title_anchor.get("href", "")
                            job_url = f"https://{domain}{href}" if href.startswith("/") else href
                            raw_id = f"ind-raw-{random.randint(100000, 999999)}"

                        company_tag = card.find("span", {"data-testid": "company-name"}) or card.find("span", class_="companyName")
                        company_name = company_tag.get_text(strip=True) if company_tag else "Confidential / Unlisted"

                        loc_tag = card.find("div", {"data-testid": "text-location"}) or card.find("div", class_="companyLocation")
                        loc_text = loc_tag.get_text(strip=True) if loc_tag else target_location

                        snippet_tag = card.find("div", class_="jobMetaDataGroup") or card.find("div", class_="underShelfFooter")
                        snippet_text = snippet_tag.get_text(separator="\n", strip=True) if snippet_tag else f"Role target for {title} at {company_name}."

                        job_dto = JobListingCreate(
                            job_id_raw=raw_id,
                            title=title,
                            company_name=company_name,
                            location=loc_text,
                            work_place_type="Onsite",
                            job_type=job_type,
                            source=self.name,
                            url=job_url,
                            description_raw=snippet_text,
                            description_clean=snippet_text[:300]
                        )
                        jobs.append(job_dto)
                    except Exception as card_err:
                        log.warning(f"Skipping corrupt structural card: {str(card_err)}")

            except Exception as e:
                log.error(f"Indeed stealth scraper encountered an execution error: {str(e)}")
            finally:
                await context.close()
                await browser.close()

        return jobs
