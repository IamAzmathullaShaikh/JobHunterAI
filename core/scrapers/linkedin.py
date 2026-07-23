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

class LinkedInScraper(BaseScraper):
    @property
    def name(self) -> str:
        return "LinkedIn"

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
        
        modified_query = search_query
        jt_param = ""
        if job_type == "Internship":
            modified_query = f"{search_query} Internship"
            jt_param = "&f_JT=I"
        elif job_type == "Apprenticeship":
            modified_query = f"{search_query} Apprenticeship"
            jt_param = "&f_JT=A"

        url = f"https://www.linkedin.com/jobs/search?keywords={quote(modified_query)}&location={quote(target_location)}{jt_param}"

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
                log.debug("Navigating to target search page...")
                await page.goto(url, timeout=45000, wait_until="domcontentloaded")
                await asyncio.sleep(random.uniform(2.0, 3.5))

                for _ in range(2):
                    scroll_distance = random.randint(400, 700)
                    await page.evaluate(f"window.scrollBy(0, {scroll_distance});")
                    await asyncio.sleep(random.uniform(1.0, 2.0))

                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")
                cards = soup.find_all("div", class_="base-card")
                
                log.info(f"Discovered {len(cards)} raw job cards. Fetching detailed descriptions...")

                for card in cards[:limit]:
                    try:
                        title_tag = card.find("h3", class_="base-search-card__title")
                        company_tag = card.find("h4", class_="base-search-card__subtitle")
                        location_tag = card.find("span", class_="job-search-card__location")
                        link_tag = card.find("a", class_="base-card__full-link")
                        
                        if not (title_tag and company_tag and link_tag):
                            continue
                            
                        raw_id = card.get("data-entity-urn", f"li-raw-{random.randint(100000, 999999)}").split(":")[-1]
                        job_url = link_tag["href"].split("?")[0]

                        # --- FAST DETAIL FETCHING via LinkedIn Guest API ---
                        full_description = "Detailed job specs unavailable."
                        try:
                            api_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{raw_id}"
                            response = await context.request.get(api_url, timeout=5000)
                            if response.status == 200:
                                detail_html = await response.text()
                                detail_soup = BeautifulSoup(detail_html, "html.parser")
                                desc_div = (
                                    detail_soup.find("div", class_="show-more-less-html__markup") or 
                                    detail_soup.find("section", class_="description")
                                )
                                if desc_div:
                                    full_description = desc_div.get_text(separator="\n", strip=True)
                        except Exception as desc_err:
                            log.debug(f"Could not extract extended detail for {raw_id}: {desc_err}")

                        job_dto = JobListingCreate(
                            job_id_raw=raw_id,
                            title=title_tag.text.strip(),
                            company_name=company_tag.text.strip(),
                            location=location_tag.text.strip() if location_tag else "Remote / Flexible",
                            work_place_type="Onsite", 
                            job_type=job_type,
                            source=self.name,
                            url=job_url,
                            description_raw=full_description,
                            description_clean=full_description[:500] + "..."
                        )
                        jobs.append(job_dto)
                    except Exception as card_err:
                        log.warning(f"Skipping corrupt structural card: {str(card_err)}")
                        
            except Exception as e:
                log.error(f"Stealth scraper pipeline encountered an error: {str(e)}")
            finally:
                await context.close()
                await browser.close()
                
        return jobs
